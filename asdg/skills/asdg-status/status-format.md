# ASDG status format

Fill this template from observed evidence and this conversation; angle brackets are placeholders.
The sample values below are not facts about the current session.

```text
ASDG SESSION STATUS

Active focus:    <None / selected role and stage / Unknown>
Role ID:         <actual canonical role ID, or None / Unknown>
Activation:      <successful explicit selection / cleared / none / unknown>
Title update:    <last observed rename outcome and title, or Not attempted / Unknown>
Target project:  <verified or supplied project, otherwise Unknown>

Role definition: <canonical path actually read, with purpose of read>
Procedure:       <procedure actually read; loaded is not executed>

Responsibility:  <canonical responsibility, or general ASDG assistance>
Boundaries:      <actual role/evaluation boundaries and their evidence>
Current task:    <latest substantive task, or Awaiting assignment>

Runtime settings: <observed configuration, otherwise Not inspected>
Evidence:         <actual read evidence and any important gap>
```

Keep this compact. Show a failure line only when a recent focus attempt failed.
No role: do not mark a Purpose definition as loaded merely because it exists.
Selected role: identify this as conversation focus, not a newly spawned subagent.
Mention inspection-only reads separately from activation evidence.
Do not expose account identifiers, tokens or private reasoning in status.
For status questions, this report is the human-readable result; do not add a second redundant envelope.
Respect required canonical failure fields for BLOCKED or OUT_OF_SCOPE responses.

Title update is the last retained action receipt; state separately whether the current UI title was verified.
Status never renames a conversation or reconstructs a missing receipt from the selected role.
