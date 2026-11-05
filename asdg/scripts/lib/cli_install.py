"""One preview/approve/apply engine for extracted packages and verified local clones."""
from __future__ import annotations

import difflib
import re
import tempfile
from pathlib import Path

from cli_files import Conflict, apply, plan
from cli_install_source import git_root, package, source_snapshot
from cli_model import REPO, git_value, json_bytes, now, sha
from cli_project import client_files, inspect, plan_initialization, preflight_package


def install(*, source=None, target=None, commit=None, client=None, project_state=None,
            apply_changes=False, expected_plan=None, repo=REPO):
    if apply_changes and not expected_plan:
        raise Conflict('--apply requires the exact --plan token from a reviewed dry run.')
    if expected_plan and not apply_changes:
        raise Conflict('--plan is only valid with --apply.')
    if bool(source) != bool(commit):
        raise Conflict('Clone installation requires both --source and --commit.')
    root = git_root(Path(target) if target else Path.cwd(), exact=bool(target))
    origin = Path(source).expanduser().resolve(strict=True) if source else root
    if origin != repo.resolve():
        raise Conflict('Run the selected package\'s own asdg/scripts/init.py entry point.')
    if source and (root == origin or origin in root.parents or root in origin.parents):
        raise Conflict('Clone source and target must be separate, non-nested repositories.')
    stamp = now()
    if expected_plan:
        match = re.fullmatch(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\.([0-9a-f]{64})', expected_plan)
        if not match:
            raise Conflict('Invalid installation plan token.')
        stamp = match[1]
    if not source:
        preflight_package(origin)
    info, entries = source_snapshot(origin, commit)
    # Normalize both acquisitions to exactly the manifest members. Unlisted provider
    # templates can never become client integration files through directory scanning.
    with tempfile.TemporaryDirectory(prefix='asdg-install-plan-') as area:
        normalized = Path(area)
        for name, data in entries.items():
            path = normalized / 'asdg' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        changes, files = [], []
        for name, data in entries.items():
            relative = 'asdg/' + name
            change = plan(root, relative, data)
            if change:
                changes.append(change)
            files.append({'path': relative, 'action': 'added' if change else 'unchanged',
                          'sha256': sha(data), 'kind': 'distribution'})
        report, generated = plan_initialization(root, repo=normalized, project_state=project_state,
                                                client=client, timestamp=stamp, source=info)
        if not source and any(client_files(root, origin, name) != client_files(root, normalized, name)
                              for name in report['clients_applied']):
            raise Conflict('Unselected integration templates in extracted package; use a clean selected package.')
        changes.extend(generated)
        for change in generated:
            path = change.relative.as_posix()
            row = {'path': path, 'action': 'added' if change.before is None else 'modified',
                   'before_sha256': sha(change.before) if change.before is not None else None,
                   'sha256': sha(change.after), 'kind': 'integration-or-scaffold', 'mode': oct(change.mode)}
            row['diff'] = ''.join(difflib.unified_diff(
                (change.before or b'').decode('utf-8').splitlines(True),
                change.after.decode('utf-8').splitlines(True), fromfile='before/' + path, tofile='after/' + path))
            files.append(row)
        identity = {'git_dir': git_value(root, 'rev-parse', '--absolute-git-dir'),
                    'head': git_value(root, 'rev-parse', 'HEAD'),
                    'branch': git_value(root, 'symbolic-ref', '-q', 'HEAD')}
        approval = {'source': info, 'target': str(root), 'git': identity, 'timestamp': stamp,
                    'client': client, 'project_status': project_state, 'files': files}
        token = stamp + '.' + sha(json_bytes(approval))
        report.update(source=info, files=files, plan=token, dry_run=not apply_changes,
                      planned_files=[c.relative.as_posix() for c in changes],
                      unchanged=not changes, installation_complete=False, context_survey={'offered': False, 'executed': False,
                                                                   'requires_separate_affirmative': True})
        if apply_changes:
            if token != expected_plan:
                raise Conflict('Installation plan changed; review a fresh dry run before applying.')
            if source_snapshot(origin, commit) != (info, entries):
                raise Conflict('Source changed during preflight; review a fresh dry run.')

            def verify():
                _, installed_entries = package(root)
                if installed_entries != entries:
                    raise Conflict('Installed package differs from the selected source.')
                checked = inspect(root, repo=root)
                if not checked['structure_ok']:
                    raise Conflict('Post-install verification failed: ' + '; '.join(checked['missing']))
                report['verification'] = checked

            report['changed_files'] = apply(changes, verify=verify)
            report['installation_complete'] = True
            report['structure_ok'] = True
        return report


def render(report):
    lines = [f"ASDG {report['source']['version']} — {report['source']['kind']}",
             'Package integrity matched; release approval NOT_ESTABLISHED; hook trust NOT_ASSESSED.',
             'Target: ' + report['project_root']]
    if report['source']['commit']:
        lines.append('Verified source commit: ' + report['source']['commit'])
    for row in report['files']:
        lines.append(f"{row['action']:9} {row['path']}  sha256={row['sha256']}")
        if row.get('diff'):
            lines.append(row['diff'].rstrip())
    lines.extend('NOTE: ' + note for note in report['notes'])
    if report['dry_run']:
        lines += ['No project or source files changed. Review every planned change above.',
                  'After explicit developer approval, repeat the same options replacing --dry-run with:',
                  '--apply --plan ' + report['plan']]
    else:
        lines += ['ASDG installation complete; package and integration structure verified.',
                  'Native Claude/Codex invocation and hook trust remain NOT_VERIFIED.',
                  'Next, use /asdg-status in your project chat.',
                  'Status reports where your project stands and recommends the next ASDG skill.',
                  'This installation did not run Status, create team chats or start Context analysis; installation approval authorizes none of those actions.']
    return '\n'.join(lines)
