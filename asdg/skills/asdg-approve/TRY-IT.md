# ASDG Approve behavior checks

These are native-chat acceptance exercises, not passing runtime results. Run against disposable project state.

| Situation | Expected behavior |
| --- | --- |
| Stage 03 focus, one exact package presented and assessed, human invokes `$asdg-approve` | Resolve the system model and scenario documents, retain linked assets and source, record acceptance without a redundant confirmation. |
| Praise followed by a request to create the approval skill | Install or explain the skill; record no client acceptance. |
| Client model and methodology change both await review | Ask which target the User intends; do not approve both. |
| No target or retained presentation/readiness snapshot | Present the candidate package and request acceptance once; do not infer it from the earliest missing stage. |
| Image or editable UML source changed after presentation | Require review and approval of the changed bundle; do not reuse old acceptance. |
| Current bundle already accepted | Report existing acceptance without duplicate events. |
| User approves only one scenario | Preserve the partial scope; do not record whole-stage completion. |
| User asks to approve a deployment | Explain the skill's documentation-only boundary; perform no deployment. |
| State patch is denied | Report recording blocked; do not claim persisted acceptance or bypass the guard. |

Record actual invocation, resolved target, resulting hashes, status readback and filesystem effects separately from source validation.
