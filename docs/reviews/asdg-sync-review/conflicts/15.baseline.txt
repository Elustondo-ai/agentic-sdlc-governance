"""Preflight one embedded distribution and preserve client-owned state."""
from __future__ import annotations
import json
import re
import shlex
from pathlib import Path
from cli_files import Conflict, apply, plan, read_bytes, safe_path
from cli_model import ARTIFACTS, BINDING, PROVIDER, REPO, VERSION, catalogue, json_bytes, now, sha
from cli_sprint import INACTIVE, SPRINT, read_state
from documentation import nonblank_source_lines, review_record, PROJECT_REVIEWS

HOOK_CONFIG = b'[features]\nhooks = true\n'
BEGIN, END = '<!-- ASDG:BEGIN embedded-v1 -->', '<!-- ASDG:END -->'
BRIDGE = f'''{BEGIN}
## ASDG integration
This client carries its own methodology in `asdg/`; read `asdg/AGENTS.md`.
Read `asdg/skills/asdg-focus/session-policy.md` on each turn.
Before substantial work run `python3 asdg/scripts/cli.py status --json` from the client root.
Use `python3 asdg/scripts/cli.py verify` for structure; folders do not prove compliance.
Use this local entry point; a machine-wide `asdg` may resolve an older installation.
Client evidence belongs in `docs/asdg/`; methodology definitions are not client evidence.
Preserve `.asdg/` state and review history; disposable activity logs belong under `logs/`.
Explicit Focus selection affects this conversation only; reading a role never activates it.
No specialist is active merely because this repository was initialized.
## Implementation gate
Before application edits, inspect `.asdg/sprint.json` and check EVERY target with
`python3 asdg/scripts/cli.py sprint check-implementation --path <target>`.
Without an active scoped sprint, report IMPLEMENTATION BLOCKED and do not implement.
Scope is an exact file or a directory ending in /; satisfy its objective and acceptance criteria.
Only an explicit human sprint start/stop decision authorizes a transition; never infer one.
Use scoped apply_patch edits. Arbitrary shell/REPL writes remain blocked by the guard.
Do not edit state, hook definitions or ASDG policies as part of application implementation.
Review and trust project hooks in Codex; configuration alone does not establish enforcement.
All current named roles retain read-only evaluation; an active sprint does not widen their roles.
Installation grants no approval, publication, commit, push, deployment or hook trust.
{END}
'''
IGNORE_BEGIN, IGNORE_END = '# ASDG generated files: BEGIN', '# ASDG generated files: END'
IGNORE = f'{IGNORE_BEGIN}\n/logs/\n/asdg/**/__pycache__/\n/asdg/**/*.pyc\n/.asdg/backups/\n/.asdg/cache/\n{IGNORE_END}\n'


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
    if name == 'AGENTS.md':
        if 'ELUSTONDO-ASDG:BEGIN' in text or 'ELUSTONDO-ASDLC:BEGIN' in text:
            raise Conflict('Linked/legacy AGENTS.md integration requires explicit migration.')
        if text.lstrip('\ufeff \t\r\n').startswith('---'):
            raise Conflict('YAML-first AGENTS.md requires manual review; nothing overwritten.')
        # The old bytes and declarations are retained in the hash-bound review ledger.
        # Do not display an old approval as if it governed the newly extended file.
        text = re.sub(r'\A(?:\ufeff)?\s*(?:AI-MODIFIED|PME-APPROVED) - [^\n]*\n*', '', text, count=1)
    return (text + ('\n' if text.endswith('\n') else '\n\n') + block).encode()


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


def preflight_package(repo):
    distribution(repo)
    agents, digest = catalogue(repo)
    from cli_status import lifecycle_rules
    lifecycle_rules(repo)
    for name in ('asdg/AGENTS.md', 'asdg/scripts/cli.py', 'asdg/scripts/hook.py', 'asdg/skills/asdg-focus/session-policy.md'):
        if read_bytes(safe_path(repo, name)) is None:
            raise Conflict(f'Missing packaged input: {name}')
    for agent in agents:
        for key in ('entry', 'skill'):
            if read_bytes(safe_path(repo, agent[key])) is None:
                raise Conflict(f'Missing role input: {agent[key]}')
        if read_bytes(safe_path(repo, Path('asdg/templates') / agent['adapter'])) is None:
            raise Conflict(f'Missing role adapter: {agent["native_name"]}')
    if len(list(safe_path(repo, 'asdg/templates/.agents/skills').glob('asdg-focus-*/SKILL.md'))) != 12:
        raise Conflict('Expected twelve packaged focus adapters.')
    return agents, digest


def initialize(root, repo=REPO, project_state=None, dry_run=False):
    from cli_status import LIFECYCLE, PROJECT_STATUSES, lifecycle_rules, read_lifecycle
    if root.resolve() != repo.resolve():
        raise Conflict('Embedded initialization must use this client repository.')
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
                 'catalog_sha256': digest, 'methodology_revision_at_init': None,
                 'distribution_root': 'asdg', 'distribution_version': VERSION,
                 'installation_mode': 'embedded-distribution', 'initialized_at': now(), 'stages': stage_names}
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
    changes.extend([plan(root, '.codex/hooks.json', hook_config(root, repo)),
                    plan(root, '.codex/config.toml', HOOK_CONFIG)])
    for relative, data in template_files(repo):
        changes.append(plan(root, relative, data))
    old_agents = read_bytes(safe_path(root, 'AGENTS.md'))
    new_agents = merge_block(old_agents, BRIDGE, BEGIN, END, 'AGENTS.md')
    if nonblank_source_lines(new_agents.decode()) > 50:
        raise Conflict('AGENTS.md would exceed 50 nonblank lines; arrange a reviewed shorter bridge first.')
    if old_agents is not None and old_agents != new_agents:
        changes.append(plan(root, Path('.asdg/backups') / f'AGENTS-before-{sha(old_agents)}.md', old_agents, mode=0o600))
    changes.append(plan(root, 'AGENTS.md', new_agents, replace=True))
    old_ignore = read_bytes(safe_path(root, '.gitignore'))
    changes.append(plan(root, '.gitignore', merge_block(old_ignore, IGNORE, IGNORE_BEGIN, IGNORE_END, '.gitignore'), replace=True))
    if read_bytes(safe_path(root, 'logs/.gitkeep')) is None:
        changes.append(plan(root, 'logs/.gitkeep', b''))
    index = ARTIFACTS / 'README.md'
    if read_bytes(safe_path(root, index)) is None:
        text = '# Project evidence\n\nRead the existing application before reconstructing its documentation.\n'
        text += 'Empty scaffolds, recorded evidence and human acceptance are distinct.\n\n'
        text += '\n'.join(f"- [{a['title']}]({Path(a['folder']).name}/README.md)" for a in agents) + '\n'
        changes.append(plan(root, index, text.encode()))
    for agent in agents:
        folder = ARTIFACTS / Path(agent['folder']).name
        if read_bytes(safe_path(root, folder / 'README.md')) is None:
            text = f"# {agent['title']} — project evidence\n\nNo assessment has been recorded here yet.\n\n"
            text += 'Use Intended / Actual / Planned; preserve sources, uncertainties and human decisions.\n'
            text += 'Intended: desired outcomes and constraints. Actual: substantiated current evidence.\n'
            text += 'Planned: selected next work, linked to the integrated Stage 07 plan.\n'
            changes.append(plan(root, folder / 'README.md', text.encode()))
    changes = [c for c in changes if c is not None]
    ledger_raw = read_bytes(safe_path(root, PROJECT_REVIEWS))
    if existing is not None and ledger_raw is None:
        raise Conflict('Existing document review history is missing; restore it before initialization.')
    ledger = json.loads(ledger_raw) if ledger_raw is not None else {'schema_version': 1, 'events': []}
    if not isinstance(ledger, dict) or ledger.get('schema_version') != 1 or not isinstance(ledger.get('events'), list):
        raise Conflict('Invalid document review history; nothing initialized.')
    records = [review_record(c.relative.as_posix(), c.before, c.after, now(), generator='asdg embedded init')
               for c in changes if c.relative.suffix == '.md']
    if records:
        ledger['events'].extend(records)
        change = plan(root, PROJECT_REVIEWS, json_bytes(ledger), replace=True)
        if change:
            changes.insert(0, change)
    written = [] if dry_run else apply(changes)
    return {'operation': 'init', 'project_root': str(root), 'dry_run': dry_run,
            'planned_files': [c.relative.as_posix() for c in changes], 'changed_files': written,
            'unchanged': not changes, 'sprint_started': False, 'human_approval': None,
            'native_runtime_enforcement': 'NOT_VERIFIED'}


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
    expected = [('.codex/hooks.json', hook_config(root, repo)), ('.codex/config.toml', HOOK_CONFIG)]
    expected.extend(template_files(repo))
    for relative, data in expected:
        if read_bytes(safe_path(root, relative)) != data:
            missing.append(f'{relative}: missing or locally modified integration')
    body = read_bytes(safe_path(root, 'AGENTS.md'))
    if body is None or BRIDGE.encode() not in body:
        missing.append('AGENTS.md: ASDG bootstrap section')
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
    if value is not None and value.get('stages') != [Path(a['folder']).name for a in agents]:
        missing.append('.asdg/project.json: stage mapping')
    return {'provider': PROVIDER, 'cli_version': VERSION, 'project_root': str(root),
            'initialized': value is not None, 'structure_ok': not missing, 'missing': missing,
            'semantic_compliance': 'NOT_ASSESSED', 'sprint_state': sprint,
            'implementation_enforcement': 'HOOK_TRUST_NOT_ASSESSED',
            'methodology_root': str(repo / 'asdg'), 'catalog_sha256': digest,
            'methodology_revision_now': None, 'methodology_revision_at_init': (value or {}).get('methodology_revision_at_init'),
            'distribution_version': VERSION, 'installation_mode': 'embedded-distribution',
            'runtime_contract': str(repo / 'asdg/00-governance/docs/runtime-contract.md'),
            'coordinator_entry': str(repo / 'asdg/00-governance/AGENTS.md'),
            'native_agent_registration': 'CONFIGURED_NOT_LIVE_VERIFIED',
            'logging_hooks': 'CONFIGURED_NOT_LIVE_VERIFIED'}
