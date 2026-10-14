AI-MODIFIED - 2026-10-10T01:19Z

# ASDLC — proposed named-agent roster

**Review draft only.** One coordinator plus exactly twelve specialist roles aligned with the existing [lifecycle baseline](../../docs/status/lifecycle-baseline.md).

## Routing principle
- The developer normally addresses `ASDLC-COORDINATOR`.
- The coordinator consults one authoritative sprint state, determines applicable scope, and delegates a bounded task.
- A developer may address a specialist directly, but direct access does not grant broader authority.
- Specialists encountering out-of-scope work return an `OUT_OF_SCOPE` request to the coordinator; they do not maintain their own routing map.
- Only the coordinator routes; **neither coordinator nor specialist may override a human approval gate**.

## Draft agents
- [ASDLC Coordinator](00-coordinator.md) — `ASDLC-COORDINATOR`
- [Context and Domain Agent](01-context-domain.md) — `ASDLC-01`
- [Intent Agent](02-intent.md) — `ASDLC-02`
- [System Model and Use Cases Agent](03-system-model-use-cases.md) — `ASDLC-03`
- [Benchmark and Test Strategy Agent](04-benchmark-test-strategy.md) — `ASDLC-04`
- [High-Level Architecture Agent](05-high-level-architecture.md) — `ASDLC-05`
- [Viable POC Agent](06-viable-poc.md) — `ASDLC-06`
- [Planning Agent](07-planning.md) — `ASDLC-07`
- [Low-Level Design Agent](08-low-level-design.md) — `ASDLC-08`
- [Build and Test Agent](09-build-test.md) — `ASDLC-09`
- [Document, Review and Release Agent](10-document-review-release.md) — `ASDLC-10`
- [Operational Reality, DevOps and User Acceptance Agent](11-operational-reality.md) — `ASDLC-11`
- [Observability, Insights and Learning Agent](12-observability-learning.md) — `ASDLC-12`

## Status and next decisions
These are *logical proposals*, not 13 live Codex subagents. Before activation: approve the agent contracts, reconcile sprint governance and role boundaries, choose native platform adapters, define tool permissions, and test negative responsibility cases. Existing personal Registry entry `SDLC2` is **not changed** by this draft.
