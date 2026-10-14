"""Read-only loopback dashboard: HTML and JSON render the same evaluated status."""
from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from cli_model import REPO
from cli_status import project_status, stage_label


def render_dashboard(status: dict) -> str:
    """Presentation only: no permission, stage or recommendation decisions live here."""
    def escaped(value):
        return html.escape(str(value if value is not None else 'Not defined'))

    def items(values):
        return '<ul>' + ''.join('<li>' + escaped(v) + '</li>' for v in values) + '</ul>' if values else '<p class="muted">None recorded</p>'

    permission = escaped(status['implementation_permission'])
    next_action = status['recommendation']
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="30"><title>ASDLC — {escaped(status['project_name'])}</title>
<style>
:root{{color-scheme:light;--ink:#142f3b;--muted:#586c75;--line:#d9e4e7;--teal:#08675a}}
*{{box-sizing:border-box}}body{{margin:0;background:#f2f6f7;color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
main{{max-width:1120px;margin:auto;padding:36px 24px}}header{{display:flex;justify-content:space-between;gap:24px;align-items:start}}
h1{{font-size:20px;letter-spacing:.1em;margin:0}}header p{{margin:5px 0;color:var(--muted)}}
.tag{{border:1px solid var(--line);border-radius:24px;padding:6px 14px;white-space:nowrap;font-size:13px}}
.hero{{background:var(--ink);color:white;padding:30px;border-radius:18px;margin:24px 0}}
.eyebrow{{font-size:12px;font-weight:700;letter-spacing:.12em;margin:0 0 12px;text-transform:uppercase}}
.permission{{font-size:clamp(26px,4vw,42px);font-weight:700;overflow-wrap:anywhere;letter-spacing:-.03em}}
.hero p{{max-width:760px;margin-bottom:0;color:#d6e5eb}}.permission-BLOCKED{{color:#ffd48c}}
.permission-ALLOWED,.permission-ALLOWED_WITHIN_SCOPE{{color:#8fe7ca}}
.grid{{display:grid;grid-template-columns:1.3fr 1fr;gap:20px}}section{{background:white;border:1px solid var(--line);border-radius:16px;padding:24px;margin-bottom:20px}}
h2{{font-size:23px;margin:0 0 14px;line-height:1.3}}.action{{font-size:21px;font-weight:650;color:var(--teal)}}
.muted,small{{color:var(--muted)}}dl{{display:grid;grid-template-columns:120px 1fr;gap:12px;margin:0}}
dt{{color:var(--muted)}}dd{{margin:0;overflow-wrap:anywhere}}ul{{padding-left:21px}}li{{overflow-wrap:anywhere;margin:6px 0}}
footer{{font-size:13px;color:var(--muted);padding:4px 0 20px}}a{{color:var(--teal)}}
@media(max-width:720px){{main{{padding:22px 16px}}header{{display:block}}.tag{{display:inline-block;margin-top:12px}}.grid{{grid-template-columns:1fr}}.hero{{padding:24px}}}}
</style></head><body><main>
<header><div><h1>ASDLC STATUS</h1><p>{escaped(status['project_name'])}</p></div>
<span class="tag">Structure: {escaped(status['structural_status'])}</span></header>
<div class="hero"><div class="eyebrow">Can I implement?</div>
<div class="permission permission-{permission}">{permission}</div><p>{escaped(status['implementation_reason'])}</p></div>
<div class="grid"><div>
<section><div class="eyebrow">Where am I?</div><h2>{escaped(stage_label(status['current_stage']))}</h2>
<dl><dt>Sprint</dt><dd>{escaped(status['sprint_status'].upper())}</dd><dt>Sprint ID</dt><dd>{escaped(status['sprint_id'])}</dd>
<dt>Objective</dt><dd>{escaped(status['sprint_objective'])}</dd></dl></section>
<section><div class="eyebrow">What should I do next?</div><p class="action">{escaped(next_action['action'])}</p>
<div class="eyebrow">Why</div><p>{escaped(next_action['reason'])}</p></section></div><div>
<section><div class="eyebrow">Sprint scope</div>{items(status['sprint_scope'])}
<div class="eyebrow">Acceptance criteria</div>{items(status['acceptance_criteria'])}</section>
<section><div class="eyebrow">Blockers</div>{items(status['blockers'])}</section>
<section><div class="eyebrow">Project binding</div><dl><dt>Provider</dt><dd>{escaped(status['provider'])}</dd>
<dt>CLI version</dt><dd>{escaped(status['cli_version'])}</dd><dt>Hook config</dt><dd>{escaped(status['guard']['configuration'])}</dd>
<dt>Hook trust</dt><dd>{escaped(status['guard']['runtime_trust'])}</dd></dl>
<p class="muted">{escaped(status['project_root'])}</p></section></div></div>
<footer>Read-only · Evaluated {escaped(status['evaluated_at'])} · Refreshes every 30 seconds · <a href="/status.json">JSON status</a><br>
Evidence presence does not establish human approval. Hook configuration does not prove runtime trust.</footer>
</main></body></html>'''


def make_server(root: Path, repo: Path = REPO, port: int = 8765) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            allowed_hosts = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            if self.headers.get('Host') not in allowed_hosts:
                self.send_error(403, 'Use the loopback dashboard URL')
                return
            path = urlsplit(self.path).path
            if path not in ('/', '/status.json'):
                self.send_error(404, 'Not Found')
                return
            status = project_status(root, repo)
            body = (json.dumps(status, indent=2).encode('utf-8') if path == '/status.json'
                    else render_dashboard(status).encode('utf-8'))
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8' if path == '/status.json' else 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


def serve_dashboard(root: Path, port: int = 8765) -> None:
    with make_server(root, port=port) as server:
        print(f'ASDLC dashboard: http://127.0.0.1:{server.server_port}', flush=True)
        print('Read-only. Press Ctrl+C to stop.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
