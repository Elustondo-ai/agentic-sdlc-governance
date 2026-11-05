"""Best-effort role write ownership; independent of sprint authorization."""
from __future__ import annotations

from pathlib import Path
from cli_files import Conflict, safe_path
from cli_model import REPO, catalogue


def local_path(root: Path, value: str) -> Path:
    """Normalize one literal file target without following links or traversal."""
    if not isinstance(value, str) or not value or value != value.strip() or any(c in value for c in '\\*?[]\n\r'):
        raise Conflict('Write target must be a literal local file.')
    path = Path(value)
    if path.is_absolute():
        path = path.relative_to(root)
    if not path.parts or '..' in path.parts:
        raise Conflict('Write target escapes the project.')
    safe_path(root, path)
    return path


def owned_directory(role: str, repo: Path = REPO) -> Path | None:
    """Derive every project-role destination from the canonical catalogue."""
    for row in catalogue(repo)[0]:
        if row['role_id'] == role:
            return Path('docs/asdg') / Path(row['folder']).name
    return None


def ownership_decision(root: Path, paths: list[str], context: dict, repo: Path = REPO) -> tuple[bool, str, list[str]]:
    """Return allow/reason/application targets; caller separately checks sprint scope.

    Context is a declaration from the conversation (CLI) or session-bound harness
    (hook), never authentication. Exception targets are exact, task-authorized files.
    """
    role = context.get('role_id')
    owner = owned_directory(role, repo)
    if owner is None and role != 'ASDG-ADMIN':
        return False, 'WRITE BLOCKED: unknown role identity; reload or reaffirm the role.', []
    if not paths:
        return False, 'WRITE BLOCKED: specify every target.', []
    workflow = context.get('workflow')
    exceptions = {local_path(root, p) for p in context.get('targets', [])}
    application = []
    for value in paths:
        path = local_path(root, value)
        # Policy/control paths are never application or ordinary documentation.
        protected = any(p in {'.git', '.codex', '.claude', '.agents', 'AGENTS.md', 'SKILL.md'} for p in path.parts)
        if role == 'ASDG-ADMIN' and workflow == 'admin' and path in exceptions:
            if '.git' not in path.parts and (path.parts[0] in {'asdg', 'scripts', 'bin'} or str(path) in {'AGENTS.md', 'README.md'} or (path.parts[:3] == ('docs', 'asdg', '07-planning') and path.name.startswith('02.') and path.suffix in {'.md', '.json'})):
                continue
        if protected or path.parts[0] == 'asdg':
            return False, f'WRITE BLOCKED: protected methodology/control target {path}.', []
        if path == Path('.asdg/document-reviews.json') and workflow == 'review-receipt':
            continue  # Append-only authorship; semantic validation remains in the workflow.
        if path in exceptions:
            if workflow in {'approve', 'purpose-review'} and path == Path('.asdg/lifecycle.json'):
                if workflow == 'approve' or role == 'ASDG-02':
                    continue
            if workflow in {'sprint-start', 'sprint-close'} and path == Path('.asdg/sprint.json'):
                continue
            if workflow == 'sprint-close' and path.parent == Path('.asdg/sprint-closeouts') and path.suffix == '.json':
                from uuid import UUID
                UUID(path.stem)
                continue
            if workflow == 'shared-record' and role == 'ASDG-COORDINATOR' and path.parts[:2] == ('docs', 'shared'):
                continue
        if path.parts[0] == '.asdg':
            return False, f'WRITE BLOCKED: shared state requires its explicit utility: {path}.', []
        if role == 'ASDG-08' and workflow == 'openspec' and path in exceptions:
            store = local_path(root, context.get('openspec_store', ''))
            # Never let a declared store override specialist or control ownership.
            if store.parts[0] not in {'docs', 'asdg', '.asdg', '.git', '.codex', '.claude', '.agents'} and store in path.parents:
                continue
        if owner is not None and owner in path.parents:
            from cli_hook import documentation_target
            if documentation_target(root, str(path)):
                continue
        if role == 'ASDG-09' and owner in path.parents:
            application.append(str(path))
            continue
        if path.parts[:2] == ('docs', 'asdg'):
            return False, f'OUT_OF_SCOPE: {path}; save a proposal in {owner or "the authorized Admin record"} or return a handoff to its owner.', []
        if role == 'ASDG-09' and path.parts[0] not in {'.asdg', 'asdg'}:
            application.append(str(path))
            continue
        return False, f'OUT_OF_SCOPE: {path}; propose the change in {owner or "the authorized Admin record"} or return a handoff.', []
    return True, 'Role ownership checked; workflow authorization and content obligations still apply.', application
