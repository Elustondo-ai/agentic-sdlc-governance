AI-MODIFIED - 2026-10-09T14:33Z

# Compatibility is measured, not assumed — Deeper explanation

Our acceptance suite should verify five boundaries: discovery, invocation, tool
availability, side-effect authorization, and evidence. We can begin with a harmless
task—create a component scaffold in a temporary test repository or review a fake diff—then
compare outputs.

Record the runtime versions and precise paths used. A failed discovery test should be
reported as a failed adapter, not papered over with a manually pasted prompt.
