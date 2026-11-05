---
name: asdg-suggestion
description: Recommend a useful next contribution from the selected ASDG specialist, or a project-wide next step when unfocused or called by Status. Advice only; preserves focus and authority.
---

# ASDG Suggestion

Recommend one concrete next step under [the continuation contract](../../00-governance/docs/continuation.md), using judgment rather than a stage checklist.
Resolve the client root from this canonical file as `../../..`; use only its embedded distribution.
Read client `AGENTS.md`, [distribution instructions](../../AGENTS.md), [session policy](../asdg-focus/session-policy.md),
[lifecycle baseline](../../docs/lifecycle-baseline.md) and [catalogue](../../00-governance/types/agent-catalog.json).

## Establish the situation

Identify the target project, latest user goal, constraints and explicit decisions from this conversation.
Resolve the recommendation perspective from that contract: direct specialist advice is role-scoped; Status always requests project-wide advice.
Keep a current methodology-maintenance task distinct from the consuming application's next product step.
When called by Status, reuse its fresh CLI result and inspection evidence; otherwise run `python3 asdg/scripts/cli.py status --json`.
Never call the Status skill back; inspect additional sources only when needed or evidence has changed. This workflow needs no SDK.
Use recorded project/release/sprint facts separately from conversation focus and human authorization.
The CLI's earliest-unmet-evidence recommendation is input, not the answer or a mandatory stage sequence.
Inspect relevant client documents and source before deciding; scaffold READMEs and methodology definitions are not client evidence.
Look for useful existing work even when no evidence is registered. Separate missing, stale, uninspected and contradictory evidence.
Read the candidate stage's contract and relevant procedure to understand its contribution and current delivery limits; reading never activates it.
Use [Intended / Actual / Planned](../../00-governance/docs/stage-perspectives.md) to distinguish desired outcomes, supported facts and selected commitments.
If a tool is denied or state is unavailable, report the specific gap once; do not retry unchanged calls or silently initialize/repair.
Offer a conditional suggestion from available evidence when possible; ask one focused question only if its answer would change the choice.

## Choose what matters next

Consider the few plausible actions that advance the current goal; compare value, uncertainty resolved, urgency, dependencies and effort.
Prefer the smallest useful conversation, decision, observation, experiment or scoped task over more machinery or documents by default.
Respect active commitments: recommend progress or evidence for the agreed scope, or explain why a human should reconsider it.
Prioritize a demonstrated operational/user problem when urgent; do not send a working project back through every empty stage.
For a seed, clarify only the context/purpose needed for the next useful trial; do not invent a platform, roadmap or required POC.
When called by Status, honor its [post-install onboarding assessment](../asdg-status/SKILL.md#after-installation--recommend-team-setup-from-status) before the NEW/Purpose heuristic; reuse its team evidence, uncertainty, deferrals and capability limits. Do not call Status again or execute team setup.
For NEW with no substantive Purpose and no urgent dependency, suggest the verified Purpose Focus selector; do not require a complete Context package first.
Treat absent sprint authorization as a boundary on implementation, not a reason to create a sprint for discussion or inspection.
Unknown hook trust matters when relying on enforcement; do not make it a universal blocker to useful read-only work.
Recommend checking behavior or user value when that uncertainty matters more than polishing documentation.
When evidence conflicts with the user's preference, explain the tradeoff respectfully rather than tailoring advice to win agreement.

## Return a useful recommendation

Use the compact session declaration once, then label the recommendation perspective and give the action, benefit and evidence-based reason; avoid repeating the role tutorial.
Explain why it outranks the nearest plausible alternative when the choice is material; avoid a long menu or automatic twelve-stage plan.
State the expected result or observation that would make the step worthwhile, plus the uncertainty that could change the recommendation.
When a focused chat would help, name the existing selector from the catalogue/adapters and provide a short ready-to-use assignment.
Read current role contracts before promising delivery: distinguish conversation-only roles from any bounded documentation/review allowance.
Keep the response proportional; distinguish facts, user preferences and recommendations without repeating a full status report.
Respect rejected advice and deferrals; change the recommendation when evidence warrants it. Agreement is not approval or execution authority.
Keep preferences in conversation context; do not persist them, change this skill or claim learning across chats without authorization.
Return advice only: no writes, role activation, delegation, title changes, sprint/release transitions, commits, installation or deployment.
