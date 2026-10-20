#!/usr/bin/env python3
"""Elustondo.ai ASDG CLI: install once, initialize the current Git project."""
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
    migration = sub.add_parser('migrate-namespace', help='Migrate reviewed legacy project state without initialization')
    migration.add_argument('--apply', action='store_true', help='explicitly apply; default is read-only planning')
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
            mode = command.add_mutually_exclusive_group()
            mode.add_argument('--facts-only', action='store_true', help='skip coordinator advice')
            mode.add_argument('--advise', action='store_true', help='include coordinator advice, also with --json')
            command.add_argument('--verbose', action='store_true', help='save detailed advice in the canonical planning folder')
            command.add_argument('--path', action='append', default=None, help='evaluate a proposed implementation target; repeatable')
    baseline = sub.add_parser('baseline', help='Capture existing-system evidence via specialist agents')
    baseline_actions = baseline.add_subparsers(dest='action', required=True)
    capture_cmd = baseline_actions.add_parser('capture', help='Read-only source; specialist-owned baseline artifacts')
    capture_cmd.add_argument('--source', required=True, help='path of pre-ASDG project, left untouched')
    capture_cmd.add_argument('--dry-run', action='store_true', help='inventory and validate without invoking agents')
    capture_cmd.add_argument('--max-agents', type=int, default=None, help='limit specialist count for a pilot')
    capture_cmd.add_argument('--timeout', type=int, default=600, help='seconds per Codex invocation (60-3600)')
    capture_cmd.add_argument('--json', action='store_true', help='print resulting report as JSON')
    dashboard = sub.add_parser('dashboard', help='Serve the read-only local ASDG dashboard')
    dashboard.add_argument('--port', type=int, default=8765)
    agent = sub.add_parser('agent', help='Inspect definitions; does not run an LLM')
    actions = agent.add_subparsers(dest='action', required=True)
    listing = actions.add_parser('list')
    listing.add_argument('--json', action='store_true')
    description = actions.add_parser('describe')
    description.add_argument('name', help='Native name, stable ID, stage number, architect or coordinator')
    args = parser.parse_args(argv)
    if args.operation == 'status' and args.verbose:
        if args.facts_only:
            parser.error('--facts-only cannot be combined with --verbose')
        if args.json and not args.advise:
            parser.error('--json --verbose requires --advise; plain --json never invokes the coordinator')
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
        if args.operation == 'migrate-namespace':
            from cli_namespace import migrate_project
            print(json.dumps(migrate_project(root, REPO, apply=args.apply), indent=2))
            return 0
        if args.operation == 'baseline':
            from pathlib import Path
            from cli_baseline import capture
            report = capture(root, Path(args.source), dry_run=args.dry_run,
                             max_agents=args.max_agents, timeout=args.timeout)
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                if report.get('run_id'):
                    print('ASDG baseline trial captured.' if report['partial'] else 'ASDG baseline captured.')
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
            want_advice = args.operation == 'status' and not args.facts_only and (args.advise or not args.json)
            if args.operation == 'status' and not args.json:
                print(render_status(status), flush=True)
            advice = None
            report = None
            if want_advice:
                from cli_advice import coordinator_advice, render_advice
                if not args.json:
                    print('\nConsulting the ASDG coordinator...', flush=True)
                advice = coordinator_advice(root, status)
                if not args.json:
                    print(render_advice(advice))
                if args.verbose:
                    if advice['status'] != 'available':
                        report = {'status': 'not_saved', 'reason': 'Coordinator advice is unavailable.'}
                    else:
                        from cli_advice_report import save_advice
                        try:
                            path = save_advice(root, status, advice)
                            report = {'status': 'saved', 'path': str(path)}
                        except (OSError, ValueError, KeyError, TypeError) as exc:
                            report = {'status': 'failed', 'reason': f'Could not save advisory report: {exc}'}
                    if not args.json:
                        print('Advisory report: ' + report['path'] if report['status'] == 'saved'
                              else 'Advisory report not saved: ' + report['reason'])
            if args.json:
                result = dict(status, advice=advice) if advice is not None else status
                if report is not None:
                    result = dict(result, advice_report=report)
                print(json.dumps(result, indent=2))
            elif args.operation == 'next':
                print(render_next(status))
            failed = (advice is not None and advice['status'] != 'available'
                      or report is not None and report['status'] != 'saved')
            return 1 if status['errors'] or failed else 0
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
                print('ASDG initialized and verified.' if args.operation == 'init'
                      else 'ASDG structure verified.')
                print('ALL GOOD!')
            else:
                print('ASDG initialization failed.' if args.operation == 'init'
                      else 'ASDG verification failed.', file=sys.stderr)
                for item in report['missing']:
                    print(f'ERROR: Missing or incomplete required structure: {item}', file=sys.stderr)
        return 0 if report['structure_ok'] else 1
    except (Conflict, OSError, ValueError, KeyError, TypeError) as exc:
        if getattr(args, 'json', False):
            print(json.dumps({'error': str(exc), 'operation': args.operation}), file=sys.stderr)
        else:
            if args.operation in ('init', 'verify'):
                print('ASDG initialization failed.' if args.operation == 'init'
                      else 'ASDG verification failed.', file=sys.stderr)
            print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
