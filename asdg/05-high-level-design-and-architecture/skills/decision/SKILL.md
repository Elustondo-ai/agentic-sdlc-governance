---
name: decision
description: Enrich the shared ASDG Decision method with high-level architecture criteria, evidence and explanatory views.
---

# Architecture decision specialization

Owner: ASDG-05. Apply this local method after the shared [Decision workflow](../../../skills/asdg-decision/SKILL.md) has resolved this role.
Inherit its common method and [extension contract](../../../skills/asdg-decision/specialization.md); do not invoke the shared entrypoint recursively.
Read [architecture foundations](../../docs/architectural-decisions.md) and the [role contract](../../types/contract.md).

## Frame and compare

Identify the system responsibility being allocated: boundaries, deployment, interfaces, data/control ownership, resilience or a dependency.
Compare alternative ways to fulfill that responsibility; distinguish complementary layers from competing choices.
Use relevant latency, reliability, consistency, security, operability, cost, portability and migration effort; explain which qualities drive this decision.
Include the current architecture when viable and prefer a commitment proportionate to the current outcome and change cost.

## Evidence and explanation

Connect alternatives to use cases, constraints, existing implementation and evaluation findings; a feature list or vendor identity does not demonstrate fitness.
Keep measured behavior distinct from intended architecture and untested expectations; identify the smallest useful evidence gap.
Choose a component, sequence, deployment or failure-boundary view that reveals responsibilities and consequences.
Use the shared short visual package for assigned architecture documentation within the role contract's existing paths.

## Reconsideration

Name concrete changes in load, failure tolerance, deployment, ownership, integration or user needs that would reopen the choice.
Distinguish a missing implementation of the selected design from evidence that the design itself is unsuitable.
All unmentioned behavior inherits the generic method. This specialization grants no additional write, implementation or acceptance authority.
