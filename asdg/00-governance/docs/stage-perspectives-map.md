# Stage mapping — Intended / Actual / Planned

This defines what each view covers; the rows below are NOT an audit of any project's actual state.
Use with the [shared contract](stage-perspectives.md) and [current lifecycle](../../../docs/status/lifecycle-baseline.md).
The catalogue has thirteen responsibilities: 00 governance plus lifecycle stages 01–12.

| Responsibility | Intended | Actual | Planned |
| --- | --- | --- | --- |
| 00 Governance | Desired responsibilities, authority boundaries, gates and traceability. | Observed assignments, approvals, active state and enforcement evidence. | Selected governance fixes, unresolved decisions and cross-stage coordination. |
| 01 Context & Domain Analysis | Required domain coverage, stakeholders and target operating context. | Known environment, stakeholders, constraints, sources and uncertainties. | Selected research, interviews and context updates. |
| 02 Purpose | Why the system should exist; desired outcomes, constraints and non-goals. | Value/outcomes currently supported by evidence; gaps and unvalidated assumptions. | Selected next outcome increments and purpose-validation decisions. |
| 03 System Model & Use Cases | Target actors, domain model, interactions and observable behavior. | Existing interactions and behavior, verified against implementation or observation. | Selected use cases/model changes and their acceptance questions. |
| 04 Benchmarks, Test Strategy & Success Criteria | Target success criteria, alternatives and evaluation approach. | Available baselines, measured results, test evidence and comparison limits. | Selected benchmark runs, test-strategy changes and evidence collection. |
| 05 High-Level Solution Design & Architecture | Target components, boundaries, interfaces and architectural constraints. | Evidenced as-built architecture and known deviations from the target. | Selected architecture decisions, migration increments and dependency impacts. |
| 06 Viable Proof of Concept | Feasibility question, hypotheses and intended experimental success. | Experiments actually performed, observations, limitations or justified non-applicability. | Selected experiments and follow-up decisions; no fabricated POC. |
| 07 Planning | Desired delivery outcomes, planning horizon and sequencing constraints. | Current plan-of-record, commitments and evidenced progress/blockers; a plan is not delivered work. | Selected plan revisions, next work items and dependency/owner decisions. |
| 08 Low-Level Design | Target contracts, detailed behavior, interfaces and edge cases. | Current as-built interfaces and behavior, linked to code and checks. | Selected design changes or specifications needed for the next increment. |
| 09 Build & Test Cycle | Required behavior and build/test exit criteria for the scoped increment. | Changes actually implemented and tests actually run, with version and results. | Selected fixes, implementation increments and test work awaiting applicable gates. |
| 10 Document, Review and Release | Required documentation, review quality and release criteria. | Existing documents, observed reviews, exact-state approvals and release evidence. | Selected documentation fixes, reviews and release-preparation actions. |
| 11 Operational Reality, DevOps & User Acceptance | Desired operating behavior, reliability, rollout and acceptance outcomes. | Observed deployment/environment state, health and user-acceptance evidence. | Selected rollout, recovery, operational and acceptance actions. |
| 12 Observability, Insights & Learning | Questions to answer, required signals and intended learning outcomes. | Available telemetry/feedback and evidence-backed findings, including uncertainty. | Selected instrumentation, validation and improvement work for the next cycle. |

## Keep the two meanings of planning separate

Planned is a perspective available in every stage; Stage 07 is the responsibility for integrating work plans.
An existing plan belongs in Actual only as an observed plan/commitment, never as completed implementation.
Specialists may propose local next work; planning/coordinator decisions and human authorization remain separate.

## Purpose is not a process-maturity score

For a product, Purpose/Actual concerns evidenced value and outcomes, not whether its agent loaded a skill.
For a methodology-implementation review, agent activation may be valid Actual evidence within that explicitly stated subject.
In either case, a target or future plan must not be presented as observed behavior.
