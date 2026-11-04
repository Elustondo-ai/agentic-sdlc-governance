# Optional coordinator advice

[Source: cli_advice.py](cli_advice.py)

Asks the Codex runtime for one bounded, read-only recommendation based on an already evaluated project snapshot.

## Responsibilities and collaborators

Owns the advice prompt/schema, runtime restrictions, response validation, timeout handling and concise console rendering.

![Status snapshot + canonical instructions → Read-only Codex turn → Validated advice or unavailable reason](images/cli_advice-flow.svg)

- [cli_model](cli_model.md): Resolves coordinator identity.
- [cli_runtime_env](cli_runtime_env.md): Restricts inherited environment.
- [cli_files](cli_files.md): Validates instruction paths.

## Interface and data

Advice is status:available plus summary/action/reason/evidence/questions/uncertainties/requirements and runtime metadata, or status:unavailable with reason. AdviceUnavailable is an adapter-owned RuntimeError. SCHEMA/FIELDS define bounded JSON; SDK_VERSION pins 0.163.0.

| Callable or interface | Contract |
| --- | --- |
| `turn_failure(result) -> str` | Extracts allowlisted public error categories from a turn result without echoing raw provider messages. |
| `build_prompt(root: Path, status: dict, repo: Path=REPO) -> str` | Returns a prompt referencing canonical sources and project facts; raises when required context files are missing. |
| `validate_advice(raw: str) -> dict` | Parses raw JSON and checks fields, bounds and concise summary rules; returns the validated dict. |
| `runtime_config(root: Path)` | Returns CodexConfig with an isolated launcher environment and disabled external tools. |
| `coordinator_advice(root: Path, status: dict, timeout: int=120) -> dict` | Returns available/unavailable advice, enforcing Python 3.10+, the pinned SDK and a timeout (default 120 s). |
| `render_advice(advice: dict) -> str` | Formats a concise summary or unavailable reason as text. |

## Effects and failure behavior

The private async _run starts an ephemeral read-only/deny-all thread, requests schema output and records observed runtime metadata. Requires the optional openai-codex package, bundled CLI, persisted login and connectivity. Failures produce unavailable results, never invented recommendations or state writes.

## Example

`status --advise --json` requests advice explicitly; `status --json` alone avoids this runtime.
