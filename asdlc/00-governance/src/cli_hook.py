"""Codex PreToolUse boundary: scoped patches; conservative read-only shell access."""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

from cli_files import safe_path
from cli_status import project_status


def implementation_decision(root: Path, paths: list[str], override: str | None = None) -> tuple[bool, str]:
    status = project_status(root, requested_paths=paths)
    permission = status['implementation']
    if permission['allowed'] is True:
        return True, permission['reason']
    reason = permission['reason']
    if override and reason == 'Specify every implementation target with --path.':
        reason = override
    return False, reason + '\n\nRecommended next action:\n' + status['recommendation']['action']


def shell_read_only(root: Path, cwd: Path, command: str) -> bool:
    # Do not try to infer write targets from arbitrary shell programs.
    if any(c in command for c in '\n\r;&|<>`$'):
        return False
    words = shlex.split(command)
    if words in (['pwd'], ['git', 'status', '--short'], ['git', 'status'],
                 ['rg', '--files'], ['rg', '--files', '--hidden']):
        return True
    if words and words[0] == 'ls' and all(word in ('-l', '-a', '-la', '-al') for word in words[1:]):
        return True
    if words and words[0] == 'cat' and len(words) > 1:
        for word in words[1:]:
            if word.startswith('-'):
                return False
            path = Path(word) if Path(word).is_absolute() else cwd / word
            safe_path(root, path.relative_to(root))
        return True
    if words and words[0] in ('asdg', 'elustondo-asdlc'):
        if words[1:] in (['status'], ['status', '--json'], ['next'], ['next', '--json'], ['verify'], ['verify', '--json']):
            return True
    if len(words) >= 3 and words[0] in ('asdg', 'elustondo-asdlc') and words[1] == 'sprint':
        if words[2:] in (['status'], ['status', '--json']):
            return True
        if words[2] == 'check-implementation':
            rest = words[3:]
            return len(rest) % 2 == 0 and all(rest[i] == '--path' for i in range(0, len(rest), 2))
    return False


def decision(root: Path, payload: dict) -> tuple[bool, str]:
    tool = payload.get('tool_name')
    data = payload.get('tool_input')
    if not isinstance(data, dict):
        return False, 'Unsupported tool input; cannot validate implementation targets.'
    if tool == 'apply_patch':
        command = data.get('command', '')
        if not isinstance(command, str):
            return False, 'Invalid patch input.'
        paths = re.findall(r'^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$', command, re.MULTILINE)
        cwd = Path(payload.get('cwd', str(root))).resolve()
        targets = [str(Path(path) if Path(path).is_absolute() else cwd / path) for path in paths]
        return implementation_decision(root, targets)
    if tool in ('Bash', 'exec_command', 'shell_command'):
        command = data.get('command', data.get('cmd', ''))
        cwd = Path(data.get('workdir') or payload.get('cwd') or root).resolve()
        cwd.relative_to(root)
        if isinstance(command, str) and shell_read_only(root, cwd, command):
            return True, 'Read-only command.'
        return implementation_decision(root, [], 'Arbitrary shell execution is blocked. Use a scoped apply_patch for implementation; run sprint start/stop in a human terminal.')
    # Unknown/MCP/REPL tools can write through other channels. Deny by default.
    return implementation_decision(root, [], 'Tool has no validated write boundary; implementation access is denied.')


def main(root: Path) -> int:
    try:
        allowed, reason = decision(root.resolve(strict=True), json.load(sys.stdin))
    except Exception as exc:
        allowed, reason = False, f'Guard could not validate tool call: {exc}'
    if allowed:
        return 0
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
          'permissionDecision': 'deny', 'permissionDecisionReason': 'IMPLEMENTATION BLOCKED\n' + reason}}))
    return 0


if __name__ == '__main__':
    sys.exit(main(Path(sys.argv[1])))
