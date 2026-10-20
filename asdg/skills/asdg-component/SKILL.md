---
name: asdg-component
description: Scaffold and validate an ASDG software component with standard docs, types, src and tests directories and twelve lifecycle stages.
---

# ASDG component skill

Use when creating a new ASDG component, not for ordinary directories.

1. Confirm the component name, repository-relative destination, and scope.
2. Read `docs/component-standard.md` and the current official stage names.
3. Run `src/create_component.py` with the repository root and component name.
4. Check the generated structure with `--check`.
5. Add component-specific context and contracts only after the scaffold; preserve existing files.
6. Report any incomplete stages and distinguish creation from implementation, testing, approval, commit or push.

Do not overwrite a populated component or infer permissions from this skill. Keep the YAML front matter first for skill discovery; any PME status conflict must be handled outside the SKILL.md header without claiming approval.
