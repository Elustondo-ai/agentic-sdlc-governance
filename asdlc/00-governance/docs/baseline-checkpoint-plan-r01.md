AI-MODIFIED - 2026-10-14T16:14:00Z

# Proposed clean pre-experiment checkpoint — approval required

Observed consumer: clean `main`, 52 tracked files, no untracked files; one local commit
`a7411af03bfe87c417d631224f8d9737a7777fbc` already contains both trial receipts/docs/logs.
It is a post-experiment checkpoint, not a clean pre-experiment baseline. Remote state was not queried.
Sprint is inactive; source is the existing sibling-of-parent `meetingHelper` directory.
Keep this consumer and legacy repository intact. Do not reset or remove their evidence.
After R02 acceptance and a separately authorized methodology commit, use a pinned method worktree
plus a NEW consuming repository; this avoids inheriting the existing trial artifacts.
The proposed operations below have NOT run and require Pablo's authorization before execution.

From the `elustondoai` workspace, substitute the actual accepted final methodology commit:
```sh
asdg_provider="$PWD/agentic-sdlc-governance"
asdg_method_sha='<ACCEPTED_FINAL_METHOD_COMMIT>'
asdg_pinned_method="$PWD/asdg-r02-pinned-method"
asdg_fresh_consumer="$PWD/agentic-speaker-coach-r02-pre-experiment"
test ! -e "$asdg_pinned_method" && test ! -e "$asdg_fresh_consumer" || exit 1
git -C "$asdg_provider" cat-file -e "$asdg_method_sha^{commit}" || exit 1
git -C "$asdg_provider" worktree add --detach "$asdg_pinned_method" "$asdg_method_sha" || exit 1
mkdir "$asdg_fresh_consumer" || exit 1
git -C "$asdg_fresh_consumer" init --initial-branch=main || exit 1
cd "$asdg_fresh_consumer" || exit 1
python3 -B "$asdg_pinned_method/asdg" init || exit 1
python3 -B "$asdg_pinned_method/asdg" verify || exit 1
python3 -B "$asdg_pinned_method/asdg" baseline capture --source ../../meetingHelper --dry-run --json > .asdlc/baseline-input.json || exit 1
python3 -B - <<'PY'
import json
from pathlib import Path
assert json.loads(Path('.asdlc/sprint.json').read_text())['status'] == 'inactive'
assert not list(Path('docs/asdlc').rglob('*__baseline-run.json'))
assert not list(Path('docs/asdlc').rglob('*__baseline-capture__*.md'))
assert not list(Path('docs/asdlc').glob('*/baselines'))
PY
test "$?" -eq 0 || exit 1
git add -- .asdlc/project.json .asdlc/sprint.json .asdlc/lifecycle.json .asdlc/.gitignore .asdlc/baseline-input.json
git add -- .codex/config.toml .codex/hooks.json AGENTS.md docs/asdlc/README.md docs/asdlc/*/README.md
git commit -m "Record clean ASDLC pre-experiment checkpoint"
```
Review the staged files before approving that commit; this plan itself grants no Git authority.
Record the resulting consumer commit, accepted method commit and original source inventory digest.
Before any separately authorized future experiment, compare the current source digest with this input.
Use the pinned method entry point and same Python; the existing hook verifier binds interpreter paths.
If creation fails, preserve the partial fresh folder for diagnosis; do not clean or overwrite it.
No hook trust, sprint start, legacy import or model capture is part of this checkpoint proposal.
