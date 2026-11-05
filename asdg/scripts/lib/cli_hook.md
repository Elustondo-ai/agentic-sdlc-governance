# Tool-call guard

[Source: cli_hook.py](cli_hook.py)

Translates a proposed tool call into a documentation/read-only allowance or a check against the active implementation scope.

## Responsibilities and collaborators

Extracts every patch target, requires a READY governance bootstrap before any write, checks role ownership through cli_ownership before the independent sprint gate, checks remaining targets against implementation scope, and returns Codex hook denial JSON when validation fails.

![Codex tool payload → Target extraction + policy → Allow or denial JSON](images/cli_hook-flow.svg)

- [cli_status](cli_status.md): Provides authoritative facts and permission.
- [cli_files](cli_files.md): Validates paths used by read-only commands.

## Interface and data

ASDG_WRITE_CONTEXT supplies a session-bound role/workflow declaration; absent or mismatched context denies patch writes. Titles and tool-input role claims are ignored.
Input payload dict contains tool_name, tool_input and optional cwd. Patch tool_input.command contains apply_patch syntax; shell input contains command/cmd and optional workdir.

| Callable or interface | Contract |
| --- | --- |
| `documentation_target(root: Path, value: str) -> bool` | Accepts supported prose, visual, media, export and evidence formats under docs/; rejects traversal, policy names and links. Application source extensions are not documentation targets. |
| `implementation_decision(root: Path, paths: list[str], override: str \| None=None, context: dict \| None=None) -> tuple[bool, str]` | Denies every write with `BLOCKED: GOVERNANCE_BOOTSTRAP` and the missing sources when the default role cannot load; otherwise owned documentation and bounded utilities need no sprint or lifecycle state, while remaining targets use project status/sprint scope. |
| `shell_read_only(root: Path, cwd: Path, command: str) -> bool` | Returns whether a shell command matches the narrow supported read-only grammar; it is not a general shell analyzer. |
| `decision(root: Path, payload: dict) -> tuple[bool, str]` | Dispatches patch/shell/unknown payloads to validation and returns (allowed, reason). |
| `main(root: Path) -> int` | Reads one JSON payload from stdin, prints denial JSON when blocked and returns 0; exceptions fail closed. |

## Effects and failure behavior

Recognized read-only commands are allowed before the bootstrap check, so diagnosis stays possible while writes are blocked. Unknown tools and arbitrary shell programs are denied. Payload/input errors become denial responses. The process exit code alone does not indicate allowance; a deny response can accompany exit 0. Installed hooks still need runtime trust. Mixed patches pass only if every non-documentation target passes the sprint gate. File types and paths cannot prove that HTML, data or assets contain only documentation.

## Example

The installed scripts/hook.py calls main with its own repository root; payload data cannot choose that root.
