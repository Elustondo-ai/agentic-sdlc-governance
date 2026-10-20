AI-MODIFIED - 2026-10-14T20:14:22Z

# ASDLC baseline — standalone Codex sandbox correction

Recommendation: **READY FOR INDEPENDENT REVIEW**. Nothing staged or committed.
Methodology base/unchanged HEAD: `76542498451b45805aa5f14884413aee720ad6d4`; initial methodology tree was clean.

## Cause and bounded correction
Failed run `20261014T200637Z-544552583a` launched the helper through `~/.local/bin/codex` inside a HOME-denying profile.
That alias traverses `~/.codex/packages/standalone/current` to the versioned binary. The native control reproduces its exit 71.
Resolve file/directory symlinks strictly, invoke the canonical regular executable, and pass the same path to the profile and receipt.
Only that executable gets an explicit read exception; its system libraries use `:minimal`. No installation parent is granted read access.
Remove the unrelated Python-prefix read grant. HOME/temp denials, output-only writes, env filtering and disabled tool networking remain.
Missing, dangling, looping, directory and non-executable selections fail closed before capture logging.
The [official permissions contract](https://learn.chatgpt.com/docs/permissions) permits narrow path exceptions inside broader denials.

## Fresh verification
| Check | Result |
| --- | --- |
| Focused baseline suite, Python 3.15 | 34 passed; exit 0 |
| Complete governance suite, Python 3.11 | 157 run: 154 passed, 3 opt-in native skips; 0 failures/errors; exit 0 |
| Package structural validator | 13 packages/adapters valid; exit 0 |
| In-memory compile / Python 3.9 grammar | 27 governance Python files; exit 0 |
| Whitespace check | git diff --check; exit 0 |
| Actual macOS no-model probe | 11 cases passed using installed Codex 0.162.1; exit 0 |

[Exact test commands/results](verification.json); [native commands, outputs and postconditions](native-probe.json).
Native probe: original symlink without grant fails (71); resolved executable runs (0); snapshot reads and output write/read succeed (0).
Source overwrite/create/delete, context overwrite, home-canary read, synthetic-auth read and network bind all fail with OS permission errors (1).
Fixtures were mode 0600 (writable by this user), so source denial is sandbox enforcement; bytes stayed unchanged and fixtures were cleaned.
CODEX_HOME was disposable and credential-free. No real credential contents were accessed and no model/session was requested.
[Library inventory](runtime-libraries.txt) contains only system dependencies; no package/release directory exception was needed.
[Exploratory outcomes](investigation.json): nested sandbox restriction, rejected ad-hoc config, and canonical-control correction are retained transparently.
The earlier canonical-without-grant control succeeds on this CLI; the failure is specifically the unresolved launch alias.

## Review and preservation
[Bounded patch](corrections.patch); [changed-file hashes](changed-files.json); [repository/evidence preservation](integrity.json).
Production files: cli_baseline.py, test_baseline.py, probe_baseline_sandbox.py and baseline-safety.md; review files are separate evidence.
The failed receipt/log remain present; 174 pre-existing consumer and all 98 legacy entries match retained hashes; sprint remains inactive.
Integrity evidence records the two newer failed-run files separately, with current hashes, original failure metadata and pre-correction timestamps.
No live capture, commit, push, sprint change or approval was performed; consumer's two failed-run files remain untracked.
Repeat from the methodology root (macOS host must allow Seatbelt creation):
`python3 -B asdlc/00-governance/tests/probe_baseline_sandbox.py --repo "$PWD" --codex "$HOME/.local/bin/codex" --evidence-dir /private/tmp/asdg-runtime-probe-review`
This proves the installed standalone runtime and tested boundaries, not a live Coordinator session or every installation layout.
Script/npm wrappers needing extra runtimes remain fail-closed; no broad fallback permission is added.
STOPPED for independent review. Prior baseline/approval history is preserved.
