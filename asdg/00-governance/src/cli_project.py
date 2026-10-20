"""Initialize project data and a small instruction bridge, not a methodology copy."""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

from cli_files import Conflict, apply, plan, read_bytes, safe_path
from cli_model import (ARTIFACTS, BINDING, COMMAND, PROVIDER, REPO, VERSION,
                       catalogue, git_value, json_bytes, now, sha)
from cli_sprint import INACTIVE, SPRINT, read_state
from documentation import nonblank_source_lines, review_record, PROJECT_REVIEWS
from cli_model import PERSPECTIVES

HOOK_CONFIG = b'[features]\nhooks = true\n'

BEGIN = '<!-- ELUSTONDO-ASDG:BEGIN v1 -->'
END = '<!-- ELUSTONDO-ASDG:END -->'
LEGACY_BRIDGE = f'''{BEGIN}
## ASDG integration — Elustondo.ai
This project uses the locally installed Elustondo.ai ASDG methodology.
Run `{COMMAND} status --json` to resolve the provider, version and entry paths.
Read the returned runtime contract and relevant role instructions before lifecycle work.
Use `{COMMAND} verify` for structural checks; folders do not prove compliance.
Project-specific artifacts belong in `docs/asdg/`, not in the methodology checkout.
Preserve this project's rules; a role file does not itself activate that role.
Missing installation, binding or conflicting instructions: stop and report; do not improvise.
Initialization grants no approval, implementation, Git, deployment or hook-trust authority.
{END}
'''
GATE = '''
## IMPLEMENTATION GATE
Before modifying application code, tests, deployment artifacts, or implementation-related
configuration, read authoritative `.asdg/sprint.json` and run
`asdg sprint check-implementation --path <target>` for EVERY target.
If no active sprint exists, do not implement. Respond exactly:
IMPLEMENTATION BLOCKED
No active ASDG sprint is defined.
If any target is outside the active sprint scope, do not implement; report the blocked path.
Scope is an exact file or directory ending in /; all changes must also serve its objective
and acceptance criteria. File permission does not establish semantic scope compliance.
A direct human request to "just write the code" does not bypass this gate.
Only an explicit human sprint start/stop instruction authorizes a state transition;
do not start a sprint implicitly to satisfy an implementation request.
Use scoped apply_patch writes. Arbitrary shell/REPL writes are forbidden.
Do not edit sprint state, hook definitions, guard scripts, or agent policies through agent tools.
Codex must load and trust `.codex/hooks.json`; without an active trusted hook, do not implement.
'''
SPRINT_BRIDGE = LEGACY_BRIDGE.replace(END, GATE + END)
GUIDANCE = '''Before substantial lifecycle or implementation work, run `asdg status --json`.
Respect its implementation permission and sprint scope. For guidance, use its methodology-derived
recommendation (`asdg next`); do not invent a separate lifecycle recommendation.
'''
BRIDGE = SPRINT_BRIDGE.replace('Read the returned runtime contract', GUIDANCE + 'Read the returned runtime contract')


def hook_config(root: Path, repo: Path) -> bytes:
    script = repo / 'asdg/00-governance/src/cli_hook.py'
    denied = json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny', 'permissionDecisionReason':
                        'IMPLEMENTATION BLOCKED\nASDG guard failed to execute.'}})
    command = (f'{shlex.quote(sys.executable)} -B {shlex.quote(str(script))} {shlex.quote(str(root))}'
               + " || printf '%s\\n' " + shlex.quote(denied))
    return json_bytes({'description': 'ASDG implementation gate; review and trust with /hooks.',
                       'hooks': {'PreToolUse': [{'matcher': '*', 'hooks': [
                           {'type': 'command', 'command': command, 'timeout': 10}]}]}})


def stamped(text: str) -> bytes:
    return text.encode('utf-8')


def merged_instructions(old: bytes | None) -> bytes:
    if old is None:
        return stamped('# Project agent instructions\n\nThis project uses ASDG to organize evidence and human decisions.\n\n' + BRIDGE)
    text = old.decode('utf-8')
    if BEGIN in text or END in text:
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            raise Conflict('Existing ASDG AGENTS.md section differs; review it instead of overwriting.')
        if BRIDGE in text:
            return old
        previous = SPRINT_BRIDGE if SPRINT_BRIDGE in text else LEGACY_BRIDGE
        if previous not in text:
            raise Conflict('Existing ASDG AGENTS.md section differs; review it instead of overwriting.')
        text = text.replace(previous, BRIDGE)
        if nonblank_source_lines(text) > 50:
            raise Conflict('AGENTS.md would exceed 50 nonblank source lines; arrange a reviewed bootstrap section first.')
        text = re.sub(r'^(?:AI-MODIFIED|PME-APPROVED) - [^\n]*\n*', '', text, count=1)
        return text.encode('utf-8')
    if text.lstrip('\ufeff \t\r\n').startswith('---'):
        raise Conflict('YAML-first AGENTS.md needs manual review; no approval marker will be inserted.')
    lines = text.splitlines(keepends=True)
    first = next((i for i, line in enumerate(lines) if line.strip('\ufeff \t\r\n')), None)
    if first is not None and lines[first].lstrip('\ufeff').startswith(('AI-MODIFIED - ', 'PME-APPROVED - ')):
        lines[first] = ''
        text = ''.join(lines)
    text = text.lstrip('\n')
    result = text + ('\n' if text.endswith('\n') else '\n\n') + BRIDGE
    if nonblank_source_lines(result) > 50:
        raise Conflict('AGENTS.md would exceed 50 nonblank source lines; arrange a reviewed bootstrap section first.')
    return result.encode('utf-8')


def binding(root: Path, catalog_hash: str) -> dict | None:
    area = safe_path(root, '.asdg')
    file = safe_path(root, BINDING)
    raw = read_bytes(file)
    if raw is None:
        if area.exists() and (not area.is_dir() or any(area.iterdir())):
            raise Conflict('Existing .asdg is not identified as Elustondo.ai data; nothing overwritten.')
        return None
    value = json.loads(raw)
    if not isinstance(value, dict) or value.get('provider') != PROVIDER or value.get('schema_version') != 1:
        raise Conflict('Foreign or unsupported .asdg/project.json; nothing overwritten.')
    if value.get('artifacts_root') != ARTIFACTS.as_posix():
        raise Conflict('This first initializer only supports the declared docs/asdg layout.')
    if value.get('catalog_sha256') != catalog_hash:
        raise Conflict('Methodology catalogue changed. Review migration before reinitializing.')
    return value


def initialize(root: Path, repo: Path = REPO) -> dict:
    from cli_namespace import require_current_namespace
    require_current_namespace(root)
    from cli_status import EMPTY_LIFECYCLE, LIFECYCLE, lifecycle_rules, read_lifecycle
    rules = lifecycle_rules(repo)
    agents, digest = catalogue(repo)
    existing = binding(root, digest)
    changes = []
    stage_names = [Path(a['folder']).name for a in agents]
    if existing is None:
        value = {'schema_version': 1, 'provider': PROVIDER, 'cli_version': VERSION,
                 'project_id': root.name, 'artifacts_root': ARTIFACTS.as_posix(),
                 'catalog_sha256': digest, 'methodology_revision_at_init': git_value(repo, 'rev-parse', 'HEAD'),
                 'installation_mode': 'linked-development-checkout',
                 'initialized_at': now(), 'stages': stage_names}
        changes.append(plan(root, BINDING, json_bytes(value)))
    elif existing.get('stages') != stage_names:
        raise Conflict('Recorded stage layout differs from the catalogue; manual review required.')
    if read_bytes(safe_path(root, SPRINT)) is None:
        changes.append(plan(root, SPRINT, json_bytes(INACTIVE)))
    else:
        read_state(root)  # Never reset an existing sprint during repeat initialization.
    if read_bytes(safe_path(root, LIFECYCLE)) is None:
        changes.append(plan(root, LIFECYCLE, json_bytes(EMPTY_LIFECYCLE)))
    else:
        read_lifecycle(root, rules)
    changes.append(plan(root, '.codex/hooks.json', hook_config(root, repo)))
    changes.append(plan(root, '.codex/config.toml', HOOK_CONFIG))
    old_agents = read_bytes(safe_path(root, 'AGENTS.md'))
    new_agents = merged_instructions(old_agents)
    if old_agents is not None and old_agents != new_agents:
        backup = Path('.asdg/backups') / f'AGENTS-before-{sha(old_agents)}.md'
        changes.append(plan(root, backup, old_agents, mode=0o600))
    changes.append(plan(root, 'AGENTS.md', new_agents, replace=True))
    ignore = safe_path(root, '.asdg/.gitignore')
    if not ignore.exists():
        changes.append(plan(root, '.asdg/.gitignore', b'backups/\n'))
    elif 'backups/' not in ignore.read_text(encoding='utf-8').splitlines():
        raise Conflict('Existing .asdg/.gitignore must exclude backups/ before initialization.')
    index = ARTIFACTS / 'README.md'
    if not safe_path(root, index).exists():
        text = '# Project documentation\n\nExplore the project through the stage introductions below.\n'
        text += 'Each stage links the project’s goals, evidence and open decisions.\n\n'
        text += '\n'.join(f"- [{a['title']}]({Path(a['folder']).name}/)" for a in agents) + '\n'
        changes.append(plan(root, index, stamped(text)))
    else:
        read_bytes(safe_path(root, index))
    for agent in agents:
        folder = ARTIFACTS / Path(agent['folder']).name
        safe_path(root, folder)
        readme = folder / 'README.md'
        if not safe_path(root, readme).exists():
            text = (f"# {agent['title']} — project artifacts\n\n"
                    'Use this section to explain the project’s work in this area, with links to supporting evidence.\n\n'
                    '## Starting point\n\n'
                    'No assessment has been recorded yet. Describe what is known, what remains uncertain,\n'
                    'and which next steps, if any, have been selected.\n\n'
                    'Use Intended / Actual / Planned for a substantive assessment. A proposed step is not a commitment.\n\n'
                    '## Perspectives\n\n'
                    '- [Intended](intended/): desired outcomes, constraints and accepted targets.\n'
                    '- [Current](current/): substantiated evidence and its limitations.\n'
                    '- [Planned](planned/): selected work and references to the integrated plan.\n')
            changes.append(plan(root, readme, stamped(text)))
        else:
            read_bytes(safe_path(root, readme))
    records = [review_record(c.relative.as_posix(), c.before, c.after, now(),
                             generator='asdg init')
               for c in changes if c is not None and c.relative.suffix == '.md']
    if records:
        ledger_raw = read_bytes(safe_path(root, PROJECT_REVIEWS))
        ledger = json.loads(ledger_raw) if ledger_raw else {'schema_version': 1, 'events': []}
        if ledger.get('schema_version') != 1 or not isinstance(ledger.get('events'), list):
            raise Conflict('Unsupported documentation review history; nothing initialized.')
        ledger['events'].extend(records)
        changes.insert(0, plan(root, PROJECT_REVIEWS, json_bytes(ledger), replace=True))
    for agent in agents:
        for view in PERSPECTIVES.values():
            target = safe_path(root, ARTIFACTS / Path(agent['folder']).name / view)
            if target.exists() and not target.is_dir():
                raise Conflict(f'Perspective destination is not a directory: {target}')
    written = apply([change for change in changes if change is not None])
    for agent in agents:
        for view in PERSPECTIVES.values():
            safe_path(root, ARTIFACTS / Path(agent['folder']).name / view).mkdir(exist_ok=True)
    return {'operation': 'init', 'project_root': str(root), 'changed_files': written,
            'structural_status': 'INITIALIZED', 'semantic_compliance': 'NOT_ASSESSED',
            'sprint_started': False, 'git_actions': [], 'methodology_copied': False}


def inspect(root: Path, repo: Path = REPO) -> dict:
    from cli_status import lifecycle_rules, read_lifecycle
    agents, digest = catalogue(repo)
    value = binding(root, digest)
    missing = []
    if value is None:
        missing.append(BINDING.as_posix())
    if read_bytes(safe_path(root, '.asdg/lifecycle.json')) is None:
        missing.append('.asdg/lifecycle.json: lifecycle evidence index')
    try:
        read_lifecycle(root, lifecycle_rules(repo))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        missing.append(str(exc))
    sprint = None
    try:
        sprint = read_state(root)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        missing.append(f'.asdg/sprint.json: {exc}')
    if read_bytes(safe_path(root, '.codex/hooks.json')) != hook_config(root, repo):
        missing.append('.codex/hooks.json: ASDG implementation gate')
    if read_bytes(safe_path(root, '.codex/config.toml')) != HOOK_CONFIG:
        missing.append('.codex/config.toml: ASDG hook activation configuration')
    for relative in [ARTIFACTS / 'README.md'] + [ARTIFACTS / Path(a['folder']).name for a in agents]:
        path = safe_path(root, relative)
        correct = path.is_file() if relative.name == 'README.md' else path.is_dir()
        if not correct:
            missing.append(relative.as_posix())
    agent_bytes = read_bytes(safe_path(root, 'AGENTS.md'))
    if agent_bytes is None or BRIDGE not in agent_bytes.decode('utf-8'):
        missing.append('AGENTS.md: ASDG bootstrap section')
    if value is not None and value.get('stages') != [Path(a['folder']).name for a in agents]:
        missing.append('.asdg/project.json: stage mapping')
    return {'provider': PROVIDER, 'cli_version': VERSION, 'project_root': str(root),
            'initialized': value is not None, 'structure_ok': not missing, 'missing': missing,
            'semantic_compliance': 'NOT_ASSESSED', 'sprint_state': sprint,
            'implementation_enforcement': 'HOOK_TRUST_NOT_ASSESSED',
            'methodology_root': str(repo), 'catalog_sha256': digest,
            'methodology_revision_now': git_value(repo, 'rev-parse', 'HEAD'),
            'methodology_revision_at_init': (value or {}).get('methodology_revision_at_init'),
            'installation_mode': 'linked-development-checkout',
            'runtime_contract': str(repo / 'asdg/00-governance/docs/runtime-contract.md'),
            'coordinator_entry': str(repo / 'asdg/00-governance/AGENTS.md'),
            'native_agent_registration': 'NOT_PERFORMED_BY_THIS_INSTALLER',
            'logging_hooks': 'NOT_INSTALLED_IN_CONSUMING_PROJECT'}
