# Authoritative sprint state

Location: `.asdg/sprint.json`. Exactly these fields are accepted; initial and stopped state:
```json
{
  "status": "inactive",
  "sprint_id": null,
  "objective": null,
  "scope": [],
  "acceptance_criteria": []
}
```
Active example:
```json
{
  "status": "active",
  "sprint_id": "SPRINT-001",
  "objective": "Hello endpoint",
  "scope": ["app.py"],
  "acceptance_criteria": ["GET /hello returns hello world"]
}
```
Starting requires a valid inactive state, non-empty ID/objective, scope and criteria.
Stopping clears all fields to the initial inactive state. Repeat init preserves active state.
A missing state file is blocked; init can create the missing inactive state.
Malformed existing state is a conflict and is never silently overwritten.

Inactive implementation guard output (exit 1):
```text
IMPLEMENTATION BLOCKED
No active ASDG sprint is defined.

Recommended next action:
Define project context and domain boundaries.
```
Outside-scope example (exit 1):
```text
IMPLEMENTATION BLOCKED
Requested path is outside active sprint scope: other.py
```
Allowed targets (exit 0): `Implementation allowed.`
Blocked CLI/hook responses include the evaluator's current recommendation, not independent advice.
Normal inactive status: `No active sprint.` Active status:
```text
Sprint SPRINT-001 active.
Objective: Hello endpoint
ALL GOOD!
```
