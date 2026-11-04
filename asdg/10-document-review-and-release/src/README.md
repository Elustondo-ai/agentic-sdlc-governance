# Document, Review and Release Agent — implementation

The current agent capability is instruction-driven; its procedure lives in `../skills/review-readiness/SKILL.md`.
No stage-specific execution engine is claimed by this scaffold.
Shared lifecycle operations remain under `asdg/scripts/lib/`; client implementation stays outside the distribution.
Future code must have explicit contracts and tests and remain within the package responsibility.
