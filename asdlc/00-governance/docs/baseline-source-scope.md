AI-MODIFIED - 2026-10-14T16:14:00Z

# Baseline source scope — textual snapshot

The current reader inventories the filesystem as UTF-8 text without executing legacy code.
Source images, screenshots, PDF/office documents, compiled assets and other binary material
are excluded rather than interpreted. Output diagrams/images are permitted; that does not
mean the source reader can inspect binary images supplied by the legacy project.
Textual SVG, PlantUML and Mermaid are eligible when safe, bounded and credential-free.

VCS metadata directories and `.git` pointer files are excluded.
Commits, branches, authorship, diffs, prior versions, deleted files, blame and remote state
are not analyzed. A present-day textual snapshot cannot establish the system's history.
Static source declarations are not execution, deployment, performance or acceptance evidence.

Private configuration/credential names, common inline secrets, symlinks, dependency/build
caches and unreadable or oversized files are also excluded with explicit reasons.
Current bounds: 500 eligible files, 2 MiB per file, 20 MiB total.
The exclusion list is evidence of reader limits; it is not proof excluded material is irrelevant.
Credential-pattern detection is conservative and incomplete; sensitive inputs need human review.

The Speaker Coach trial supplied 22 eligible textual files and excluded the `.git` directory.
Its recorded 45/75 versus 25/35-second discrepancy is a static source/document contradiction,
not a new runtime measurement. No binary source or VCS-history understanding is claimed.

Future option: separately authorized, bounded image/document extraction and read-only history
analysis with provenance, privacy controls and tests. This correction adds neither subsystem.
See [baseline contract](baseline-capture.md) and [R01 validation](baseline-validation-r01.md).
