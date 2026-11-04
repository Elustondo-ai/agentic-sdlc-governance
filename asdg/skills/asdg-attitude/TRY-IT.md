# Attitude and independent session fields — acceptance exercise

These are acceptance scenarios, not recorded passes. Use explicitly authorized test chats and their stable IDs.
Keep application files, sprint state, approvals and the working team's assignments unchanged.
The [session diagram and receipt](../asdg-focus/session-state.md) define the fields to observe.

## Core sequence

1. Select Architecture through the existing Focus command and record the actual role reads, project and user goal.
2. Select `subject Security`, then Black. Expect `05 Architecture Security`, then `05 Architecture Security Black`; record actual native outcomes.
3. Change Black to Green, then NoAttitude. Preserve role, Security, goal and history; distinguish computed and observed titles.
4. Select Black “for this answer only.” Apply it, restore NoAttitude before delivery and show both the attitude used and restored state; reconcile the title.
5. Select Yellow, then Green for a named review. On delivery restore Yellow; an explicit NoAttitude during that review cancels the pending restoration.
6. In a separately authorized Architecture chat select Performance and NoAttitude. Verify both receipts and stable IDs; changes in the first chat leave the second unchanged.
7. Resume or compact the first chat through an available native action. Report recovered fields and unresolved expiry from the retained receipt; if unavailable, mark unverified.

## Interpretation and failure cases

| Request or condition | Expected evidence |
| --- | --- |
| `actitud blanca`, `sombrero rojo`, `verde`, `amarillo`, `negra`, `azul`, `sin sombrero` in explicit selection context | Correct canonical color/NoAttitude; role and subject unchanged. |
| Explicit factual / creative / critical thinking attitude | Clear equivalents resolve; ambiguous wording prompts clarification. |
| “Explain Black,” a quoted command, or “make the diagram green” | No selection or rename. |
| `status` / `estado` | Read-only receipt; no rename or authority change. |
| Purple, conflicting hats or an unclear temporary endpoint | Preserve prior valid fields/title and ask a focused clarification. |
| A new selection supersedes a temporary hat | Old expiry cannot undo the newer selection. |
| Native rename unavailable, explicit failure, or inconclusive result | UNAVAILABLE, FAILED or UNKNOWN respectively; selection survives. |
| Native title already observed equal to computed title | UNCHANGED, supported by readback. |
| Native title clipping | Distinguish a preview from a stored-title change; preserve role identity and full subject in the receipt. |
| NoAttitude or legacy Off; subject NoFocus | Empty values remain in the receipt; omit them and the project suffix from the title. |
| Both optional fields unset / only focus / only attitude | `05 Architecture` / `05 Architecture Security` / `05 Architecture Black`. |
| Missing recovery evidence | Unknown fields, no authority reconstructed from the title. |
| Two same-role candidates in a routing request | Verify project, role, subject and ID; unresolved ambiguity is reported. |

Existing numeric, canonical and native role selectors and role-clear commands retain their meanings under the [Focus exercise](../asdg-focus/TRY-IT.md).
Role changes retain subject and attitude; even distinct titles require routing by verified stable ID and receipt.
New chats start NoAttitude unless explicitly assigned; they do not inherit the caller's attitude.

## Recording results

Record prompts, before/after fields, retained goal, actual reads, native results, stable IDs and protected-file hashes.
Use compact evidence, not private reasoning or full unrelated chat histories.
Separate actual native observations from modeled failure cases and source-level checks.
Do not alter tools, trust or runtime settings just to induce a failure; label unsupported native tests unverified.
Passing installation tests does not prove picker refresh, natural-language interpretation or native resume behavior.
