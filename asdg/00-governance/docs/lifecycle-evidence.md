# Authoritative lifecycle evidence index

`asdg init` creates `.asdg/lifecycle.json` without advancing or approving any stage:
```json
{
  "schema_version": 1,
  "stages": {}
}
```
Humans register project-specific evidence using two-digit canonical stage numbers:
```json
{
  "schema_version": 1,
  "stages": {
    "01": {
      "artifacts": ["docs/asdg/01-context-and-domain-analysis/context.md"],
      "not_applicable_reason": null
    }
  }
}
```
References must be repository-relative files in the corresponding stage folder.
Missing or empty referenced files leave the stage unmet. Unregistered files do not establish evidence.
Generated README placeholders, symlinks, traversal and references outside the stage are rejected.
Established means evidence is referenced and present; it does not mean complete or human-approved.
A file may contain uncertain or unreviewed evidence; quality review remains a human/role responsibility.
The index holds references, not a second copy of project context, intent or implementation content.

Only Stage 06 can be explicitly unnecessary, with an explanation and no artifacts:
```json
{
  "schema_version": 1,
  "stages": {
    "06": {
      "artifacts": [],
      "not_applicable_reason": "No experimental uncertainty requires a POC."
    }
  }
}
```
This does not skip preceding unmet stages. Other stages cannot be marked unnecessary.
Malformed existing indexes are errors and are not silently repaired by init.
Repeat init preserves registered evidence and active sprint state.
The guard protects this index from agent writes; humans establish authoritative evidence references.
The generated AGENTS bridge directs agents to shared status and recommendations without adding rules.
Exact previously generated bridges migrate on init; authored changes remain conflicts for review.
Existing consuming projects need a deliberate init/upgrade before the new structure verifies.
Optional `project_status` and `release` declarations: see [status metadata](../../../CODEX-SDK-PILOT.md).
