# Configuration, tools, and enforcement are separate — Deeper explanation

Some settings depend on the CLI, IDE, trust state, and Codex version. We must test the
actual surface instead of assuming the presence of a config file proves it was loaded.

Store secrets outside the repository. For evolving functionality, start with read-only or
assessment-only modes, then add explicit effectful operations and failure tests.
