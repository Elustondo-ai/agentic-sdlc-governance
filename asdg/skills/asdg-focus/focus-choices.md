# Focus picker entries — UI mapping, not role definitions

The [existing catalogue](../../00-governance/types/agent-catalog.json) owns IDs, paths and procedures.
The [lifecycle baseline](../../../docs/status/lifecycle-baseline.md) owns numbering and full stage names.
These display labels follow the current baseline. Stage 02 is Purpose; canonical role, native and procedure identities use the ASDG namespace.
Each entry is a thin discovery adapter into the same shared [Focus workflow](SKILL.md).

| Stage | Short display label | Picker skill | Canonical role | Generic short alias |
| --- | --- | --- | --- | --- |
| 01 | Context & Domain Analysis | `asdg-focus-01-context` | `ASDG-01` | `context` |
| 02 | Purpose | `asdg-focus-02-purpose` | `ASDG-02` | `purpose`, `02-purpose`, `intent` |
| 03 | System Model & Use Cases | `asdg-focus-03-use-cases` | `ASDG-03` | `use-cases` |
| 04 | Benchmarks & Test Strategy | `asdg-focus-04-test-strategy` | `ASDG-04` | `test-strategy` |
| 05 | High-Level Architecture | `asdg-focus-05-architecture` | `ASDG-05` | `architecture` |
| 06 | Viable Proof of Concept | `asdg-focus-06-poc` | `ASDG-06` | `poc` |
| 07 | Planning | `asdg-focus-07-planning` | `ASDG-07` | `planning` |
| 08 | Low-Level Design | `asdg-focus-08-low-level-design` | `ASDG-08` | `low-level-design` |
| 09 | Build & Test Cycle | `asdg-focus-09-build-test` | `ASDG-09` | `build-test` |
| 10 | Document, Review & Release | `asdg-focus-10-review-release` | `ASDG-10` | `review-release` |
| 11 | Operations, DevOps & User Acceptance | `asdg-focus-11-operations` | `ASDG-11` | `operations` |
| 12 | Observability, Insights & Learning | `asdg-focus-12-insights` | `ASDG-12` | `insights` |

Prefer selecting the named skill in the native picker; it requires no parameter and no second menu.
Generic numeric selectors, canonical role IDs/native names and catalogue folder basenames also work.
`purpose` / `02-purpose` / `intent` / `02-purpose` / `02` / `ASDG-02` / `asdg_02` identify the same Purpose role.
`asdg-focus clear` clears focus without granting permission or activating the coordinator.
All twelve currently retain their canonical read-only evaluation limits; picker presence is not execution evidence.
