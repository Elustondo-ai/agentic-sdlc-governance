# Narrow write exceptions

These exceptions supplement [role ownership](documentation-authority.md), without selecting roles or authorizing work by themselves.
Every workflow preserves existing records, exact hashes, role assessments and human decisions; a path allowance cannot validate those semantics.

![Role-owned documents and separate authorization gates frame each narrow exception.](images/documentation-authority.svg)

| Workflow | Allowed responsibility and authorization |
| --- | --- |
| Specifications / OpenSpec | ASDG-08, only on an authorized specification task, follows the installed native workflow to resolve root, configured store and CLI-provided artifact paths. No assumed `openspec/` path; no apply, sync, archive, initialization or application edits. |
| Coding and testing | ASDG-09 may write application code, tests, source companions and related technical documentation in appropriate locations, only with active sprint, approved task, scope, criteria and per-target implementation checks. Other specialist stage documents remain owned. |
| Governance shared records | Governance owns its stage and may update explicitly assigned exact records under `docs/shared/`. Shared navigation outside it requires a separately reviewed workflow; no general root or specialist write grant. |
| Admin maintenance | Explicitly selected Admin may edit exact methodology, skill, template, control and test targets within human maintenance scope, plus its required Stage 07 change report/JSON receipt. No application work or state changes. |
| Authorship receipts | Every known role may append exact-hash AI modification events in `.asdg/document-reviews.json`; Admin uses the provider ledger for methodology documents. No rewriting history or acceptance. |
| Documentation review | Explicit Approve permits only target-stage registration and append-only review events in `.asdg/lifecycle.json`, under its recording contract. ASDG-02 retains its two-gate Purpose review allowance. No invented specialist readiness. |
| Sprint utilities | Explicit start/close requests permit the CLI transition of `.asdg/sprint.json`; close additionally creates a UUID JSON under `.asdg/sprint-closeouts/` and appends closure observations. Review is read-only. Sprint branch operations retain their existing human-directed preflight. |
| Generated coordinator advice | Existing `status --advise --verbose` writer may create only unique `02.1-status-*.md` reports and matching JSON receipts in Stage 07; it cannot overwrite planning documents. This is a utility allowance, not general Governance ownership of Planning. |
| Installation and synchronization | Existing explicit preview → approval → apply engines keep their exact reviewed-plan writes and preservation rules. Update/team setup keep their existing separately requested integration/chat capabilities. No generic file-write exception is inferred. |
| Runtime recorder | Existing reviewed/trusted logging hooks may write public activity summaries under `logs/`; this does not grant the acting role arbitrary log or shell writes. |

## Store and control limits

The checker supports OpenSpec stores within the project outside reserved `docs/`, methodology and control roots, with exact native-resolved artifact targets.
A configured external store, or one under a reserved root, needs its actual runtime's separately reviewed boundary; report the limitation and retain the resolved location. Never relocate artifacts to bypass a denial.
A supported custom store such as `planning/spec-store/` must come from actual configuration/native CLI evidence, not an arbitrary path selected to gain writes.
The optional Stage 07 OpenSpec navigation entry belongs to Planning: Specifications returns a proposed link in its own folder or a handoff.

Legacy provider baseline capture remains historical, outside the portable engine: its runner may preserve owner-authored bytes and run receipts only under that separately authorized trial contract; it grants no new generic agent exception.

No discovered workflow grants all roles unrestricted documentation or state access. New exceptions require bounded Admin maintenance and human review.
