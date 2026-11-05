---
name: asdg-publish
description: Publish a verified portable ASDG ZIP and checksum from the canonical agentic-sdlc-governance provider, with matching release metadata and installation instructions. Provider-only; never use in an adopting project.
---

# Publish ASDG from its canonical provider

Use when Pablo requests `asdg publish` in this repository. This is an agent workflow, not an installed `asdg` terminal subcommand.
This skill is provider-only, excluded from `metadata/package-files.json`, client ZIPs and generated client adapters. Keep the provider's existing disabled discovery entries disabled.

## Establish scope

Resolve the Git root and verify its origin is `Elustondo-ai/agentic-sdlc-governance`, its provider root instructions and `scripts/prepare_commit.py` exist, and this skill is not in the portable file list. Stop in a client or ambiguous checkout.
Read root `AGENTS.md`, the [Admin contract](../../admin/AGENTS.md), [distribution build](../../docs/distribution-build.md) and [synchronization contract](../../docs/synchronization.md).
Require explicitly selected ASDG Admin and a bounded human publication request; a build, commit, status request or prior publication is not release authorization.
Record Git status/revision, preserve unrelated work and identify the exact source changes to publish. Existing authorization persists within its scope; ask only for missing authority.
Publication authorization does not silently cancel an explicit reservation of commits/pushes for the human. Prepare the concrete candidate first, then resolve that reservation before a required commit/push.

## Prepare one versioned candidate

Read current metadata and published releases. Select the next unused pilot/version appropriate to the requested change; preserve published tags and assets rather than overwriting them.
Preserve the previous actually shipped manifest from its published tag in `asdg/metadata/deliveries/<version>.json`; do not mistake a locally refreshed candidate for that delivery.
Keep `metadata/distribution.json`, `scripts/lib/cli_model.py` and its companion consistent. Record the source baseline and previous version; add historical manifests to the reviewed portable file list.
Update root README installation ZIP, checksum and release links to the selected version. Reconcile other active version references while preserving historical reports and presentation downloads.
Append exact-hash documentation receipts and save a bounded Stage 07 maintenance report/JSON receipt listing changed paths, authority, actual verification and remaining limits. Publication never adds PME-APPROVED or implies documentation acceptance.
Run `python3 scripts/prepare_commit.py`, then `python3 asdg/scripts/check.py --integrity` and the applicable portable/provider tests. Inspect the ZIP's single `asdg/` root, manifest, install prompt, version and checksum.
Confirm this provider-only skill, provider scripts, client state, credentials and application evidence are absent from the ZIP. Generated ZIPs/checksums stay under ignored `build/distributions/`.
If candidate files change, regenerate and recheck before committing or uploading. Stop on failed required checks; report the actual failure.

## Publish and verify

When authorized, commit only the prepared release changes, push them, and bind the new GitHub tag to that exact full commit. Never include unrelated work or move an existing tag.
Prefer sufficient connected GitHub tools; if release creation or binary upload is unavailable, use the signed-in GitHub browser release UI without extracting credentials.
Create a prerelease for a pilot. Upload the verified ZIP and `.sha256` sidecar, using fresh UI state and the supported file chooser. Preserve all older releases and their assets.
Release notes identify source commit, installation links, actual checks and material limitations; do not claim native discovery, hook trust or interception from structural tests.
Publish only after uploads complete. Verify the public tag/commit, asset names/sizes/digest and download links; compare the remote ZIP digest to the local SHA-256 and verify the public README points to those assets.
If upload/publication fails, preserve successful work and report the exact remaining action; do not claim an attempted or draft release was published or delete old assets as a retry.
Report the release URL, ZIP/checksum URLs, source commit, verification, instruction update and uncommitted leftovers. Never change deployment, credentials, hook trust, client state or discovery activation as a side effect.
