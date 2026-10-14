"""Observe, guard and guide from one authoritative project/sprint/evidence snapshot."""
from __future__ import annotations

import json
import re
from pathlib import Path

from cli_files import Conflict, read_bytes, safe_path
from cli_model import ARTIFACTS, PROVIDER, REPO, VERSION, catalogue, now
from cli_policy import implementation_permission
from cli_project import inspect

LIFECYCLE = Path('.asdlc/lifecycle.json')
EMPTY_LIFECYCLE = {'schema_version': 1, 'stages': {}}
RULES = Path('asdlc/00-governance/types/lifecycle-rules.json')


def lifecycle_rules(repo: Path) -> list[dict]:
    value = json.loads(safe_path(repo, RULES).read_bytes())
    rows = value.get('rules', [])
    if value.get('schema_version') != 1 or [row.get('stage') for row in rows] != list(range(1, 13)):
        raise Conflict('Unsupported lifecycle rules; expected ordered stages 01 through 12.')
    labels = re.findall(r'^\| (\d{2}) \| (.+?) \|$',
                        safe_path(repo, value['baseline']).read_text(encoding='utf-8'), re.MULTILINE)
    if [int(number) for number, _ in labels] != list(range(1, 13)):
        raise Conflict('Canonical lifecycle baseline must retain twelve ordered stages.')
    agents, _ = catalogue(repo)
    result = []
    for row, (number, label), agent in zip(rows, labels, agents[1:]):
        for field in ('evidence', 'action', 'source'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise Conflict(f'Invalid lifecycle rule {number}: {field}')
        result.append(dict(row, number=int(number), name=label.replace('&', 'and'),
                           slug=Path(agent['folder']).name))
    return result


def read_lifecycle(root: Path, rules: list[dict]) -> dict:
    raw = read_bytes(safe_path(root, LIFECYCLE))
    value = json.loads(raw) if raw is not None else EMPTY_LIFECYCLE
    if (not isinstance(value, dict) or set(value) != {'schema_version', 'stages'}
            or type(value['schema_version']) is not int or value['schema_version'] != 1 or not isinstance(value['stages'], dict)):
        raise Conflict('Invalid .asdlc/lifecycle.json; expected schema_version 1 and stages map.')
    known = {f"{rule['number']:02d}": rule for rule in rules}
    for number, entry in value['stages'].items():
        if number not in known or not isinstance(entry, dict) or set(entry) != {'artifacts', 'not_applicable_reason'}:
            raise Conflict(f'Invalid lifecycle evidence entry: {number}')
        files, reason = entry['artifacts'], entry['not_applicable_reason']
        if not isinstance(files, list) or any(not isinstance(p, str) or not p.strip() for p in files):
            raise Conflict(f'Invalid artifact list for stage {number}.')
        if reason is not None and (not known[number].get('may_be_not_applicable')
                                  or not isinstance(reason, str) or not reason.strip() or files):
            raise Conflict('Only Stage 06 permits an explicit unnecessary-POC reason, without artifacts.')
        for file in files:
            relative = Path(file)
            expected = ARTIFACTS / known[number]['slug']
            if relative.is_absolute() or not relative.is_relative_to(expected) or relative.name == 'README.md':
                raise Conflict(f'Stage {number} evidence must be a named artifact in {expected}, not a README placeholder.')
            safe_path(root, relative)
    return value


def evidence_status(root: Path, rules: list[dict], value: dict) -> list[dict]:
    stages = []
    for rule in rules:
        entry = value['stages'].get(f"{rule['number']:02d}", {})
        files = entry.get('artifacts', [])
        absent = []
        for file in files:
            raw = read_bytes(safe_path(root, file))
            if raw is None or not raw.strip():
                absent.append(file)
        skipped = bool(entry.get('not_applicable_reason'))
        established = skipped or bool(files) and not absent
        stages.append(dict(rule, readiness='NOT_APPLICABLE' if skipped else 'ESTABLISHED' if established else 'MISSING',
                           artifacts=files, missing_paths=absent,
                           not_applicable_reason=entry.get('not_applicable_reason')))
    return stages


def recommendation(stages: list[dict], sprint: dict | None, errors: list[str]) -> dict:
    if errors:
        return {'code': 'REPAIR_STATE', 'stage': None, 'action': 'Repair ASDLC structure or state, then run asdg verify.',
                'reason': errors[0]}
    unmet = next((stage for stage in stages if stage['readiness'] == 'MISSING'), None)
    if unmet is None:
        return {'code': 'REVIEW_NEXT_CYCLE', 'stage': stages[-1],
                'action': 'Review the recorded evidence and select the next roadmap or sprint cycle.',
                'reason': 'Evidence is established for all twelve stages; completion and approval are not inferred.'}
    active = bool(sprint and sprint['status'] == 'active')
    code, action = f"ESTABLISH_STAGE_{unmet['number']:02d}", unmet['action']
    if unmet['number'] >= 7 and not active:
        code, action = 'DEFINE_SPRINT', 'Define and review the sprint plan, then start a sprint for the selected scope.'
    elif unmet['number'] == 9 and active:
        code = 'IMPLEMENT_WITHIN_SPRINT'
    reason = (f"Required evidence is missing: {', '.join(unmet['missing_paths'])}." if unmet['missing_paths'] else
              f"Project structure is valid, but no {unmet['name'].lower()} artifact is established.")
    return {'code': code, 'stage': unmet, 'action': action, 'reason': reason}


def project_status(root: Path, repo: Path = REPO, requested_paths: list[str] | None = None) -> dict:
    """Read-only evaluator. Views render its result; they never decide readiness or permissions."""
    errors, stages = [], []
    try:
        report = inspect(root, repo)
        errors.extend(report['missing'])
    except (OSError, ValueError, TypeError, KeyError) as exc:
        report = {'project_root': str(root), 'provider': PROVIDER, 'cli_version': VERSION,
                  'structure_ok': False, 'missing': [str(exc)], 'sprint_state': None}
        errors.append(str(exc))
    try:
        rules = lifecycle_rules(repo)
        stages = evidence_status(root, rules, read_lifecycle(root, rules))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        if str(exc) not in errors:
            errors.append(str(exc))
    sprint = report.get('sprint_state')
    permission = implementation_permission(root, sprint, errors, requested_paths)
    next_action = recommendation(stages, sprint, errors)
    current = next_action['stage']
    blockers = list(errors)
    if not errors and permission['permission'] == 'BLOCKED' and permission['reason'] not in blockers:
        blockers.append(permission['reason'])
    if current and current['readiness'] == 'MISSING':
        blockers.append(next_action['reason'])
    return dict(report, project_name=root.name, evaluated_at=now(), errors=errors,
                structural_status='PASS' if report['structure_ok'] else 'INVALID',
                current_stage=current, lifecycle_stages=stages,
                current_stage_basis='EARLIEST_UNMET_EVIDENCE' if current and current['readiness'] == 'MISSING'
                else 'ALL_EVIDENCE_ESTABLISHED' if current else 'UNKNOWN',
                sprint_status=(sprint or {}).get('status', 'UNKNOWN'),
                sprint_id=(sprint or {}).get('sprint_id'), sprint_objective=(sprint or {}).get('objective'),
                sprint_scope=(sprint or {}).get('scope', []), acceptance_criteria=(sprint or {}).get('acceptance_criteria', []),
                implementation_permission=permission['permission'], implementation_reason=permission['reason'],
                implementation=permission, blockers=blockers,
                missing_required_artifacts=[{'stage': s['number'], 'required_evidence': s['evidence'],
                                             'missing_paths': s['missing_paths']} for s in stages if s['readiness'] == 'MISSING'],
                guard={'configuration': 'UNKNOWN' if 'implementation_enforcement' not in report else 'PRESENT' if not any(
                    '.codex/' in error for error in errors) else 'MISSING_OR_INVALID',
                       'runtime_trust': 'UNKNOWN', 'runtime_enforcement': 'NOT_VERIFIED'},
                recommendation=next_action)


def stage_label(stage: dict | None) -> str:
    return f"{stage['number']:02d} — {stage['name']}" if stage else 'UNKNOWN'


def render_status(status: dict) -> str:
    lines = ['ASDLC STATUS', '', f"Project: {status['project_name']}",
             f"Sprint: {status['sprint_status'].upper()}", f"Implementation: {status['implementation_permission']}",
             f"Stage: {stage_label(status['current_stage'])}", '', 'Recommended next action:',
             status['recommendation']['action']]
    if status['errors']:
        lines.extend(f'ERROR: {error}' for error in status['errors'])
    else:
        lines.extend(['', 'ALL GOOD structurally.'])
    return '\n'.join(lines)


def render_next(status: dict) -> str:
    next_action = status['recommendation']
    lines = ['Recommended next step:', stage_label(next_action['stage']), next_action['action'],
             '', 'Reason:', next_action['reason'], '']
    lines.append('Implementation: ' + status['implementation_permission'])
    if status['implementation_permission'] == 'BLOCKED':
        lines.append(status['implementation_reason'])
    return '\n'.join(lines)
