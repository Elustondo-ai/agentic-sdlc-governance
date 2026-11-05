---
name: asdg-init
description: Preview and explicitly apply ASDG initialization from an extracted package or verified local canonical clone. Use only for a direct installation request; never for application implementation, role activation or migration from a linked provider.
---

# Initialize ASDG using one Python engine

Read [installation](../../docs/installation.md), [client integrations](../../docs/client-integrations.md) and the target project's instructions.
This skill is a conversational interface to `asdg/scripts/init.py`; never reproduce its file writes in prompts or shell scripts.
Use Python 3.9+ and an existing Git project. Never initialize Git or install dependencies automatically.
Identify the target root and acquisition: an extracted ZIP or an existing local canonical clone.
For ZIP, require its single `asdg/` folder; acquisition must never overwrite existing application or methodology files.
For Clone, require the local clone path and explicit full commit ID. Never choose HEAD as consent or fetch a newer commit.
Use the selected source's entry point; its engine verifies canonical origin, exact HEAD, selected committed bytes and integrity.
A stale manifest blocks installation; obtain a matching package or stop for source review. Never refresh it to install.
Select `--client claude` in Claude Code or `--client codex` in Codex; ask if unknown, never install both unasked.
Use an explicitly supplied `--project-status`; otherwise retain `new`. Code presence establishes no stage acceptance.

## Mandatory approval presentation — both clients

Run the [ZIP preview](../../docs/install-zip-prompt.md) or [Clone preview](../../docs/install-clone-prompt.md) with `--dry-run --json`.
Capture the complete successful JSON report, including every file row, diff and plan token, in a uniquely named temporary file outside the target Git root; do not overwrite an existing file. Keep it accessible through the decision and verification.
Check successful exit, valid JSON, `dry_run: true`, `installation_complete: false` and a nonempty `plan` before requesting approval. Errors or conflicts block; never present a failed preview as approvable.
Read back the saved report and provide its actual accessible path as a clickable reference (or a terminal read command in text-only clients). If it cannot be accessed, show the complete report and diffs inline before asking.
Display the following distinct section, replacing EVERY placeholder with values from that same preview; never show example numbers or claim installation has been applied:

### ASDG INSTALLATION — APPROVAL REQUIRED

**Target:** `<project_root>` · **Version:** `<source.version>` · **Client:** `<clients_applied>`
**New files:** `<count files with action added>` · **Existing files modified:** `<count files with action modified>`
**Integrity:** `<source.integrity>` · **Conflicts:** None (only after a successful conflict-free preview)
Complete installation plan and diffs: `<actual accessible reference or complete inline report>`
**Do you approve applying this exact installation plan?**
**Reply APPROVE to proceed, or CANCEL to stop.**

Counts describe the pending engine writes, including distribution files for Clone; already extracted ZIP members are unchanged and excluded. Identify that distinction separately; never invent an acquisition count.
Separately explain: approval covers only this plan. Hook trust requires separate human action; commits, pushes, publication, sprint starts and Context are not authorized.
STOP. Only a standalone APPROVE (case-insensitive, surrounding whitespace ignored) approves the displayed plan; CANCEL stops. Ambiguous replies, initial install requests, silence or conditional approval do not authorize apply; clarify and wait.

## Apply, verify and offer Context

After APPROVE, repeat identical options with `--apply --plan <token from the displayed preview>` instead of `--dry-run`; never use a different token silently.
A collision, stale plan, source mismatch or runtime denial stops dependent writes; any fresh plan needs a new presentation and APPROVE.
Never bypass hooks, grant trust, edit lifecycle state manually or resolve unrelated promotion conflicts. If the runtime blocks apply, report the exact terminal command for the human.
The engine verifies structure inside its rollback boundary; then run the installed `python3 asdg/scripts/cli.py verify --json` in the target.
Repeat the same preview for no further writes; repeat apply requires another approval. Report completion only after verification, with changed paths and preservation evidence.
Distinguish structural checks from observed native discovery, invocation and human hook trust; unit tests prove no native operation.
Ask “Would you like to run the optional Context survey?” then STOP; never ask survey questions, create orientation notes, activate a specialist or invoke another skill without a separate affirmative response.
A later yes authorizes only Context under its existing scope; infer no acceptance. Never commit, push, merge, tag, publish, declare a release or start a sprint automatically.
