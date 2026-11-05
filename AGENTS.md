# Agentic SDLC repository instructions

This repository is the canonical ASDG methodology provider. `asdg/` contains reusable implementation; `docs/` explains the method and records its development.
Read root README, [methodology entry](asdg/AGENTS.md), [session policy](asdg/skills/asdg-focus/session-policy.md) and task-relevant sources before work.
Current explicit instructions from Pablo override older notes and proposals.

## Maintenance and distribution

Agent changes to methodology run under explicitly selected [ASDG Admin](asdg/admin/AGENTS.md) within the human's bounded request.
This provider is not an initialized application: use `python3 asdg/scripts/check.py --integrity` and applicable tests instead of client status/init.
The [README handoff](README.md#quick-start--give-your-agent-the-repository-url) lets a developer explicitly ask their agent to acquire and verify the versioned ZIP, safely extract into an existing Git root, then follow the packaged prompt; a URL alone is not installation authorization. Stop if `asdg/` exists and retain the preview approval and separate team/project-work requests.
The recommended first-time workflow is the explicit repository-URL request in README; manual [ZIP + Prompt](asdg/docs/install-zip-prompt.md) remains available: download the versioned portable ZIP, extract its single `asdg/` folder into an existing Git root, stop if that folder exists, then paste the prompt in Claude Code or Codex.
The assistant uses the single `asdg/scripts/init.py` engine: preview → explicit approval → apply and verify → point to `/asdg-status` and wait for the user to invoke it. Status owns the post-install assessment and any `/asdg-create-team` recommendation, including evidence, deferrals and client limits. No methodology clone or manual Python command is required of the user.
For contributors, [Clone + Prompt](asdg/docs/install-clone-prompt.md) pins a full reviewed commit with a matching manifest; `asdg promote` brings pilot improvements into the local canonical checkout for review and a contributor PR, while `asdg upgrade` adopts an accepted packaged version in another project.
Each client (for example LifeBuckets and iShop) owns its versioned `asdg/` copy; follow the [synchronization contract](asdg/docs/synchronization.md) for previews, approved apply and conflicts.
For provider-only `asdg publish` requests, use [ASDG Publish](asdg/skills/asdg-publish/SKILL.md); keep that workflow out of client packages and adapters.
Before every human commit/push, run `python3 scripts/prepare_commit.py` to refresh the candidate manifest and regenerate the portable ZIP/checksum. Review and include the refreshed manifest in the commit; re-run after further package edits.
The wrapper reuses `asdg/scripts/build_distribution.py`; the reviewed file list is `asdg/metadata/package-files.json`. No automatic Git hook or publication is installed.
Generated ZIPs, checksums and previews belong under ignored `build/`; never stage them.
`bin/asdg` delegates to the portable runtime. Old provider installer/baseline code is retained as history, not a second active policy engine.
Canonical skill definitions remain under `asdg/skills/`; native adapters are thin discovery entry points.
Templates under `asdg/templates/` generate client adapters. Do not copy a client's state, installed configuration, logs or application evidence into the distribution.
Keep this repository's disabled `.agents` discovery entries disabled unless Pablo explicitly requests activation.
Before claiming platform operation, verify native discovery and an actual invocation on that platform; structural tests are insufficient.
ASDG-owned automation uses Python >= 3.9; applications may use any language.

## Presentation and component work

Use `asdg/skills/asdg-presentation/SKILL.md` for presentation creation, maintenance and builds; do not duplicate its standard.
Presentation source folders under `docs/presentations/` are authoritative; each owns an ignored `build/` for generated exports.
Use `asdg/skills/asdg-component/SKILL.md` for component creation/structure validation.
Presentation, component and video tools remain provider capabilities outside the portable core's acceptance claim.
The video builder's eSpeak implementation is a proof of concept, not approved high-quality narration.

## Scope and evidence

Keep changes bounded; preserve unrelated work and historical source material.
Distinguish implemented, tested, proposed and human-approved states; all 13 project roles use [Intended / Actual / Planned](asdg/00-governance/docs/stage-perspectives.md).
Preserve catalogue identities and [lifecycle numbering](asdg/docs/lifecycle-baseline.md); legacy identities exist only in migration records.
Follow the [documentation standard](asdg/00-governance/docs/documentation-standard.md), with exact-hash review events and YAML-first skills.
Never add or advance PME-APPROVED without explicit approval of the exact file state.
A plan, review marker or prior operation grants no publication, commit, push, deployment, deletion or permission-change authority.
Report actual verification and failed operations; generated files and passing tests are not approval.

## Conversation state

Follow the shared session policy on every turn. Governance is the default accountable role; specialist and Admin selection require their explicit activation rules.
Keep role, subject focus and attitude in this conversation; never infer them from folders, titles, another chat or project state.
Status inspects state without selecting or clearing a role. No shared ACTIVE_ROLE file is used.
