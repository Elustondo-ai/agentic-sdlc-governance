AI-MODIFIED - 2026-10-14T16:07:31Z

# ASDLC canonical implementation packages

Reusable methodology definitions live here; consuming projects own their state and results.
The [catalogue](00-governance/types/agent-catalog.json) fixes stable identities and lifecycle order.
00 is governance; 01–12 are the twelve stages from the [baseline](../docs/status/lifecycle-baseline.md).

| Stage | Role | Canonical definition |
| --- | --- | --- |
| 00 | ASDLC-COORDINATOR | [ASDLC Coordinator](00-governance/AGENTS.md) |
| 01 | ASDLC-01 | [Context and Domain Agent](01-context-and-domain-analysis/AGENTS.md) |
| 02 | ASDLC-02 | [Intent Agent](02-intent/AGENTS.md) |
| 03 | ASDLC-03 | [System Model and Use Cases Agent](03-system-model-and-use-cases/AGENTS.md) |
| 04 | ASDLC-04 | [Benchmark and Test Strategy Agent](04-benchmarks-test-strategy-and-success-criteria/AGENTS.md) |
| 05 | ASDLC-05 | [High-Level Architecture Agent](05-high-level-solution-design-and-architecture/AGENTS.md) |
| 06 | ASDLC-06 | [Viable POC Agent](06-viable-proof-of-concept/AGENTS.md) |
| 07 | ASDLC-07 | [Planning Agent](07-planning/AGENTS.md) |
| 08 | ASDLC-08 | [Low-Level Design Agent](08-low-level-design/AGENTS.md) |
| 09 | ASDLC-09 | [Build and Test Agent](09-build-and-test-cycle/AGENTS.md) |
| 10 | ASDLC-10 | [Document, Review and Release Agent](10-document-review-and-release/AGENTS.md) |
| 11 | ASDLC-11 | [Operational Reality, DevOps and User Acceptance Agent](11-operational-reality-devops-and-user-acceptance/AGENTS.md) |
| 12 | ASDLC-12 | [Observability, Insights and Learning Agent](12-observability-insights-and-learning/AGENTS.md) |

## Shared capabilities and runtime
- [Documentation](skills/asdlc-documentation/SKILL.md): compact specialist-owned visual/notes units.
- [Presentation](skills/asdlc-presentation/SKILL.md): optional derived presentation exports.
- [Component](skills/asdlc-component/SKILL.md): software-component scaffolding, not agent roles.
- [Runtime](00-governance/docs/runtime-contract.md): role activation, scope, evidence and gates.
- [Baseline](00-governance/docs/baseline-capture.md): separate Codex processes loading role packages.
Read-only native adapters remain under `.codex/agents/`; baseline processes do not activate them.
Structural validity is not native execution, semantic correctness, approval or implementation authority.
