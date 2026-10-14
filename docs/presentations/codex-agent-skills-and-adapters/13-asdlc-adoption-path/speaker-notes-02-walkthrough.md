AI-MODIFIED - 2026-10-09T14:33Z

# ASDLC adoption: implement, inspect, then extend — Visual walkthrough

The sequence begins by keeping our two canonical ASDLC skills as they are. Next, add the
missing component-creation adapter to the common .agents/skills directory. Define one
reviewer role with explicit inputs, evidence, and prohibited effects.

Translate that responsibility into native Codex TOML, Claude Markdown, and Copilot agent
profiles. Exercise the same harmless review fixture in each runtime, checking whether it
finds the right material and avoids forbidden actions. Only after review should we treat a
platform adapter as accepted.
