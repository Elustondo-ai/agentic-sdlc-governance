# Codex installation prompt

Use the copy-ready [ZIP + Prompt](docs/install-zip-prompt.md) after extraction, or [Clone + Prompt](docs/install-clone-prompt.md) with an explicitly selected local commit.
Both call the same Python engine through [ASDG Init](skills/asdg-init/SKILL.md). In Codex select `--client codex`; the same prompts in Claude Code select `--client claude`.

| Step | Boundary |
| --- | --- |
| Preview | Integrity and preflight, all planned files and generated diffs |
| Approve | Wait for explicit developer approval of the exact plan |
| Apply | Identical options plus `--apply --plan TOKEN`; rollback and verification |
| Complete | Report results, offer optional Context survey, wait for a separate yes |

No prompt performs file synchronization itself, runs Context automatically, grants trust, starts a sprint or commits/publishes work.
