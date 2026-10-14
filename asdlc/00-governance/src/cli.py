#!/usr/bin/env python3
"""Elustondo.ai ASDLC CLI: install once, initialize the current Git project."""
from __future__ import annotations

import argparse
import json
import sys

sys.dont_write_bytecode = True
from cli_files import Conflict, safe_path
from cli_model import COMMAND, REPO, SHORT_COMMAND, VERSION, agent_by_name, catalogue, project_root, require_python
from cli_project import initialize, inspect
from cli_sprint import check_implementation, start, stop
from cli_status import project_status, render_next, render_status


def main(argv: list[str] | None = None) -> int:
    if not require_python():
        return 1
    parser = argparse.ArgumentParser(prog=SHORT_COMMAND, description=__doc__)
    parser.add_argument('--version', action='version', version=f'{COMMAND} {VERSION}')
    sub = parser.add_subparsers(dest='operation', required=True)
    sub.add_parser('install', help='Install user-local Python launchers and shell PATH configuration')
    sprint = sub.add_parser('sprint', help='Manage authoritative project sprint state')
    sprint_actions = sprint.add_subparsers(dest='action', required=True)
    sprint_status = sprint_actions.add_parser('status')
    sprint_status.add_argument('--json', action='store_true')
    sprint_start = sprint_actions.add_parser('start')
    sprint_start.add_argument('--id', required=True)
    sprint_start.add_argument('--objective', required=True)
    sprint_start.add_argument('--scope', action='append', required=True, help='exact file or directory ending in /; repeatable')
    sprint_start.add_argument('--acceptance', action='append', required=True, help='acceptance criterion; repeatable')
    sprint_actions.add_parser('stop')
    check = sprint_actions.add_parser('check-implementation')
    check.add_argument('--path', action='append', default=[], help='every proposed target; repeatable')
    for name in ('init', 'status', 'verify', 'next'):
        command = sub.add_parser(name)
        command.add_argument('--json', action='store_true', help='machine-readable report')
        if name == 'status':
            command.add_argument('--path', action='append', default=None, help='evaluate a proposed implementation target; repeatable')
    baseline = sub.add_parser('baseline', help='Capture existing-system evidence via specialist agents')
    baseline_actions = baseline.add_subparsers(dest='action', required=True)
    capture_cmd = baseline_actions.add_parser('capture', help='Read-only source; specialist-owned baseline artifacts')
    capture_cmd.add_argument('--source', required=True, help='path of pre-ASDLC project, left untouched')
    capture_cmd.add_argument('--dry-run', action='store_true', help='inventory and validate without invoking agents')
    capture_cmd.add_argument('--max-agents', type=int, default=None, help='limit specialist count for a pilot')
    capture_cmd.add_argument('--timeout', type=int, default=600, help='seconds per Codex invocation (60-3600)')
    capture_cmd.add_argument('--json', action='store_true', help='print resulting report as JSON')
    dashboard = sub.add_parser('dashboard', help='Serve the read-only local ASDLC dashboard')
    dashboard.add_argument('--port', type=int, default=8765)
    agent = sub.add_parser('agent', help='Inspect definitions; does not run an LLM')
    actions = agent.add_subparsers(dest='action', required=True)
    listing = actions.add_parser('list')
    listing.add_argument('--json', action='store_true')
    description = actions.add_parser('describe')
    description.add_argument('name', help='Native name, stable ID, stage number, architect or coordinator')
    args = parser.parse_args(argv)
    if args.operation == 'install':
        from cli_install import main as install_main
        return install_main([])
    try:
        if args.operation == 'agent':
            agents, _ = catalogue()
            if args.action == 'list':
                if args.json:
                    print(json.dumps({'agents': agents, 'live_invocation_tested': False}, indent=2))
                else:
                    for item in agents:
                        print(f"{item['native_name']:20} {item['title']}")
                    print('Definitions only. This is not a live-agent health check.')
            else:
                item = agent_by_name(args.name)
                print(f"Definition: {item['native_name']} ({item['role_id']})\n")
                print(safe_path(REPO, item['entry']).read_text(encoding='utf-8'))
            return 0
        root = project_root()
        if args.operation == 'baseline':
            from pathlib import Path
            from cli_baseline import capture
            report = capture(root, Path(args.source), dry_run=args.dry_run,
                             max_agents=args.max_agents, timeout=args.timeout)
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                if report.get('run_id'):
                    print('ASDLC baseline trial captured.' if report['partial'] else 'ASDLC baseline captured.')
                    print(f"{len(report['selected_stages'])} specialists completed. Ready for human review.")
                    print('ALL GOOD!')
                else:
                    print('Baseline dry run complete.')
                    print(f"Eligible source files: {report['source_files']}; excluded: {len(report['source_skipped'])}.")
                    print('No agents invoked. ALL GOOD!')
            return 0
        if args.operation == 'dashboard':
            if not 0 <= args.port <= 65535:
                raise Conflict('Dashboard port must be between 0 and 65535.')
            from cli_dashboard import serve_dashboard
            serve_dashboard(root, args.port)
            return 0
        if args.operation in ('status', 'next'):
            status = project_status(root, requested_paths=getattr(args, 'path', None))
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print(render_status(status) if args.operation == 'status' else render_next(status))
            return 1 if status['errors'] else 0
        if args.operation == 'sprint':
            if args.action == 'check-implementation':
                allowed, reason = check_implementation(root, args.path, guidance=True)
                if not allowed:
                    print('IMPLEMENTATION BLOCKED')
                print(reason)
                return 0 if allowed else 1
            # Validate the project binding before human state transitions.
            status = project_status(root)
            if status['errors']:
                raise Conflict('Project structure is incomplete. Run asdg init and verify first.')
            state = (start(root, args.id, args.objective, args.scope, args.acceptance)
                     if args.action == 'start' else stop(root) if args.action == 'stop' else status['sprint_state'])
            if getattr(args, 'json', False):
                print(json.dumps(state, indent=2))
            elif state['status'] == 'inactive':
                print('No active sprint.')
            else:
                print(f"Sprint {state['sprint_id']} active.")
                print(f"Objective: {state['objective']}")
                print('ALL GOOD!')
            return 0
        if args.operation == 'init':
            report = initialize(root)
            report.update(inspect(root))
        else:
            report = inspect(root)
        if args.json:
            print(json.dumps(report, indent=2))
        elif args.operation in ('init', 'verify'):
            if report['structure_ok']:
                print('ASDLC initialized and verified.' if args.operation == 'init'
                      else 'ASDLC structure verified.')
                print('ALL GOOD!')
            else:
                print('ASDLC initialization failed.' if args.operation == 'init'
                      else 'ASDLC verification failed.', file=sys.stderr)
                for item in report['missing']:
                    print(f'ERROR: Missing or incomplete required structure: {item}', file=sys.stderr)
        return 0 if report['structure_ok'] else 1
    except (Conflict, OSError, ValueError, KeyError, TypeError) as exc:
        if getattr(args, 'json', False):
            print(json.dumps({'error': str(exc), 'operation': args.operation}), file=sys.stderr)
        else:
            if args.operation in ('init', 'verify'):
                print('ASDLC initialization failed.' if args.operation == 'init'
                      else 'ASDLC verification failed.', file=sys.stderr)
            print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
