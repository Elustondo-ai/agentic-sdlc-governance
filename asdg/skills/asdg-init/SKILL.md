---
name: asdg-init
description: Preview and explicitly apply ASDG initialization from an extracted package or verified local canonical clone. Use only for a direct installation request; never for application implementation, role activation or migration from a linked provider.
---

# Initialize ASDG using one Python engine

Read [installation](../../docs/installation.md), [client integrations](../../docs/client-integrations.md) and the target project's instructions.
This skill is a conversational interface to `asdg/scripts/init.py`; never reproduce its file writes in prompts or shell scripts.
Use Python 3.9+ and an existing Git project. Never initialize Git or install dependencies automatically.
Identify the target root and whether acquisition is ZIP extraction or an existing local canonical clone.

For ZIP, the selected package must already be extracted as the target's single `asdg/` folder; do not extract over existing application or methodology files.
For Clone, require the local clone path and the developer's explicit full commit ID. Do not choose HEAD as consent or fetch a newer commit.
Use the selected source's Python entry point. The engine verifies canonical origin, exact HEAD, committed selected bytes and package integrity.
A stale manifest is a blocked installation, not permission to refresh it. Obtain a matching package or stop for source review.

Select `--client claude` in Claude Code or `--client codex` in Codex unless the developer explicitly chose otherwise. Ask if the host is unknown; never install both unasked.
Use an explicitly supplied initial `--project-status`; otherwise keep the default `new`. Code presence does not establish `defined` or stage acceptance.

Run the [ZIP preview](../../docs/install-zip-prompt.md) or [Clone preview](../../docs/install-clone-prompt.md).
Show the complete file plan and generated diffs, especially hooks, configuration and instruction bridges. Report source version, integrity and clone commit where applicable.
STOP and wait for explicit developer approval of that exact plan before applying. An initial request to install does not authorize an unseen plan.

After approval, repeat identical options with `--apply --plan <token>` in place of `--dry-run`. Never modify the plan or silently retry with a new token.
A collision, stale plan, source mismatch or runtime denial stops dependent writes. Preserve existing work and give the human an exact terminal command if the runtime blocks it.
Never bypass hooks, grant trust, edit lifecycle state manually or resolve unrelated promotion conflicts.

The engine verifies package and integration structure inside its rollback boundary. Then run the installed `python3 asdg/scripts/cli.py verify --json` from the target root.
Repeat the same preview to verify there are no further planned writes; repeat application requires another explicit approval.
Report installation complete only after successful verification, with exact changed paths and preservation evidence.
Distinguish deterministic structural checks from observed native discovery, actual invocation and human hook trust. No successful unit test proves native operation.

After completion, ask: “Would you like to run the optional Context survey?” Then STOP.
Never execute the Context survey, ask its questions, create orientation notes, activate a specialist or invoke another skill without a separate affirmative response.
A later yes authorizes only the Context survey; follow the Context role's existing scope and document unknowns without inferring acceptance.
Do not commit, push, merge, tag, publish, declare a release or start a sprint automatically.
