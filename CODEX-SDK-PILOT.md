AI-MODIFIED - 2026-10-16T19:40:08Z

# ASDG coordinator SDK integration

`asdg status` uses Python Codex SDK 0.163.0 and the existing coordinator definition.
It reports recorded state and requests one read-only advisory turn; it never starts a sprint.
The agent chooses the recommendation. The deterministic engine still owns facts and gates.

## Run

Use Python 3.10+ in the interpreter recorded by the ASDG installer.
For this checkout: `../agentic-sandbox/.venv311/bin/python3 -m pip install openai-codex==0.163.0`.
The SDK installs its matching `openai-codex-cli-bin` runtime; PATH's Codex is not selected.
Use your normal Codex sign-in; do not place credentials in project files.
From the Speaker Coach project directory: `asdg status`.
For factual JSON without an agent: append `--json`.
For factual text without an agent: append `--facts-only`.
For JSON including advice: append `--json --advise`.
The model uses the account's configured default. Advice has a 120-second timeout.
Advice failure leaves factual status available; it is not a fabricated recommendation.

## Code walkthrough

`asdg-sdk.py` is a compatibility launcher forwarding to the same integrated CLI.
`asdlc/00-governance/src/cli_advice.py` validates the role context and starts an ephemeral thread.
The ephemeral SDK thread requests `Sandbox.read_only` and `ApprovalMode.deny_all`.
The prompt identifies the project, role contracts, snapshot, output and advisory boundary.
The SDK requests a JSON schema; Python validates the returned fields independently.
Normal advice is printed; `--verbose` saves a bounded [report](asdlc/00-governance/docs/status-advice.md).
MCP, apps, browser/computer use, web search and additional agents are disabled for advice.
Shell tools receive an allowlisted environment; runtime authentication uses persisted sign-in.
The SDK returns a plain `TurnStatus` enum; compare `.value`, not the enum to a string.
The SDK merges `config.env`; a small execve launcher supplies a clean allowlisted environment.
It sets the nonempty `asdg_coordinator` originator required for initialization metadata.
Advice includes SDK/runtime version and configured model; this is not per-turn model telemetry.
Missing SDK diagnostics identify the exact ASDG interpreter and installation command.

## Integration and verification

The original `codex-sdk-integration.patch` was reviewed and incorporated with safer diagnostics,
runtime restrictions, observable metadata and a nonzero exit code on unavailable advice.
It is historical input; do not reapply it to the integrated CLI.
`status --json`, `status --facts-only` and `next` never invoke the SDK.
Deterministic evaluation retains its existing UTC evaluation timestamp.
`status --json --advise` emits one JSON object with recorded facts and a separate `advice` field.
Advice cannot override gate decisions or approve, start, or execute any workflow action.
Absent project/release fields remain UNKNOWN; explicit `release: null` means none declared.
`project_status`: `new`, `defining`, `defined`; release object: `release_id` and `status`.
Release statuses: `planning`, `active`, `in_review`, `closed`; these declarations do not grant approval.
Tests mock LLM execution; live acceptance must separately verify a completed turn and unchanged files.
