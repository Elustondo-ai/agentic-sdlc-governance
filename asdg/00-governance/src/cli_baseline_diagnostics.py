"""Bounded, display-safe diagnostic detail; no artifact acceptance policy."""
from __future__ import annotations

import math
import re
import unicodedata

from cli_files import Conflict

# Shared unchanged with artifact/source screening. Display redaction below is
# additional protection only; it never decides whether an artifact is accepted.
SECRET = re.compile(rb'(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|'
                    rb'-----BEGIN [A-Z ]*PRIVATE KEY-----|'
                    rb'(?i:api[_-]?key|password|secret|access[_-]?token)\s*[:=]\s*[\"\']?[A-Za-z0-9_/+=-]{16,})')
ANSI = re.compile(r'\x1b(?:\][^\x07\x1b]*(?:\x07|\x1b\\|$)|\[[0-?]*[ -/]*[@-~]|[@-_])')
URL = re.compile(r'(?i)(?:\b[a-z][a-z0-9+.-]*:)?//[^\s<>\"\x27`]+')
QUERY = re.compile(r'\?[^\s<>\"\x27`]+')
ASSIGNMENT = re.compile(
    r'(?i)(\b(?:[A-Za-z0-9]+_)*(?:password|api[_-]?key|access[_-]?token|secret|authorization|'
    r'client[_-]?secret|refresh[_-]?token|id[_-]?token)\b[\"\x27]?\s*[:=]\s*)'
    r'(?:Bearer\s+)?(?:\"[^\"\n]*\"|\x27[^\x27\n]*\x27|[^\s;,&]+)')
PRIVATE_KEY = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?'
                         r'(?:-----END [A-Z ]*PRIVATE KEY-----|$)', re.S)
SENSITIVE_FIELD = re.compile(r'(?i)(?:[A-Za-z0-9]+_)*(?:password|api[_-]?key|access[_-]?token|'
                             r'secret|authorization|client[_-]?secret|refresh[_-]?token|id[_-]?token|token|credentials?)')


def _safe_url(match: re.Match) -> str:
    value = match.group()
    prefix, address = value.split('//', 1)
    boundary = re.search(r'[/#?]', address)
    end = boundary.start() if boundary else len(address)
    authority, suffix = address[:end], address[end:]
    if '@' in authority:
        authority = '[REDACTED]@' + authority.rsplit('@', 1)[1]
    # Query/fragment values can be credentials even with an innocuous field name.
    suffix = re.sub(r'[?#].*', '?[REDACTED]', suffix)
    return prefix + '//' + authority + suffix


def sanitize_text(value: object, limit: int = 320, multiline: bool = False) -> str:
    """Remove terminal controls and redact credentials before applying a bound."""
    text = value.decode('utf-8', errors='replace') if isinstance(value, bytes) else str(value)
    text = ANSI.sub('', text).replace('\r\n', '\n').replace('\r', '\n')
    text = ''.join(character for character in text
                   if unicodedata.category(character) not in {'Cc', 'Cf', 'Cs'}
                   or character in '\n\t')
    text = URL.sub(_safe_url, text)
    text = QUERY.sub('?[REDACTED]', text)
    text = ASSIGNMENT.sub(lambda match: match.group(1) + '[REDACTED]', text)
    text = PRIVATE_KEY.sub('[REDACTED PRIVATE KEY]', text)
    text = SECRET.sub(b'[REDACTED]', text.encode('utf-8')).decode('utf-8', errors='replace')
    if not multiline:
        text = re.sub(r'\s+', ' ', text).strip()
    return text[:max(0, limit)]


def sanitize_record(value: object) -> object:
    """Copy JSON-like evidence for display; never use this to make decisions.

    Preserve ordinary structure/types, with explicit markers for oversized or
    unsupported material. Always sanitize complete string values before clipping.
    Final agent messages are already limited to 64,000 bytes by the runner.
    """
    remaining = [4096]

    def safe_string(text: str) -> str:
        cleaned = sanitize_text(text, limit=2049)
        return cleaned[:2036] + ' [TRUNCATED]' if len(cleaned) > 2048 else cleaned

    def visit(item: object, depth: int) -> object:
        if remaining[0] <= 0 or depth > 12:
            return '[OMITTED: record limit]'
        remaining[0] -= 1
        if isinstance(item, str):
            return safe_string(item)
        if item is None or isinstance(item, (bool, int)):
            return item
        if isinstance(item, float):
            return item if math.isfinite(item) else '[OMITTED: non-finite number]'
        if isinstance(item, list):
            result = []
            for index, child in enumerate(item):
                if index >= 128 or remaining[0] <= 0:
                    result.append('[OMITTED: record limit]')
                    break
                result.append(visit(child, depth + 1))
            return result
        if isinstance(item, dict):
            result = {}
            for index, (key, child) in enumerate(item.items()):
                if index >= 128 or remaining[0] <= 0:
                    result['[OMITTED: remaining entries]'] = 'record limit'
                    break
                safe_key = safe_string(key) if isinstance(key, str) else '[OMITTED: non-string key]'
                if safe_key in result:
                    safe_key = safe_key[:2000] + f' [duplicate sanitized key {index}]'
                if isinstance(key, str) and isinstance(child, str) and SENSITIVE_FIELD.fullmatch(key):
                    remaining[0] -= 1
                    result[safe_key] = '[REDACTED]'
                else:
                    result[safe_key] = visit(child, depth + 1)
            return result
        return '[OMITTED: unsupported record type]'

    return visit(value, 0)


class ValidationDiagnostic(Conflict):
    """Keep existing exception wording while adding safe structured context."""

    def __init__(self, message: str, *, code: str, rule: str, expected: str,
                 target: str | None = None, artifact: str | None = None,
                 line: int | None = None):
        super().__init__(message)
        self.diagnostic = {
            'code': sanitize_text(code, 80),
            'artifact': sanitize_text(artifact) if artifact is not None else None,
            'line': line,
            'target': sanitize_text(target) if target is not None else None,
            'rule': sanitize_text(rule),
            'expected': sanitize_text(expected),
        }
