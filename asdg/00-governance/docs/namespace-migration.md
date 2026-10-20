# Migrating a project to ASDG

The namespace migration preserves an existing project rather than initializing another one.
It updates the reviewed provider binding, role identities and path references together.
The [identity map](../types/migrations/namespace-map.json) records the old and new names.

## Inspect and migrate

From the consumer repository, run `asdg migrate-namespace` to inspect the proposed changes.
Run `asdg migrate-namespace --apply` only for an explicitly authorized migration.
If the installed launcher points to the former source location, use the provider's `bin/asdg` with Python.
Updating the global installation is a separate operation; migration does not perform it.

Both old and new state trees, unknown catalogue hashes, linked sources and conflicting destinations are errors.
The supported baseline catalogue is retained solely as migration input, never as a second active catalogue.
The migration keeps project identity, initial binding history, sprint status, scope, criteria and decisions.
It maps lifecycle evidence references and retains historical report bytes and file permissions.
Its JSON receipt records old/new paths, hashes, original integration and state, and review events.
Repeat migration verifies the binding and does not initialize or reset state.

## Documentation layout

Each responsibility has `intended/`, `current/` and `planned/` under its project documentation folder.
These correspond to Intended, Actual and Planned; `current/` contains substantiated baseline records.
Historical captures move intact into `current/`; technical logs stay in the governance record area.
Empty perspectives remain empty until there is evidence or selected work to document.
The initializer recreates missing empty directories; it never treats them as stage completion.
Stage 07 integrates selected work; other Planned views reference it without creating competing schedules.

## Verify the boundary

Run `asdg verify`, inspect status and confirm the unchanged application implementation permission.
Renamed hook references require native review; this command neither grants nor assumes trust.
Native Codex discovery and execution require separate live tests.
Registry routing, global installation, permissions, application behavior and human approval are unchanged.
