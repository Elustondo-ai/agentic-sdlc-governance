AI-MODIFIED - 2026-10-14T20:13:21Z

# Baseline isolation and validation

Baseline agents use an ephemeral named `asdg_baseline` permissions profile.
Its default root, home and broad temp reads are denied; platform/runtime paths and the isolated
snapshot are readable. Only that invocation's `output/` subtree is writable.
The selected Codex executable is resolved through symlinks, invoked by its canonical path and granted exact-file read access.
Standalone Codex uses `:minimal` system libraries; no HOME, `~/.codex`, release-directory or unrelated Python-prefix read grant is added.
Explicit temp denials matter: the macOS probe found root-deny alone left a temp canary readable.
Both source-write denial and outside-canary read denial were verified with actual Codex Seatbelt
probes. No hook-trust bypass or global configuration/registry change is used.

Each Codex process receives root instructions, actual role/contracts, local and shared documentation skill,
runtime contract, lifecycle baseline, assigned objective and prior-stage context.
Apps, MCP servers, browser/computer use, web search, additional agents and command networking
are disabled per invocation. Login shells are disabled; approval policy is never.
These settings affect only the child invocation; existing consumer hooks and sprint policy remain.
Processes and their tool environments use explicit whitelists, not unrestricted parent inheritance.
Authentication uses persisted login; environment-only API keys/tokens are not forwarded.
See [environment/provenance/execution contract](baseline-validation-r01.md).
Official interface: https://learn.chatgpt.com/docs/permissions

The runner fingerprints protected workspace files AND directory/mode changes; it rejects changes
outside output/ before promotion. Source files are copied only after matching inventory hashes.
The canonical binding, sprint, lifecycle index, AGENTS bridge and hook files are checked unchanged.
Failure logs preserve emitted sessions and actual end times. Timed-out process groups are stopped.

## Artifact validation
- Only numbered topic directories, each with exactly visual.* and speaker-notes.md.
- No unauthorized files, nested directories, symlinks, hardlinks or oversized/empty artifacts.
- Notes must be UTF-8, <=50 physical lines, have a valid current invocation AI-MODIFIED stamp,
  match the assigned Agent identity and state Sources, Uncertainties and Contradictions.
- Declared/recognized snapshot references must resolve; unsupported reference-style citations fail closed.
- Common secret payloads and manufactured approval markers are rejected.
- Common SVG active/external constructs, Mermaid directives/clicks and PlantUML includes are rejected.
- Safe Mermaid comments and supported diagram declarations are accepted, not rewritten.
- Promotion preserves bytes; the receipt associates each artifact hash with its owner/session.

## Limits
This is not a complete visual-language parser or semantic reviewer. Evidence truth, diagram
meaning and unresolved contradictions require review. Common-secret detection is conservative,
not exhaustive; review unusual sensitive source material before capture.
Read restrictions were verified against synthetic canaries, not by attempting to expose secrets.
Managed/runtime policy may further restrict the profile; incompatible hosts fail rather than
falling back to broad writes. Windows execution is not established by this Mac/Linux implementation.
No automatic retention, deletion, evidence approval or lifecycle completion is inferred.
The repeatable no-model check is `tests/probe_baseline_sandbox.py` (macOS); see the [runtime-fix review](../../../docs/reviews/asdlc-baseline-runtime-fix/README.md).
