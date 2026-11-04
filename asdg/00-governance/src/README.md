# Historical provider runtime

This retained implementation predates the portable consolidation. Current entry points use `asdg/scripts/lib/`.
Installer, namespace migration and baseline capture need separate compatibility work; they are excluded from the core ZIP.
The material below records the earlier provider layout.

# ASDG Coordinator — implementation

The current agent capability is instruction-driven; its procedure lives in `../skills/review-routing/SKILL.md`.
`validate_agents.py` checks package structure and references; it never invokes agents or changes sprint state.
Shared software remains under `../../components/`; do not duplicate it here.
Future code must have explicit contracts and tests and remain within the package responsibility.
