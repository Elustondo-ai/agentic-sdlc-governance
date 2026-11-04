"""One conservative three-way file synchronizer for promote and upgrade."""
from __future__ import annotations

import json
from pathlib import Path

from cli_files import Conflict, apply as apply_changes, plan, read_bytes, safe_path
from cli_sync_manifest import (PROVIDER, STATE, MANIFEST, adopted_binding, baseline, digest,
                               encoded, methodology_path, repository_id, snapshot)


def endpoints(operation: str, source: dict, target: dict) -> None:
    if operation not in ('promote', 'upgrade'):
        raise Conflict('Unknown synchronization direction.')
    a, b = source['root'], target['root']
    if a == b or a in b.parents or b in a.parents:
        raise Conflict('Source and target must be separate, non-nested repositories.')
    canonical, pilot = (target, source) if operation == 'promote' else (source, target)
    declared = canonical['descriptor'].get('canonical_repository')
    if not isinstance(declared, str) or repository_id(declared) != canonical['info']['repository']:
        raise Conflict('Canonical repository origin does not match its distribution identity.')
    if pilot['info']['repository'] == canonical['info']['repository']:
        raise Conflict('Pilot origin must differ from the canonical repository.')
    pilot_canonical = pilot['descriptor'].get('canonical_repository')
    if pilot_canonical and repository_id(pilot_canonical) != canonical['info']['repository']:
        raise Conflict('Pilot belongs to a different canonical distribution.')
    binding = json.loads(pilot['binding_raw'] or b'null')
    if (not isinstance(binding, dict) or binding.get('schema_version') != 1
            or binding.get('provider') != PROVIDER or not binding.get('project_id')
            or binding.get('installation_mode') != 'embedded-distribution'
            or binding.get('distribution_root') != 'asdg' or binding.get('artifacts_root') != 'docs/asdg'):
        raise Conflict('Pilot project binding cannot be established.')
    if binding.get('distribution_version') != pilot['info']['version']:
        catalog_hash = pilot['hashes'].get('00-governance/types/agent-catalog.json')
        if not adopted_binding(pilot['root'], pilot['binding_raw'], pilot['info']['version'], catalog_hash):
            raise Conflict('Pilot version differs from its binding without an adopted upgrade.')


def classify(old: str | None, incoming: str | None, local: str | None) -> tuple[str, str]:
    if incoming == local:
        return 'unchanged', 'same content'
    if incoming == old:
        return 'unchanged', 'local change retained'
    if local == old:
        return ('deleted' if incoming is None else 'added' if local is None else 'modified'), 'source change'
    return 'conflicting', 'both changed since baseline' if old is not None else 'no common baseline for different content'


def preview(operation: str, source_path, target_path):
    source, target = snapshot(source_path), snapshot(target_path)
    endpoints(operation, source, target)
    old, basis = baseline(source, target)
    rows, changes = [], []
    # Include baseline paths to detect deletions, but never enumerate unrelated application files.
    for name in sorted(set(old) | set(source['hashes']) | set(target['hashes'])):
        methodology_path(name)
        target_path = safe_path(target['core'], name)
        current = read_bytes(target_path)  # An unlisted local file still blocks an addition collision.
        local, incoming = digest(current), source['hashes'].get(name)
        category, reason = classify(old.get(name), incoming, local)
        tracked = 'asdg/' + name in target['tracked']
        if category == 'deleted' and not tracked:
            category, reason = 'conflicting', 'refusing to delete untracked work'
        rows.append({'path': 'asdg/' + name, 'status': category, 'reason': reason,
                     'baseline_sha256': old.get(name), 'source_sha256': incoming,
                     'target_sha256': local, 'target_tracked': tracked})
        if category in ('added', 'modified', 'deleted'):
            change = plan(target['root'], 'asdg/' + name, source['data'].get(name), replace=True)
            if change:
                changes.append(change)
    counts = {key: sum(r['status'] == key for r in rows)
              for key in ('added', 'modified', 'deleted', 'unchanged', 'conflicting')}
    report = {'operation': operation, 'source': source['info'], 'target': target['info'],
              'baseline': basis, 'counts': counts, 'files': rows,
              'warnings': ['Only asdg/ distribution files are synchronized; installed adapters, hooks and project state are unchanged.',
                           'Apply records adoption, not a release or methodology approval.'],
              'sync_state_sha256': digest(read_bytes(safe_path(target['core'], STATE)))}
    if not source['info']['manifest_matches_worktree']:
        report['warnings'].append('Source worktree differs from its delivery manifest; snapshot hashes identify the actual proposed bytes.')
    if operation == 'upgrade' and not source['info']['manifest_matches_worktree']:
        report['warnings'].append('Upgrade apply requires a verified canonical manifest; refresh/review it before applying.')
    report['plan_id'] = digest(encoded(report))
    return report, changes, source, target


def synchronize(operation: str, source_path, target_path, *, apply=False, expected_plan=None) -> dict:
    report, changes, source, target = preview(operation, source_path, target_path)
    if not apply:
        return dict(report, dry_run=True, applied=False)
    if not expected_plan or expected_plan != report['plan_id']:
        raise Conflict('Apply requires the exact --plan digest from a fresh reviewed dry run.')
    if report['counts']['conflicting']:
        raise Conflict('Conflicting files require reconciliation; nothing applied.')
    if operation == 'upgrade' and not source['info']['manifest_matches_worktree']:
        raise Conflict('Canonical worktree does not match its versioned manifest; nothing upgraded.')
    record = {'operation': operation, 'target_repository': target['info']['repository'],
              'target_binding_sha256': digest(target['binding_raw']),
              'source_repository': source['info']['repository'], 'source_commit': source['info']['head'],
              'version': source['info']['version'], 'snapshot_sha256': source['info']['snapshot_sha256'],
              'source_snapshot_kind': source['info']['snapshot_kind'],
              'source_delivery_manifest': source['info']['delivery_manifest'],
              'validation_status': source['info']['validation_status'],
              'human_approval_status': source['info']['human_approval_status'],
              'files': source['hashes']}
    state = target['state']
    state['upstreams'][source['info']['repository']] = record
    receipt = plan(target['root'], 'asdg/' + STATE, encoded(state), replace=True)
    if receipt:
        changes.append(receipt)
    # Re-read source, target, binding and receipt immediately before the existing file transaction.
    fresh, _, _, _ = preview(operation, source_path, target_path)
    if fresh['plan_id'] != report['plan_id']:
        raise Conflict('Source or target changed during preflight; review a new dry run.')
    written = apply_changes(changes)
    return dict(report, dry_run=False, applied=True,
                written_files=[str(Path(p).relative_to(target['root'])) for p in written])


def render(report: dict) -> str:
    source = report['source']
    manifest = source['delivery_manifest']
    lines = [f"ASDG {report['operation']}: {'applied' if report['applied'] else 'dry run; no writes'}",
             f"Source: {source['root']} (declared version {source['version']})",
             f"Source bytes: {source['snapshot_kind']}; delivery manifest: {manifest['status']}",
             'Manifest differences: ' + ', '.join(f'{k}: {len(v)}' for k, v in manifest['differences'].items()),
             f"Validation: {source['validation_status']}; human approval: {source['human_approval_status']}",
             f"Target: {report['target']['root']} ({report['target']['version']})",
             'Baseline: ' + report['baseline'],
             ', '.join(f'{name}: {count}' for name, count in report['counts'].items())]
    lines += [f"{row['status'].upper():12} {row['path']} — {row['reason']}" for row in report['files']]
    lines += ['NOTE: ' + warning for warning in report['warnings']]
    lines += ['Plan: ' + report['plan_id'], 'After review: repeat with --apply --plan <digest>; conflicts block all writes.']
    return '\n'.join(lines)
