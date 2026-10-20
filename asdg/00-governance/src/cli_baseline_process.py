"""Bounded offline-observable process transport for baseline invocations."""
from __future__ import annotations

import json
import os
import re
import selectors
import signal
import subprocess
import time

from cli_baseline_diagnostics import sanitize_text

CAPTURE_LIMIT = 64 * 1024
EVENT_LINE_LIMIT = 64 * 1024
TERMINATION_GRACE = 5.0
READ_SIZE = 16 * 1024


class _Capture:
    def __init__(self):
        self.data = bytearray()
        self.bytes_seen = 0

    def feed(self, data: bytes) -> None:
        self.bytes_seen += len(data)
        remaining = CAPTURE_LIMIT - len(self.data)
        if remaining > 0:
            self.data.extend(data[:remaining])

    def record(self) -> dict:
        data = bytes(self.data)
        truncated = self.bytes_seen > len(data)
        # Never retain a cut-off credential prefix or unfinished JSON record.
        tail = 0
        if truncated and data and not data.endswith(b'\n'):
            end = data.rfind(b'\n') + 1
            tail = len(data) - end
            data = data[:end]
        text = sanitize_text(data.decode('utf-8', errors='replace'),
                             limit=CAPTURE_LIMIT, multiline=True)
        return {'text': text, 'bytes_seen': self.bytes_seen,
                'retained_bytes': len(data), 'capture_limit_bytes': CAPTURE_LIMIT,
                'truncated': truncated, 'omitted_bytes': self.bytes_seen - len(data),
                'incomplete_tail_omitted_bytes': tail,
                'sanitized': text != data.decode('utf-8', errors='replace')}


class _Events:
    """Scan JSONL independently of capture, using only a thread.started ID.

    Lines larger than EVENT_LINE_LIMIT are counted and skipped, even if they
    might contain a session. No other event fields establish validation,
    progress, acceptance or promotion; those require runner observations.
    """
    def __init__(self):
        self.pending = bytearray()
        self.discarding = False
        self.omitted = 0
        self.session = None

    def feed(self, data: bytes) -> None:
        for index, part in enumerate(data.split(b'\n')):
            if index:
                self.finish_line()
            if not self.discarding:
                if len(self.pending) + len(part) > EVENT_LINE_LIMIT:
                    self.pending.clear()
                    self.discarding = True
                    self.omitted += 1
                else:
                    self.pending.extend(part)

    def finish_line(self) -> None:
        if not self.discarding and self.pending:
            try:
                event = json.loads(self.pending)
            except (ValueError, UnicodeDecodeError, RecursionError):
                event = None
            if isinstance(event, dict) and event.get('type') == 'thread.started':
                value = event.get('thread_id')
                if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value):
                    self.session = self.session or value
        self.pending.clear()
        self.discarding = False


def observe_process(process: subprocess.Popen, prompt: str, timeout: float, *,
                    heartbeat=None, interval: float = 15.0,
                    runtime: dict | None = None) -> tuple[str | None, str]:
    """Drain a binary PIPE child, return its session and sanitized bounded stderr.

    Callers must launch with start_new_session=True. Heartbeat receives observed
    elapsed seconds. Timeout and interruption retain their exception type and
    attach `.session`; both stop the process group using TERM, then KILL after
    the existing five-second grace. Runtime records are filled even on failure.
    """
    if interval <= 0:
        raise ValueError('Heartbeat interval must be positive.')
    started = time.monotonic()
    deadline = started + timeout
    next_heartbeat = started + interval
    capture = {'stdout': _Capture(), 'stderr': _Capture()}
    events = _Events()
    selector = selectors.DefaultSelector()
    payload = memoryview(prompt.encode('utf-8'))
    sent = 0
    cleanup = []
    cleanup_errors = []

    def close_pipe(stream) -> None:
        try:
            selector.unregister(stream)
        except KeyError:
            pass
        stream.close()

    def read_ready(wait: float) -> None:
        nonlocal sent
        for key, _ in selector.select(max(0, wait)):
            stream, kind = key.fileobj, key.data
            if kind == 'stdin':
                try:
                    sent += os.write(stream.fileno(), payload[sent:sent + READ_SIZE])
                except (BrokenPipeError, OSError):
                    close_pipe(stream)
                    continue
                if sent == len(payload):
                    close_pipe(stream)
                continue
            try:
                data = os.read(stream.fileno(), READ_SIZE)
            except BlockingIOError:
                continue
            except OSError:
                close_pipe(stream)
                raise
            if not data:
                close_pipe(stream)
                if kind == 'stdout':
                    events.finish_line()
                continue
            capture[kind].feed(data)
            if kind == 'stdout':
                events.feed(data)

    def pending() -> bool:
        return bool(selector.get_map()) or process.poll() is None

    def stop_group() -> None:
        # A descendant may still own a pipe after the parent exits, so signal
        # the process group even when poll() already returned an exit code.
        for sig, grace in ((signal.SIGTERM, TERMINATION_GRACE),
                           (signal.SIGKILL, 1.0)):
            try:
                os.killpg(process.pid, sig)
                cleanup.append(signal.Signals(sig).name)
            except ProcessLookupError:
                pass
            except OSError as exc:
                cleanup_errors.append(sanitize_text(str(exc)))
                # A group can disappear between TERM and KILL (some sandbox
                # hosts report EPERM for that race). Still stop a live parent.
                if process.poll() is None:
                    try:
                        process.send_signal(sig)
                        cleanup.append(signal.Signals(sig).name + '_parent_fallback')
                    except OSError as fallback:
                        cleanup_errors.append(sanitize_text(str(fallback)))
            until = time.monotonic() + grace
            try:
                while pending() and time.monotonic() < until:
                    read_ready(min(0.1, until - time.monotonic()))
            except (Exception, KeyboardInterrupt) as exc:
                # If transport itself breaks, do not let another read failure
                # prevent KILL or replace the original exception.
                cleanup_errors.append(sanitize_text(str(exc)))
                continue
            if not pending():
                break
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            cleanup_errors.append('Child did not exit after termination attempts.')

    try:
        for kind in ('stdout', 'stderr', 'stdin'):
            stream = getattr(process, kind)
            if stream is None:
                raise ValueError('Process stdin/stdout/stderr must use binary PIPEs.')
            os.set_blocking(stream.fileno(), False)
            if kind == 'stdin' and not payload:
                stream.close()
                continue
            selector.register(stream, selectors.EVENT_WRITE if kind == 'stdin'
                              else selectors.EVENT_READ, kind)
        while pending():
            current = time.monotonic()
            if current >= deadline:
                raise subprocess.TimeoutExpired(process.args, timeout)
            if heartbeat is not None and current >= next_heartbeat and process.poll() is None:
                heartbeat(current - started)
                next_heartbeat = current + interval
            heartbeat_wait = (max(0, next_heartbeat - current)
                              if heartbeat is not None and process.poll() is None else 0.1)
            read_ready(min(0.1, deadline - current,
                           heartbeat_wait))
        process.wait()
    except BaseException as exc:
        stop_group()
        if isinstance(exc, (subprocess.TimeoutExpired, KeyboardInterrupt)):
            exc.session = events.session
        raise
    finally:
        for key in list(selector.get_map().values()):
            close_pipe(key.fileobj)
        selector.close()
        if runtime is not None:
            runtime.update({name: value.record() for name, value in capture.items()})
            runtime.update({'exit_code': process.poll(), 'session_id': events.session,
                            'elapsed_seconds': round(time.monotonic() - started, 3),
                            'event_lines_omitted': events.omitted,
                            'event_line_limit_bytes': EVENT_LINE_LIMIT,
                            'termination_signals': cleanup,
                            'cleanup_errors': cleanup_errors})
    return events.session, capture['stderr'].record()['text']
