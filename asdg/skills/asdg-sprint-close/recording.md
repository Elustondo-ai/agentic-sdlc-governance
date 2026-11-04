# Preserve a sprint closeout

This technical receipt retains evidence before the CLI clears active sprint fields; it is not another state authority.
Explicit human use of Sprint close permits creating one receipt and appending its observed closure result.
Only `.asdg/sprint.json` determines current implementation scope; a receipt cannot authorize work or restore a sprint.

## Destination and content

Use `.asdg/sprint-closeouts/<uuid>.json` with a fresh generated UUID; do not derive paths from untrusted sprint IDs.
Create only that file with a scoped patch, respecting runtime permissions. Reject symlinked destinations and never replace an existing receipt.
Use this JSON shape, with actual values rather than placeholders:

```json
{
  "schema_version": 1,
  "prepared_at": "<UTC timestamp>",
  "sprint_sha256": "<SHA-256 of the exact active sprint.json bytes>",
  "sprint_snapshot": {"status": "active", "sprint_id": "...", "objective": "...", "scope": ["..."], "acceptance_criteria": ["..."]},
  "review": {
    "assessed_at": "<UTC timestamp>",
    "revision": "<observed Git revision or null>",
    "working_tree": "<observed relevant changes and attribution limits>",
    "criteria": [{"criterion": "<exact criterion>", "result": "PASS|FAIL|UNVERIFIED", "evidence": ["<reference>"], "gap": "<gap or null>"}],
    "limitations": ["<evidence or independence limit>"]
  },
  "outcome": "completed|unfinished|cancelled",
  "carry_forward": ["<unfinished item>"],
  "human_decision": "<actual closure request>",
  "closure_observations": []
}
```

Every snapshot criterion must appear exactly once, in order. `completed` requires all results PASS with concrete supporting evidence.
Preserve command outcomes and reviewed references, not secrets, full logs or private reasoning. Use null for unknown revisions.
Read the file back, parse its JSON and verify its snapshot against the exact active bytes/hash before invoking stop.
No new human acceptance is inferred: `human_decision` authorizes ending the sprint only.

## Record what actually happened

After the stop attempt, append an observation with `observed_at`, `command`, `exit_code` (or null), `observed_state` and `result`.
Use `result: closed` only after command success and verified inactive readback; otherwise record failed or uncertain with the actual evidence.
Preserve the snapshot, review and earlier observations; reread the receipt before a scoped append to avoid overwriting concurrent work.
If preparation fails, leave the sprint active. If stopping succeeds but final recording fails, report both facts and retain the prepared receipt.
For retries, reuse a known matching prepared receipt after inspecting current state; never treat its presence as proof the CLI ran.
Closing an already inactive sprint creates no duplicate event. A later correction is an appended observation, not rewritten history.
These rules do not change the CLI schema, hooks, lifecycle acceptance or application-file permissions.
