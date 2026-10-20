# ASDG refactor status

The provider now uses ASDG for people and `asdg` for its technical namespace.
Speaker Coach’s state and living documentation have migrated without changing application behavior.
The presentation exporter integration remains pending, so this pass is not fully complete.

## Changes and evidence

The launcher lives at `bin/asdg`; reusable implementation lives under `asdg/`.
All thirteen role definitions and native TOML identities pass structural validation.
Purpose uses `02-purpose/`; every stage has `intended/current/planned` views.
The normal initializer creates the same layout and preserves content and state on repeat runs.

The [documentation standard](../../asdg/00-governance/docs/documentation-standard.md) requires readable source and rendered prose.
Its shared counter permits 50 nonblank source lines and ignores blank or whitespace-only lines.
Review declarations remain attached to their original document hashes in technical history.
Historical capture reports retain their original wording and evidence limits.

The governance suite passed 240 tests with four native integration skips; three component tests passed.
Preservation checks found no changes in 115 provider records and 85 Speaker Coach historical files.
Speaker Coach’s application files still match its existing commit.
The [technical record](purpose-perspectives-change-2026-10-19.json) retains exact results, limitations and migration references.

## Remaining dependencies

Speaker Coach’s authorized namespace sprint is active only for `docs/presentations/`.
Its exporter changes await confirmation of an active trusted native hook.
The [prepared patch](../../asdg/00-governance/types/migrations/speaker-coach-exporters.patch) is reviewable and unapplied.
Rebuilding the historical review also requires its missing original capture receipt and archive.

The global launcher still needs a separately authorized installation update; use local `bin/asdg` meanwhile.
Registry routing is unchanged. Native discovery, execution and hook enforcement remain unverified.
Full presentation tests require missing Python dependencies; native preview conversion also has documented limits.
No edits were committed, pushed, deployed or marked human-approved.
