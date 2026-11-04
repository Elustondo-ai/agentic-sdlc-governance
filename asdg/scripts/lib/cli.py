#!/usr/bin/env python3
"""Embedded ASDG: initialize and inspect this client repository."""
from __future__ import annotations

import argparse
import json
import sys

sys.dont_write_bytecode = True
from cli_files import Conflict, safe_path
from cli_model import COMMAND, REPO, SHORT_COMMAND, VERSION, agent_by_name, catalogue, project_root, require_python
from cli_project import inspect
from cli_sprint import check_implementation, start, stop
from cli_status import project_status, render_next, render_status


def main(argv: list[str] | None = None) -> int:
    if not require_python():
        return 1
    parser = argparse.ArgumentParser(prog=SHORT_COMMAND, description=__doc__)
    parser.add_argument('--version', action='version', version=f'{COMMAND} {VERSION}')
    sub = parser.add_subparsers(dest='operation', required=True)
    for name in ('promote', 'upgrade'):
        sync = sub.add_parser(name, help='Preview or explicitly apply local methodology synchronization')
        sync.add_argument('--source', required=True, help='source Git repository root')
        sync.add_argument('--target', required=True, help='target Git repository root')
        mode = sync.add_mutually_exclusive_group(required=True)
        mode.add_argument('--dry-run', action='store_true', help='inspect without writing')
        mode.add_argument('--apply', action='store_true', help='apply the reviewed, conflict-free plan')
        sync.add_argument('--plan', help='exact plan digest returned by a reviewed dry run; required with --apply')
        sync.add_argument('--json', action='store_true', help='machine-readable preview or result')
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
        if name == 'init':
            command.add_argument('--project-status', choices=('new', 'defining', 'defined'), default=None,
                                 help='initial declaration only; defaults to new, preserves existing state')
            mode = command.add_mutually_exclusive_group()
            mode.add_argument('--dry-run', action='store_true', help='preview without writing (the default)')
            mode.add_argument('--apply', action='store_true', help='apply only a reviewed plan')
            command.add_argument('--plan', help='exact preview token; required with --apply')
            command.add_argument('--source', help='existing canonical clone root; run its own entry point')
            command.add_argument('--commit', help='explicit full commit ID of the canonical clone')
            command.add_argument('--target', help='existing target Git root; defaults to caller project')
            command.add_argument('--client', choices=('codex', 'claude', 'both'), default=None,
                                 help='client integration to add; repeat setup without it keeps the recorded clients (Codex if none)')
        if name == 'status':
            mode = command.add_mutually_exclusive_group()
            mode.add_argument('--facts-only', action='store_true', help='skip coordinator advice')
            mode.add_argument('--advise', action='store_true', help='include coordinator advice, also with --json')
            command.add_argument('--verbose', action='store_true', help='save detailed advice in the canonical planning folder')
            command.add_argument('--path', action='append', default=None, help='evaluate a proposed implementation target; repeatable')
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
    try:
        if args.operation in ('promote', 'upgrade'):
            from cli_sync import synchronize, render
            result = synchronize(args.operation, args.source, args.target,
                                 apply=args.apply, expected_plan=args.plan)
            print(json.dumps(result, indent=2) if args.json else render(result))
            return 1 if result['counts']['conflicting'] else 0
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
        if args.operation == 'init':
            from cli_install import install, render
            report = install(source=args.source, target=args.target, commit=args.commit, client=args.client,
                             project_state=args.project_status, apply_changes=args.apply, expected_plan=args.plan)
            print(json.dumps(report, indent=2) if args.json else render(report))
            return 0
        root = project_root()
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
        report = inspect(root)
        if args.json:
            print(json.dumps(report, indent=2))
        elif args.operation == 'verify':
            if report['structure_ok']:
                print('ASDG structure verified.')
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
