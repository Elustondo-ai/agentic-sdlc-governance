# Conversational Focus — behavioral acceptance

One picker entry serves governance and twelve specialist roles. These scenarios are test requirements, not passing results.
Use disposable conversations and clients. File presence alone proves no native picker refresh, activation or title update.

## Interpretation cases

| Request/context | Expected behavior |
| --- | --- |
| “Focus on high level architecture” | Announce 05, load its canonical sources, then activate; no extra confirmation. |
| “Help me specify exact request fields and error contracts” | Resolve 08 from responsibilities, not the word architecture. |
| “Focus on testing,” with no task detail | Ask among plausible 04/09 choices, with a provisional recommendation and reason; preserve focus/title. |
| “We need benchmark coverage; focus on testing” | Resolve 04 from context when unambiguous. |
| “Focus on design,” with unresolved scope | Ask among the relevant design/model roles, not an arbitrary default. |
| “High levl architecure” | Interpret the ordinary spelling errors when the intent is clear. |
| No phrase or “focus on something useful” | Ask which specialist and list all twelve; Governance separately. |
| Explicit conflicting role IDs | Clarify; no role switch or rename before the answer. |
| User answers a pending clarification | Resolve that choice; retain the original task and load the chosen sources. |
| Unanswered or preselected recommended option | Remain pending; no activation or title mutation. |
| “Focus on our rules” or “fix the policy” with no Admin selector | Treat as a topic or proposal under the current role; never select Admin. |
| Explicit “return to general” | Return to 00 Governance after loading its sources, attempt its title; retain subject, attitude and goal. |
| `subject Security`, then `subject Performance` while Architecture is selected | Change subject only, retain role/attitude/goal and update the title with the real native outcome. |
| Select Specs / Coding / ReviewQA, or the corresponding legacy role names | Resolve 08 / 09 / 10 respectively; short labels do not change responsibilities. |
| `subject status` / `subject clear` | Report without mutation / explicitly clear subject only. |
| Quoted example or “explain Focus” | Explain only; no activation. |
| Numeric ID, canonical ID or native name | Preserve valid shorthand without requiring it. |

## Activation and integration

1. New chat: after its required reads, Status reports role 00 Governance, subject NoFocus and attitude NoAttitude; it does not rename.
2. Invoke Focus with “help me clarify the project's purpose”: load ASDG-02, attempt its title and begin the canonical read-only opening.
3. Status and a later role question retain Purpose; discuss a task without repeating activation.
4. Invoke Focus for Architecture: load 05 and attempt its title while retaining project context.
5. Ambiguous selection or missing role source preserves the previous focus and title; report the actual limitation.
6. Governance selects the coordinator; legacy clear also returns to it. Neither changes goal, subject, attitude or project state.
7. Rename failure preserves a successfully selected role; report the actual tool result and avoid blind retries.
8. Hide a Governance source: a new chat records role Unknown, reports `BLOCKED: GOVERNANCE_BOOTSTRAP` and performs no dependent work.
9. Resume with a valid specialist receipt keeps it; a legacy None receipt resumes as Governance; an unclear one blocks until reaffirmed.
10. New chat and legacy None migration each sync the title to `00 Governance` after the reads, or report UNCHANGED when it already matches.
11. “Switch to ASDG Admin” loads Admin and titles the chat `ASDG Admin`; selecting it alone changes no rule.
12. Under Governance or a specialist, a task blocked by an ASDG rule yields a proposal or question; the agent neither edits the rule nor selects Admin itself.
13. Test repeat selection, resume and compaction in the actual client before claiming their behavior verified.

Fresh installation exposes only `asdg-focus`; repeat setup neither recreates retired named picker entries nor changes lifecycle/sprint state.
Thirteen canonical role definitions and native role adapters remain; team setup uses the shared Focus path with explicit catalogue IDs.
An edited shared adapter remains a conflict, not permission for initialization to overwrite it.
A missing shared template or metadata, or a retired per-role Focus template, fails preflight before writes.
An older client may still contain retired adapters; inspect customizations and remove them only as an explicitly authorized migration.

## Evidence

Record original phrase/context, decision rationale, actual reads/rename outcome, previous/resulting role and subject, retained attitude/goal, and file effects.
Separate semantic interpretation tests from native activation, picker refresh, title behavior and hook enforcement.
Run the [Purpose continuation exercise](continuation-tests.md) separately; this change does not extend other specialists' opening procedures.
