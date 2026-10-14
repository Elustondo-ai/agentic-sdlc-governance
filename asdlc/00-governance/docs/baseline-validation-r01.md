AI-MODIFIED - 2026-10-14T19:27:16Z

# Baseline capture — environment and evidence contract (R02)

## Subprocess environment
`subprocess_environment()` passes only PATH/HOME/user identity, temp locations, locale,
public CA certificate locations and the fixed PYTHONDONTWRITEBYTECODE setting.
An explicit, existing absolute CODEX_HOME may locate persisted Codex authentication/state.
No API keys/access tokens, cloud/application credentials, SSH agent, proxy credentials,
Python injection paths or dynamic-loader injection variables are inherited.
Persisted Codex login is supported; environment-only provider authentication is deliberately unsupported.
Use a persisted login before capture; no silent credential forwarding or broad fallback.
The child command environment uses an explicit whitelist with `inherit="none"` and default exclusions.
CODEX_HOME is for the trusted client, not included in the tool environment whitelist.
Per-run policy replaces the environment table; incompatible managed configurations fail closed.
See [official command-environment settings](https://learn.chatgpt.com/docs/config-file/config-advanced)
and [Codex state/auth locations](https://learn.chatgpt.com/docs/config-file/environment-variables).
Negative tests use in-memory synthetic sentinels; child probes report only success, never values.
Persisted authentication was checked read-only; a real model invocation is not authorized in R01.

## Provenance
Every unit requires a `Sources:` line listing actual source/ or context/ snapshot files.
Separate entries with semicolons. Raw paths, backticks, Markdown links, URL-encoded spaces,
anchors and conventional `:line` / `:start-end` suffixes are accepted.
Examples: `source/Plan.md:2`; `[diagram](source/docs/design.svg#topic)`; `context/01/visual.png`.
Declared entries, recognized inline links and source/context path references must resolve inside the workspace.
Missing files, traversal (including encoded traversal), absolute/external paths, symlinks
and linked/non-regular files are rejected before promotion. File extensions are not restricted.
Links to existing artifacts in the same authored unit and same-document anchors are allowed.
Reference-style Markdown definitions and full/collapsed references are rejected, including literal examples.
Use inline links instead; this restriction also applies to reference definitions in narrative lines.
URI/email autolinks outside narrative lines are rejected; explicit narrative autolinks remain unverified.
External/narrative citations belong on an explicit `Narrative citations:` line and are UNVERIFIED.
They cannot replace resolvable Sources evidence. No URLs are fetched by this validator.
This is a constrained citation grammar, not a complete Markdown/HTML parser or arbitrary prose-path checker.
Resolution proves a file exists, not that a citation, passage/anchor or factual assertion is accurate.
Narrative citation truth and visual semantics remain human-review tasks.

## Execution semantics
Each invocation is a separate Codex process loaded with one catalogued role, not a native subagent.
Coordinator routing and synthesis are separate process/session invocations.
Logs identify loaded role, process mode, emitted Codex session, observed start/end/status/count
and validated artifact hashes; a successful agent result is explicitly labelled a self-report.
Runner errors are labelled runner observations. The runner authors these operational logs.
The specialist process authors its own stage artifacts; the runner promotes exact validated bytes.
Native adapter names describe catalogue configuration, never proof those adapters were activated.
Native subagents remain disabled during baseline capture; old trial evidence is not relabelled.
