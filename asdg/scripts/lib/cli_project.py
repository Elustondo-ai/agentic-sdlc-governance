"""Preflight one embedded distribution and preserve client-owned state."""
from __future__ import annotations
import json
import re
import shlex
from pathlib import Path
from cli_clients import (CLIENTS, INTEGRATIONS, claude_bridge, claude_bridge_problems, claude_files,
                         integrations_bytes, read_integrations, resolve_clients)
from cli_files import Conflict, plan, read_bytes, safe_path
from cli_model import ARTIFACTS, BINDING, PROVIDER, REPO, VERSION, catalogue, json_bytes, now, sha
from cli_sprint import INACTIVE, SPRINT, read_state
from documentation import nonblank_source_lines, review_record, PROJECT_REVIEWS

STAGE_FOLDERS = ()  # Flat numbered documents; no mandatory perspective directories.
STAGE_NOTE = (  # Legacy scaffold signature, retained only for Context compatibility.
    'Intended documents live at this stage root; substantiated evidence belongs in `current/`.\n'
    'Use `planned-release/` for release work and `planned-sprint/` for sprint work, linked to Stage 07.\n'
    "At cycle closeout, consolidate verified outcomes into Current before deleting that cycle's temporary plans.\n")

HOOK_CONFIG = b'[features]\nhooks = true\n'
BEGIN, END = '<!-- ASDG:BEGIN bootstrap-v2 -->', '<!-- ASDG:END -->'
MANAGED_BEGIN = '<!-- ASDG:BEGIN'  # Any version of the managed block.
BRIDGE = f'''{BEGIN}
## ASDG bootstrap
This project uses the ASDG methodology embedded in `asdg/`. ASDG setup generates this block; edit only outside its markers.
Before any project work, read and follow `asdg/AGENTS.md` and every startup source it requires.
If a required source is missing or contradictory, stop dependent work and report it; read-only diagnosis stays allowed.
Shared ASDG rules live under `asdg/`; project-owned guidance follows this block.
{END}
'''
IGNORE_BEGIN, IGNORE_END = '# ASDG generated files: BEGIN', '# ASDG generated files: END'
IGNORE = f'{IGNORE_BEGIN}\n/logs/\n/asdg/**/__pycache__/\n/asdg/**/*.pyc\n/.asdg/backups/\n/.asdg/cache/\n{IGNORE_END}\n'


def stage_readme(repo, slug):
    """Read a portable human-facing stage introduction without project assumptions."""
    data = read_bytes(safe_path(repo, Path('asdg/scaffolds/stages') / (slug + '.md')))
    if data is None or nonblank_source_lines(data.decode()) > 50:
        raise Conflict(f'Missing or oversized stage introduction: {slug}')
    return data


# Exact earlier generated blocks, appended at the end of AGENTS.md by older setups.
# Setup moves an unedited one to the top; an edited one stays a conflict.
_LEGACY_BRIDGE_V1 = '''<!-- ASDG:BEGIN embedded-v1 -->
## ASDG integration
This client carries its own methodology in `asdg/`; read `asdg/AGENTS.md`.
Read `asdg/skills/asdg-focus/session-policy.md` on each turn.
Before substantial work run `python3 asdg/scripts/cli.py status --json` from the client root.
Use `python3 asdg/scripts/cli.py verify` for structure; folders do not prove compliance.
Use this local entry point; a machine-wide `asdg` may resolve an older installation.
Client evidence belongs in `docs/asdg/`; methodology definitions are not client evidence.
Preserve `.asdg/` state and review history; disposable activity logs belong under `logs/`.
Explicit Focus selection affects this conversation only; reading a role never activates it.
Sessions act under 00 Governance (ASDG-COORDINATOR) by default; there is no role-less path.
No specialist is active merely because this repository was initialized.
## Implementation gate
Before application edits, inspect `.asdg/sprint.json` and check EVERY target with
`python3 asdg/scripts/cli.py sprint check-implementation --path <target>`.
Without an active scoped sprint, report IMPLEMENTATION BLOCKED and do not implement.
Scope is an exact file or a directory ending in /; satisfy its objective and acceptance criteria.
Only an explicit human sprint start/stop decision authorizes a transition; never infer one.
Use scoped apply_patch edits. Arbitrary shell/REPL writes remain blocked by the guard.
Do not edit state, hook definitions or ASDG policies as part of application implementation.
Agent changes to ASDG rules run only under explicitly selected ASDG Admin (asdg/admin/AGENTS.md) within a human-authorized scope.
Review and trust project hooks in Codex; configuration alone does not establish enforcement.
Every agent may create and update project documentation and supporting assets under docs/ without an active sprint or separate save approval.
Use asdg/00-governance/docs/documentation-authority.md; documentation is the default shared handoff, while code, approvals and state transitions retain their gates.
A sprint does not widen role authority; asdg-decision preserves Focus and operational gates.
Explicit human use of asdg-approve permits only the documentation-acceptance recording workflow in asdg/skills/asdg-approve/recording.md.
Explicit human sprint requests use asdg/skills/asdg-sprint-start/SKILL.md or asdg/skills/asdg-sprint-close/SKILL.md; these utilities do not widen specialist delivery authority.
Installation grants no approval, publication, commit, push, deployment or hook trust.
<!-- ASDG:END -->
'''
_LEGACY_ADMIN_LINE = 'Agent changes to ASDG rules run only under explicitly selected ASDG Admin (asdg/admin/AGENTS.md) within a human-authorized scope.\n'
_LEGACY_DEFAULT_LINE = 'Sessions act under 00 Governance (ASDG-COORDINATOR) by default; there is no role-less path.\n'
LEGACY_BRIDGES = (_LEGACY_BRIDGE_V1,
                  _LEGACY_BRIDGE_V1.replace(_LEGACY_ADMIN_LINE, ''),
                  _LEGACY_BRIDGE_V1.replace(_LEGACY_ADMIN_LINE, '').replace(_LEGACY_DEFAULT_LINE, ''))


def distribution(repo):
    value = json.loads(read_bytes(safe_path(repo, 'asdg/metadata/distribution.json')) or b'{}')
    if (value.get('schema_version') != 1 or value.get('provider') != PROVIDER
            or value.get('version') != VERSION or value.get('installation_mode') != 'embedded-distribution'):
        raise Conflict('Unsupported or missing embedded distribution metadata.')
    return value


def hook_config(root, repo=REPO):
    denied = json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny', 'permissionDecisionReason':
                        'IMPLEMENTATION BLOCKED\nASDG guard failed to execute.'}})
    command = 'python3 -B "$(git rev-parse --show-toplevel)/asdg/scripts/hook.py"'
    guard = command + " || printf '%s\\n' " + shlex.quote(denied)
    hooks = {'PreToolUse': [{'matcher': '*', 'hooks': [
        {'type': 'command', 'command': guard, 'timeout': 10}]}]}
    for event in ('SubagentStart', 'SubagentStop', 'PostToolUse', 'PostToolUseFailure'):
        hooks[event] = [{'matcher': '*', 'hooks': [
            {'type': 'command', 'command': command + ' log', 'timeout': 10}]}]
    return json_bytes({'description': 'ASDG guard and public activity logs; review/trust in /hooks.', 'hooks': hooks})


def merge_block(old, block, begin, end, name):
    if old is None:
        return block.encode()
    text = old.decode('utf-8')
    if begin in text or end in text:
        if text.count(begin) != 1 or text.count(end) != 1 or block not in text:
            raise Conflict(f'Edited or incomplete managed section in {name}; reconcile manually.')
        return old
    return (text + ('\n' if text.endswith('\n') else '\n\n') + block).encode()


def bootstrap_is_current(text: str) -> bool:
    """True when AGENTS.md begins with the current bootstrap and has no other managed markers."""
    return text.startswith(BRIDGE) and text.count(MANAGED_BEGIN) == 1 and text.count(END) == 1


def merge_bootstrap(old):
    """Put the managed bootstrap first and keep every project-owned byte outside it."""
    if old is None:
        return BRIDGE.encode()
    text = old.decode('utf-8')
    if 'ELUSTONDO-ASDG:BEGIN' in text or 'ELUSTONDO-ASDLC:BEGIN' in text:
        raise Conflict('Linked/legacy AGENTS.md integration requires explicit migration.')
    if bootstrap_is_current(text):
        return old
    markers = (text.count(MANAGED_BEGIN), text.count(END))
    if markers != (0, 0):
        known = [block for block in LEGACY_BRIDGES if text.count(block) == 1]
        if markers != (1, 1) or len(known) != 1:
            raise Conflict('Edited, moved or incomplete ASDG bootstrap in AGENTS.md; reconcile it manually.')
        before, after = text.split(known[0])
        if before.endswith('\n\n'):
            before = before[:-1]  # Older setups added one separator newline before the block.
        project = before + after
        return (BRIDGE + ('\n' + project if project.strip() else '')).encode()
    if text.lstrip('\ufeff \t\r\n').startswith('---'):
        raise Conflict('YAML-first AGENTS.md requires manual review; nothing overwritten.')
    # The old bytes and declarations are retained in the hash-bound review ledger.
    # Do not display an old approval as if it governed the newly extended file.
    text = re.sub(r'\A(?:\ufeff)?\s*(?:AI-MODIFIED|PME-APPROVED) - [^\n]*\n*', '', text, count=1)
    return (BRIDGE + ('\n' + text if text.strip() else '')).encode()


def binding(root, catalog_hash):
    area = safe_path(root, '.asdg')
    raw = read_bytes(safe_path(root, BINDING))
    if raw is None:
        if area.exists() and (not area.is_dir() or any(area.iterdir())):
            raise Conflict('Unidentified nonempty .asdg directory; nothing overwritten.')
        return None
    value = json.loads(raw)
    if not isinstance(value, dict) or value.get('schema_version') != 1 or value.get('provider') != PROVIDER:
        raise Conflict('Foreign or unsupported .asdg/project.json; nothing overwritten.')
    if value.get('installation_mode') != 'embedded-distribution':
        raise Conflict('Existing linked installation needs explicit migration; state was preserved.')
    if value.get('catalog_sha256') != catalog_hash or value.get('distribution_version') != VERSION:
        from cli_sync_manifest import adopted_binding
        if not adopted_binding(root, raw, VERSION, catalog_hash):
            raise Conflict('Distribution or catalogue changed; review an upgrade before reinitializing.')
    if value.get('artifacts_root') != ARTIFACTS.as_posix() or value.get('distribution_root') != 'asdg':
        raise Conflict('Unsupported embedded layout; nothing overwritten.')
    return value


def template_files(repo):
    base = safe_path(repo, 'asdg/templates')
    if not base.is_dir():
        raise Conflict('Missing packaged discovery templates.')
    templates = []
    for path in sorted(base.rglob('*')):
        if path.is_symlink():
            raise Conflict('Symlink in distribution templates.')
        if path.is_file():
            relative = path.relative_to(base)
            if relative.parts[0] not in ('.agents', '.codex'):
                raise Conflict('Unexpected discovery template destination.')
            templates.append((relative, read_bytes(path)))
    return templates


def client_files(root, repo, client):
    """Managed files for one client integration; shared methodology files are planned separately."""
    if client == 'codex':
        return [(Path('.codex/hooks.json'), hook_config(root, repo)), (Path('.codex/config.toml'), HOOK_CONFIG),
                *template_files(repo)]
    return claude_files(repo)


def client_report(root, repo, installed):
    """Per client: never selected, complete or damaged. Runtime behavior is never verified here."""
    try:
        current = read_integrations(root)
    except Conflict as exc:
        problem = str(exc)
        return {name: {'selection': 'unknown', 'status': 'DAMAGED', 'problems': [problem],
                       'runtime': 'NOT_VERIFIED'} for name in CLIENTS}, [problem]
    recorded = current['clients'] if current else ({'codex': {'recorded_from': 'legacy installation'}} if installed else {})
    report, problems = {}, []
    for name in CLIENTS:
        if name not in recorded:
            report[name] = {'selection': 'not-selected', 'status': 'NOT_SELECTED', 'problems': [], 'runtime': 'NOT_VERIFIED'}
            continue
        found = [f'{relative}: missing or locally modified integration'
                 for relative, data in client_files(root, repo, name) if read_bytes(safe_path(root, relative)) != data]
        if name == 'claude':
            found += claude_bridge_problems(root)
        report[name] = {'selection': 'recorded' if current else 'legacy-unrecorded',
                        'recorded_from': recorded[name]['recorded_from'],
                        'status': 'DAMAGED' if found else 'COMPLETE', 'problems': found, 'runtime': 'NOT_VERIFIED'}
        problems.extend(found)
    return report, problems


def preflight_package(repo):
    distribution(repo)
    agents, digest = catalogue(repo)
    from cli_status import lifecycle_rules
    lifecycle_rules(repo)
    for name in ('asdg/AGENTS.md', 'asdg/scripts/cli.py', 'asdg/scripts/hook.py', 'asdg/skills/asdg-focus/session-policy.md'):
        if read_bytes(safe_path(repo, name)) is None:
            raise Conflict(f'Missing packaged input: {name}')
    for agent in agents:
        stage_readme(repo, Path(agent['folder']).name)
        for key in ('entry', 'skill'):
            if read_bytes(safe_path(repo, agent[key])) is None:
                raise Conflict(f'Missing role input: {agent[key]}')
        if read_bytes(safe_path(repo, Path('asdg/templates') / agent['adapter'])) is None:
            raise Conflict(f'Missing role adapter: {agent["native_name"]}')
    from cli_session import validate_admin
    validate_admin(repo)
    focus_root = safe_path(repo, 'asdg/templates/.agents/skills')
    if (list(focus_root.glob('asdg-focus-*/SKILL.md'))
            or not (focus_root / 'asdg-focus/SKILL.md').is_file()
            or not (focus_root / 'asdg-focus/agents/openai.yaml').is_file()):
        raise Conflict('Expected one shared Focus adapter and no per-role Focus picker templates.')
    return agents, digest


def plan_initialization(root, repo=REPO, project_state=None, client=None, timestamp=None, source=None):
    from cli_status import LIFECYCLE, PROJECT_STATUSES, lifecycle_rules, read_lifecycle
    timestamp = timestamp or now()
    for legacy in ('.asdlc', 'docs/asdlc'):
        if safe_path(root, legacy).exists():
            raise Conflict('Legacy ASDLC data requires explicit migration; use a fresh client for this pilot.')
    if project_state is not None and project_state not in PROJECT_STATUSES:
        raise Conflict('Unsupported initial project status.')
    agents, digest = preflight_package(repo)
    existing = binding(root, digest)
    rules = lifecycle_rules(repo)
    stage_names = [Path(a['folder']).name for a in agents]
    changes = []
    if existing is None:
        value = {'schema_version': 1, 'provider': PROVIDER, 'cli_version': VERSION,
                 'project_id': root.name, 'artifacts_root': ARTIFACTS.as_posix(),
                 'catalog_sha256': digest, 'methodology_revision_at_init': (source or {}).get('commit'),
                 'installation_source': {key: value for key, value in (source or {}).items() if key != 'path'},
                 'distribution_root': 'asdg', 'distribution_version': VERSION,
                 'installation_mode': 'embedded-distribution', 'initialized_at': timestamp, 'stages': stage_names}
        changes.append(plan(root, BINDING, json_bytes(value)))
    elif existing.get('stages') != stage_names:
        raise Conflict('Recorded stage layout differs; explicit migration required.')
    if read_bytes(safe_path(root, SPRINT)) is None:
        if existing is not None:
            raise Conflict('Existing sprint state is missing; do not silently recreate it.')
        changes.append(plan(root, SPRINT, json_bytes(INACTIVE)))
    else:
        read_state(root)
    if read_bytes(safe_path(root, LIFECYCLE)) is None:
        if existing is not None:
            raise Conflict('Existing lifecycle state is missing; do not silently recreate it.')
        state = {'schema_version': 1, 'project_status': project_state or 'new', 'release': None, 'stages': {}}
        changes.append(plan(root, LIFECYCLE, json_bytes(state)))
    else:
        state = read_lifecycle(root, rules)
        if project_state is not None and state.get('project_status') != project_state:
            raise Conflict('--project-status only declares initial state; existing state is preserved.')
    recorded, applied, notes = resolve_clients(root, client, existing is not None)
    for name in applied:  # Only the selected clients; another client's files are never planned here.
        for relative, data in client_files(root, repo, name):
            changes.append(plan(root, relative, data))
    bridge = claude_bridge(root) if 'claude' in applied else None
    if bridge is not None:
        target, data = bridge
        old_bridge = read_bytes(safe_path(root, target))
        if old_bridge is not None:
            changes.append(plan(root, Path('.asdg/backups') / f'CLAUDE-before-{sha(old_bridge)}.md', old_bridge, mode=0o600))
        changes.append(plan(root, target, data, replace=True))
    changes.append(plan(root, INTEGRATIONS, integrations_bytes(recorded), replace=True))
    old_agents = read_bytes(safe_path(root, 'AGENTS.md'))
    new_agents = merge_bootstrap(old_agents)
    if nonblank_source_lines(new_agents.decode()) > 50:
        raise Conflict('AGENTS.md would exceed 50 nonblank lines; shorten its project-owned guidance first.')
    if old_agents is not None and old_agents != new_agents:
        changes.append(plan(root, Path('.asdg/backups') / f'AGENTS-before-{sha(old_agents)}.md', old_agents, mode=0o600))
    changes.append(plan(root, 'AGENTS.md', new_agents, replace=True))
    old_ignore = read_bytes(safe_path(root, '.gitignore'))
    changes.append(plan(root, '.gitignore', merge_block(old_ignore, IGNORE, IGNORE_BEGIN, IGNORE_END, '.gitignore'), replace=True))
    if read_bytes(safe_path(root, 'logs/.gitkeep')) is None:
        changes.append(plan(root, 'logs/.gitkeep', b''))
    index = ARTIFACTS / 'README.md'
    if read_bytes(safe_path(root, index)) is None:
        text = '# Project documentation\n\nExplore the project from its purpose through design, delivery and learning.\n'
        text += 'These introductions explain each area; project evidence and decisions are added as work progresses.\n\n'
        text += '\n'.join(f"- [{Path(a['folder']).name.replace('-', ' ')}]({Path(a['folder']).name}/README.md)" for a in agents) + '\n'
        changes.append(plan(root, index, text.encode()))
    for agent in agents:
        folder = ARTIFACTS / Path(agent['folder']).name
        if read_bytes(safe_path(root, folder / 'README.md')) is None:
            changes.append(plan(root, folder / 'README.md', stage_readme(repo, folder.name)))
        if not folder.name.startswith('00-'):
            for name in STAGE_FOLDERS:
                destination = safe_path(root, folder / name)
                if not destination.exists() or not any(destination.iterdir()):
                    changes.append(plan(root, folder / name / '.gitkeep', b''))
    changes = [c for c in changes if c is not None]
    ledger_raw = read_bytes(safe_path(root, PROJECT_REVIEWS))
    if existing is not None and ledger_raw is None:
        raise Conflict('Existing document review history is missing; restore it before initialization.')
    ledger = json.loads(ledger_raw) if ledger_raw is not None else {'schema_version': 1, 'events': []}
    if not isinstance(ledger, dict) or ledger.get('schema_version') != 1 or not isinstance(ledger.get('events'), list):
        raise Conflict('Invalid document review history; nothing initialized.')
    records = [review_record(c.relative.as_posix(), c.before, c.after, timestamp, generator='asdg embedded init')
               for c in changes if c.relative.suffix == '.md']
    if records:
        ledger['events'].extend(records)
        change = plan(root, PROJECT_REVIEWS, json_bytes(ledger), replace=True)
        if change:
            changes.insert(0, change)
    return {'operation': 'init', 'project_root': str(root),
            'planned_files': [c.relative.as_posix() for c in changes], 'changed_files': [],
            'unchanged': not changes, 'sprint_started': False, 'human_approval': None,
            'clients_applied': applied, 'clients_recorded': sorted(recorded), 'notes': notes,
            'native_runtime_enforcement': 'NOT_VERIFIED'}, changes


def inspect(root, repo=REPO):
    from cli_status import lifecycle_rules, read_lifecycle, LIFECYCLE
    agents, digest = preflight_package(repo)
    value = binding(root, digest)
    missing = []
    if value is None:
        missing.append(BINDING.as_posix())
    sprint = None
    try:
        if read_bytes(safe_path(root, LIFECYCLE)) is None:
            raise Conflict('Missing .asdg/lifecycle.json')
        read_lifecycle(root, lifecycle_rules(repo))
        sprint = read_state(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        missing.append(str(exc))
    integrations, problems = client_report(root, repo, value is not None)
    missing.extend(problems)
    codex = integrations['codex']['status'] != 'NOT_SELECTED'
    body = read_bytes(safe_path(root, 'AGENTS.md'))
    if body is None or not bootstrap_is_current(body.decode('utf-8', 'replace')):
        missing.append('AGENTS.md: ASDG bootstrap block missing, edited or not first')
    ignore = read_bytes(safe_path(root, '.gitignore'))
    if ignore is None or IGNORE.encode() not in ignore:
        missing.append('.gitignore: log/cache exclusions')
    try:
        ledger = json.loads(read_bytes(safe_path(root, PROJECT_REVIEWS)) or b'{}')
        if ledger.get('schema_version') != 1 or not isinstance(ledger.get('events'), list):
            raise Conflict('Missing or invalid document review history')
    except (ValueError, TypeError, AttributeError) as exc:
        missing.append(str(exc))
    for relative in [ARTIFACTS / 'README.md'] + [ARTIFACTS / Path(a['folder']).name / 'README.md' for a in agents]:
        if read_bytes(safe_path(root, relative)) is None:
            missing.append(str(relative))
    for agent in agents[1:]:
        for name in STAGE_FOLDERS:
            relative = ARTIFACTS / Path(agent['folder']).name / name
            if not safe_path(root, relative).is_dir():
                missing.append(str(relative))
    if value is not None and value.get('stages') != [Path(a['folder']).name for a in agents]:
        missing.append('.asdg/project.json: stage mapping')
    return {'provider': PROVIDER, 'cli_version': VERSION, 'project_root': str(root),
            'initialized': value is not None, 'structure_ok': not missing, 'missing': missing,
            'semantic_compliance': 'NOT_ASSESSED', 'sprint_state': sprint, 'integrations': integrations,
            'implementation_enforcement': 'HOOK_TRUST_NOT_ASSESSED' if codex else 'NO_ASDG_GUARD_INSTALLED',
            'methodology_root': str(repo / 'asdg'), 'catalog_sha256': digest,
            'methodology_revision_now': None, 'methodology_revision_at_init': (value or {}).get('methodology_revision_at_init'),
            'distribution_version': VERSION, 'installation_mode': 'embedded-distribution',
            'runtime_contract': str(repo / 'asdg/00-governance/docs/runtime-contract.md'),
            'coordinator_entry': str(repo / 'asdg/00-governance/AGENTS.md'),
            'native_agent_registration': 'CONFIGURED_NOT_LIVE_VERIFIED' if codex else 'NOT_INSTALLED',
            'logging_hooks': 'CONFIGURED_NOT_LIVE_VERIFIED' if codex else 'NOT_INSTALLED'}
