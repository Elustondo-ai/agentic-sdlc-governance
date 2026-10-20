---
name: asdg-derive-insights
description: "Observability, Insights and Learning Agent: evidence-scoped analysis in read-only evaluation."
---

# Derive Insights

Owner: `ASDG-12`; [entry](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-driven specialization; loading this method does not activate a role or authorize writes.
Read shared runtime rules and [asdg-documentation](../../../skills/asdg-documentation/SKILL.md).
Use domain-appropriate topology, signal or feedback diagrams; do not duplicate shared capability.

## Procedure

1. Identify the telemetry period, system revision, collection limits and privacy boundaries; do not collect new data without authority.
2. Separate observed signals from hypotheses; trace each finding to supplied evidence and note missing baselines or sampling bias.
3. Compare trends, incidents and user feedback without inventing metrics, causation or independent confirmation.
4. Document signal/feedback flows and confidence limits using the shared documentation skill; keep sensitive payloads out of reports.
5. Propose lessons and candidate next-cycle work for human prioritization; do not change backlog scope, code, approvals or sprint state.

## Output and boundary

Return insights with provenance, hypotheses, and proposed next-cycle work.
Identify provenance, uncertainty, contradictions and unavailable evidence; do not infer approval.
Do not silently change scope, implement fixes, or override product priorities.
In native read-only evaluation, return proposals in conversation; writes are BLOCKED: READ_ONLY_EVALUATION.
Only an explicitly authorized baseline process may author its own isolated documentation; no application implementation.
Return OUT_OF_SCOPE through the coordinator; never claim delivery or measurements without observation.
