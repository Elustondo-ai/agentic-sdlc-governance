# Build and verify the portable distribution

The canonical repository produces one ZIP with one top-level `asdg/` folder.
The recommended [repository-URL Quick Start](https://github.com/Elustondo-ai/agentic-sdlc-governance#quick-start--give-your-agent-the-repository-url) delegates acquisition and initialization to an agent; manual extraction and a pinned clone remain alternatives.

![The provider selects portable files, validates hashes and builds a ZIP; the client extracts it and initializes local integrations and state.](images/distribution-flow.svg)

## Developer installation

Python 3.9+ and Git are required. From the client repository root:

```sh
python3 asdg/scripts/init.py --client codex --dry-run
# After explicit approval of that plan:
python3 asdg/scripts/init.py --client codex --apply --plan TOKEN_FROM_PREVIEW
python3 asdg/scripts/cli.py verify
```

Choose `codex`, `claude` or explicitly `both`; preview is the default.
A pinned local canonical clone uses the same [installation engine](installation.md).
Existing project guidance and state are preserved; conflicts stop setup before writes.
Repeat initialization creates no duplicate adapters or workflow state.
No global launcher, sibling checkout, download or model call is needed for setup.
Codex hook trust and native invocation require separate local observation.

## Maintainer build

The selected package includes `skills/asdg-init/SKILL.md`, the single owner of the approval presentation contract; verify the built ZIP contains its exact reviewed bytes.
Version `0.3.0-pilot.3` packages Status-owned onboarding, Help, Update and stable team ordering; preserve existing pilot.1 and pilot.2 assets. Publication requires explicit human authorization.
Review `metadata/package-files.json`, the explicit portable file list, when adding a capability.
Repository-only presentation tools, legacy provider code, application evidence and builds are excluded.
Before every commit/push, after changes and documentation receipts are ready, run from the provider root:

```sh
python3 scripts/prepare_commit.py
python3 asdg/scripts/check.py --integrity
python3 -B -m unittest discover -s asdg/tests -v
```

The provider-only wrapper refreshes the manifest through the existing builder and writes a ZIP and SHA-256 sidecar under ignored `build/distributions/`.
Review/include the refreshed manifest in your commit; re-run after further package edits. No hook is installed; commit, push and publication remain human actions.
The ZIP contains working-tree bytes. Regeneration replaces the local same-version artifact; it does not increment the version, and unchanged inputs produce identical bytes.
Stable file order, timestamps and permissions make repeated local builds byte-identical.
Without `--refresh-manifest`, changed or missing package bytes fail the build.
The manifest binds content, not approval; historical delivery manifests stay unchanged.
Source repository commits and the candidate version live in `metadata/distribution.json`.

## Upgrade and compatibility boundary

This candidate supports fresh embedded installations, repeat setup and [reviewed local promote/upgrade](synchronization.md).
Existing linked providers still require explicit migration. Version upgrades use an adoption record; init does not silently change versions.
Synchronization preserves `.asdg/`, client documents, installed adapters and hooks; changed templates need separately reviewed integration work.
The provider's `bin/asdg` delegates to the embedded runtime; machine-wide installation is retired from that entry point.
Historical installer, namespace migration and baseline code remain in the provider for separate reconciliation.
The preserved presentation/component tools are outside this core package and its acceptance claim.
Publishing an artifact and granting exact-state human acceptance are separate decisions.
