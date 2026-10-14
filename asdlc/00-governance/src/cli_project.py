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

HOOK_CONFIG = b'[features]\nhooks = true\n'

BEGIN = '<!-- ELUSTONDO-ASDLC:BEGIN v1 -->'
END = '<!-- ELUSTONDO-ASDLC:END -->'
LEGACY_BRIDGE = f'''{BEGIN}
## ASDLC integration — Elustondo.ai
This project uses the locally installed Elustondo.ai ASDLC methodology.
Run `{COMMAND} status --json` to resolve the provider, version and entry paths.
Read the returned runtime contract and relevant role instructions before lifecycle work.
Use `{COMMAND} verify` for structural checks; folders do not prove compliance.
Project-specific artifacts belong in `docs/asdlc/`, not in the methodology checkout.
Preserve this project's rules; a role file does not itself activate that role.
Missing installation, binding or conflicting instructions: stop and report; do not improvise.
Initialization grants no approval, implementation, Git, deployment or hook-trust authority.
{END}
'''
GATE = '''
## IMPLEMENTATION GATE
Before modifying application code, tests, deployment artifacts, or implementation-related
configuration, read authoritative `.asdlc/sprint.json` and run
`asdg sprint check-implementation --path <target>` for EVERY target.
If no active sprint exists, do not implement. Respond exactly:
IMPLEMENTATION BLOCKED
No active ASDLC sprint is defined.
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
    script = repo / 'asdlc/00-governance/src/cli_hook.py'
    denied = json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny', 'permissionDecisionReason':
                        'IMPLEMENTATION BLOCKED\nASDLC guard failed to execute.'}})
    command = (f'{shlex.quote(sys.executable)} -B {shlex.quote(str(script))} {shlex.quote(str(root))}'
               + " || printf '%s\\n' " + shlex.quote(denied))
    return json_bytes({'description': 'ASDLC implementation gate; review and trust with /hooks.',
                       'hooks': {'PreToolUse': [{'matcher': '*', 'hooks': [
                           {'type': 'command', 'command': command, 'timeout': 10}]}]}})


def stamped(text: str) -> bytes:
    return (f'AI-MODIFIED - {now()}\n\n' + text).encode('utf-8')


def merged_instructions(old: bytes | None) -> bytes:
    if old is None:
        return stamped('# Project agent instructions\n\n' + BRIDGE)
    text = old.decode('utf-8')
    if BEGIN in text or END in text:
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            raise Conflict('Existing ASDLC AGENTS.md section differs; review it instead of overwriting.')
        if BRIDGE in text:
            return old
        previous = SPRINT_BRIDGE if SPRINT_BRIDGE in text else LEGACY_BRIDGE
        if previous not in text:
            raise Conflict('Existing ASDLC AGENTS.md section differs; review it instead of overwriting.')
        text = text.replace(previous, BRIDGE)
        if len(text.splitlines()) > 50:
            raise Conflict('AGENTS.md would exceed 50 lines; arrange a reviewed bootstrap section first.')
        text = re.sub(r'^AI-MODIFIED - [^|\n]+', f'AI-MODIFIED - {now()} ', text, count=1)
        return text.encode('utf-8')
    if text.lstrip('\ufeff \t\r\n').startswith('---'):
        raise Conflict('YAML-first AGENTS.md needs manual review; no approval marker will be inserted.')
    lines = text.splitlines(keepends=True)
    first = next((i for i, line in enumerate(lines) if line.strip('\ufeff \t\r\n')), None)
    status = f'AI-MODIFIED - {now()}'
    if first is not None and lines[first].lstrip('\ufeff').startswith(('AI-MODIFIED - ', 'PME-APPROVED - ')):
        approved = re.search(r'PME-APPROVED - [^|\r\n]+', lines[first])
        if approved:
            status += ' | ' + approved.group(0).strip()
        lines[first] = status + '\n'
        text = ''.join(lines)
    else:
        text = status + '\n\n' + text
    result = text + ('\n' if text.endswith('\n') else '\n\n') + BRIDGE
    if len(result.splitlines()) > 50:
        raise Conflict('AGENTS.md would exceed 50 lines; arrange a reviewed bootstrap section first.')
    return result.encode('utf-8')


def binding(root: Path, catalog_hash: str) -> dict | None:
    area = safe_path(root, '.asdlc')
    file = safe_path(root, BINDING)
    raw = read_bytes(file)
    if raw is None:
        if area.exists() and (not area.is_dir() or any(area.iterdir())):
            raise Conflict('Existing .asdlc is not identified as Elustondo.ai data; nothing overwritten.')
        return None
    value = json.loads(raw)
    if not isinstance(value, dict) or value.get('provider') != PROVIDER or value.get('schema_version') != 1:
        raise Conflict('Foreign or unsupported .asdlc/project.json; nothing overwritten.')
    if value.get('artifacts_root') != ARTIFACTS.as_posix():
        raise Conflict('This first initializer only supports the declared docs/asdlc layout.')
    if value.get('catalog_sha256') != catalog_hash:
        raise Conflict('Methodology catalogue changed. Review migration before reinitializing.')
    return value


def initialize(root: Path, repo: Path = REPO) -> dict:
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
        backup = Path('.asdlc/backups') / f'AGENTS-before-{sha(old_agents)}.md'
        changes.append(plan(root, backup, old_agents, mode=0o600))
    changes.append(plan(root, 'AGENTS.md', new_agents, replace=True))
    ignore = safe_path(root, '.asdlc/.gitignore')
    if not ignore.exists():
        changes.append(plan(root, '.asdlc/.gitignore', b'backups/\n'))
    elif 'backups/' not in ignore.read_text(encoding='utf-8').splitlines():
        raise Conflict('Existing .asdlc/.gitignore must exclude backups/ before initialization.')
    index = ARTIFACTS / 'README.md'
    if not safe_path(root, index).exists():
        text = '# Project ASDLC artifacts\n\nInitialization is structural only; no stage is approved or complete.\n'
        text += 'Governance, roles and skills remain in the installed methodology.\n\n'
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
                    'Status: NOT ASSESSED. This folder alone does not complete the stage.\n\n'
                    'Keep this project\'s content and evidence here.\n'
                    'Do not copy methodology agent definitions or skills here.\n')
            changes.append(plan(root, readme, stamped(text)))
        else:
            read_bytes(safe_path(root, readme))
    written = apply([change for change in changes if change is not None])
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
    if read_bytes(safe_path(root, '.asdlc/lifecycle.json')) is None:
        missing.append('.asdlc/lifecycle.json: lifecycle evidence index')
    try:
        read_lifecycle(root, lifecycle_rules(repo))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        missing.append(str(exc))
    sprint = None
    try:
        sprint = read_state(root)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        missing.append(f'.asdlc/sprint.json: {exc}')
    if read_bytes(safe_path(root, '.codex/hooks.json')) != hook_config(root, repo):
        missing.append('.codex/hooks.json: ASDLC implementation gate')
    if read_bytes(safe_path(root, '.codex/config.toml')) != HOOK_CONFIG:
        missing.append('.codex/config.toml: ASDLC hook activation configuration')
    for relative in [ARTIFACTS / 'README.md'] + [ARTIFACTS / Path(a['folder']).name for a in agents]:
        path = safe_path(root, relative)
        correct = path.is_file() if relative.name == 'README.md' else path.is_dir()
        if not correct:
            missing.append(relative.as_posix())
    agent_bytes = read_bytes(safe_path(root, 'AGENTS.md'))
    if agent_bytes is None or BRIDGE not in agent_bytes.decode('utf-8'):
        missing.append('AGENTS.md: ASDLC bootstrap section')
    if value is not None and value.get('stages') != [Path(a['folder']).name for a in agents]:
        missing.append('.asdlc/project.json: stage mapping')
    return {'provider': PROVIDER, 'cli_version': VERSION, 'project_root': str(root),
            'initialized': value is not None, 'structure_ok': not missing, 'missing': missing,
            'semantic_compliance': 'NOT_ASSESSED', 'sprint_state': sprint,
            'implementation_enforcement': 'HOOK_TRUST_NOT_ASSESSED',
            'methodology_root': str(repo), 'catalog_sha256': digest,
            'methodology_revision_now': git_value(repo, 'rev-parse', 'HEAD'),
            'methodology_revision_at_init': (value or {}).get('methodology_revision_at_init'),
            'installation_mode': 'linked-development-checkout',
            'runtime_contract': str(repo / 'asdlc/00-governance/docs/runtime-contract.md'),
            'coordinator_entry': str(repo / 'asdlc/00-governance/AGENTS.md'),
            'native_agent_registration': 'NOT_PERFORMED_BY_THIS_INSTALLER',
            'logging_hooks': 'NOT_INSTALLED_IN_CONSUMING_PROJECT'}
