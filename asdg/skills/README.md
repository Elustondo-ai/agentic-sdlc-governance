# Shared ASDG skills

Canonical workflows live here; native discovery adapters remain thin references.

| Skill | Purpose |
| --- | --- |
| [Update](asdg-update/SKILL.md) | Preview a selected distribution update and separate adapter refresh; explicit approval per plan |
| [Help](asdg-help/SKILL.md) | Explain all ASDG commands, examples and invocation syntax without executing them |
| [Initialize](asdg-init/SKILL.md) | Bootstrap the explicitly identified client |
| [Create team](asdg-create-team/SKILL.md) | Set up governance and twelve specialist chats, reusing existing focused chats |
| [Focus](asdg-focus/SKILL.md) | Select a role; use `subject` to change its topic independently |
| [Attitude](asdg-attitude/SKILL.md) | Choose a thinking approach, temporary scope, NoAttitude or read-only status |
| [Status](asdg-status/SKILL.md) | Show status, a suggested next step, then observations and technical debt |
| [Report project status](asdg-report-project-status/SKILL.md) | Author an illustrated Markdown presentation with slide sources and speaker notes. Export PowerPoint last |
| [Role](asdg-role/SKILL.md) | Explain the selected role's responsibilities, outputs and boundaries |
| [Admin](asdg-admin/SKILL.md) | Explicitly switch this chat to ASDG Admin for rule maintenance, or clear back to 00 Governance |
| [Approve](asdg-approve/SKILL.md) | Resolve the current reviewed documentation baseline and record explicit human acceptance |
| [Sprint start](asdg-sprint-start/SKILL.md) | Require clean Git status, create a sprint branch, then activate the chosen scope |
| [Sprint review](asdg-sprint-review/SKILL.md) | Assess evidence against the sprint criteria without changing state |
| [Sprint close](asdg-sprint-close/SKILL.md) | Preserve the review and end the explicitly selected sprint, retaining unfinished work |
| [Suggestion](asdg-suggestion/SKILL.md) | Recommend one useful next step from project evidence and priorities |
| [Development view](asdg-view-dev/SKILL.md) | Open a useful project file and terminal alongside the chat |
| [Documentation](asdg-documentation/SKILL.md) | Preserve readable, evidence-based project documents |
| [Decision](asdg-decision/SKILL.md) | Shared decision method with optional specialist-local enrichment |
| [OpenSpec proposal](asdg-openspec-propose/SKILL.md) | Connect ASDG evidence to the installed native proposal workflow; planning only |

Each numbered stage owns its bounded specialist procedure under its local `skills/` folder.
Its optional `skills/decision/SKILL.md` enriches Decision through the [shared interface](asdg-decision/specialization.md); absence uses generic behavior.
One Focus picker entry interprets natural-language requests for all thirteen roles; ambiguous intent prompts a choice, and 00 Governance is the default role.
Presentation/video and ASDG component-development tooling are outside this client core.
Native discovery and actual behavior must be checked in the selected Codex runtime.
