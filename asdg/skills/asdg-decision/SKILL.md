---
name: asdg-decision
description: Analyze, compare, document, or revisit a material ASDG decision using the current project and specialist context. Use for architectural trade-offs as well as product choices; preserves Focus and operational authority.
---

# ASDG Decision

Use this conversation's decision, purpose, constraints, evidence, and human choices; do not restart a completed discussion.
Recognize `$asdg-decision` and “asdg decision” as this conversational skill, not a new CLI subcommand.
Resolve the client from this canonical directory as `../../..`; read its instructions, [session policy](../asdg-focus/session-policy.md), and fresh local CLI status.
Use current verified context when available. Ask only for missing information that would materially change the analysis or destination.

## Resolve context and intent

Identify the decision subject, affected project, accountable role (00 Governance by default, or Unknown when blocked), and requested action.
A selected role defines the perspective; an explicit user assignment defines the subject. Neither reading this skill nor inferring an owner changes Focus.
Distinguish methodology maintenance from a decision about the consuming application.
Resolve the selected specialist or explicit role assignment through the [catalogue](../../00-governance/types/agent-catalog.json); read that role's contract.
Apply [optional specialization](specialization.md): load `<catalogue folder>/skills/decision/SKILL.md` when present; otherwise use the generic method below.
The specialist folder supplies context, not a changed terminal working directory. Do not search unrelated roles for an override or route every decision to Stage 05.
Without a selected role, use the explicit task and evidence to identify a proposed owner without activating it. If ownership or destination matters and remains ambiguous, clarify it.
A request for analysis only returns analysis. A request to record/document, or an existing assigned documentation task, saves within applicable authority; never ask again for already granted authorization.
A bare invocation continues the evident task; if intent is unknown, analyze provisionally and clarify the missing action before writing.

## Analyze and record

Explain the desired outcome and why a choice matters before describing mechanisms.
Compare the few viable options, including the current approach or no change when meaningful; compare equivalent responsibilities and separate complements.
Consider relevant quality attributes, constraints, costs, failure modes, reversibility, migration effort, and evidence gaps; avoid arbitrary scoring.
Distinguish verified behavior, vendor claims, inference, and untested expectations. Verify unstable external claims with primary sources.
Carry forward an explicit human selection; otherwise label the choice proposed or undecided. A framework recommendation is not measured superiority.
For documentation, follow [the decision package format](record-format.md); use [the worked example](example.md) as guidance, not a fixed product list.
Reuse the existing decision package when revisiting it; preserve the previous choice, evidence, rationale, and reasons for change.
Deliver a concise recommendation or record link, consequences, and the evidence that would justify revisiting the decision.

## Boundaries

The owning contract determines documentation authority and destination; a local specialization cannot expand either.
Discovery alone grants no writes, role activation, delegation, or state transitions; generic fallback grants no additional authority.
Selection records describe the human's stated choice; they do not approve newly written bytes or trigger implementation.
Preserve lifecycle/sprint state and review history. Formal acceptance uses the existing approval workflow only when explicitly requested.
Respect runtime denials; preserve the analysis and report the exact blocked write rather than bypassing controls.

