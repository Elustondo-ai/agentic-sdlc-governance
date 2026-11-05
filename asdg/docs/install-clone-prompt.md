# Clone + Prompt — human installation trial

Replace the three placeholders before pasting into Claude Code or Codex. Select a full commit containing this installer and a matching portable manifest; no fetch, checkout or commit is performed for you.
The [installation contract](installation.md) owns the engine and approval boundary. Local candidate testing does not approve a methodology release.

```text
Initialize ASDG in TARGET_PROJECT using my existing local canonical clone at CANONICAL_CLONE and exactly FULL_COMMIT_SHA.
Use that clone's asdg/skills/asdg-init/SKILL.md and the target's existing instructions.
Use Python 3.9+ and the clone's asdg/scripts/init.py; do not create a second installer.
Select --client claude in Claude Code or --client codex in Codex; ask if uncertain.
Inspect target Git root/status and record application-file hashes.
Run python3 "CANONICAL_CLONE/asdg/scripts/init.py" --source "CANONICAL_CLONE" --commit FULL_COMMIT_SHA --target "TARGET_PROJECT" --client CLIENT --dry-run.
Require verified canonical origin, exact HEAD, committed selected bytes and matching package integrity. Stop on mismatch; do not change the commit or refresh a manifest.
Show the complete file plan and generated diffs, including hooks. Copy only the selected portable distribution; never copy source .git, provider extras or project state.
Use the canonical asdg-init skill’s mandatory approval presentation, including a real complete-plan/diff reference and actual preview values.
STOP and wait for APPROVE for this exact plan; CANCEL stops, and ambiguous replies require clarification.
After I approve, repeat the identical options with --apply --plan TOKEN_FROM_PREVIEW.
From TARGET_PROJECT, run python3 asdg/scripts/cli.py verify --json; repeat the original preview for no further changes.
Report changed paths, preserved application/evidence and deterministic results separately from actual native tests and trust.
Report installation complete only on success, offer the optional Context survey, then STOP.
Never execute that survey or ask its questions without my separate affirmative response.
Do not overwrite conflicts, bypass hooks, grant trust, resolve promotion conflicts, commit, push, merge, tag, publish or start a sprint.
```

| Result | What the human should observe |
| --- | --- |
| Before approval | Commit and package verified, complete preview, no target writes |
| After approval | Only selected portable files plus generated target integration/scaffolds |
| Completion | Verified install, optional survey offered; no native-trust or release claim |
