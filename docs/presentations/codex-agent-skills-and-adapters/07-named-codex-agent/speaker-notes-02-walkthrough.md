# Named agent: a Codex TOML role, not a skill — Visual walkthrough

Read the example line by line. The name asdg_reviewer is the Codex runtime identifier. The
description explains when it should be delegated work.

The read-only sandbox requests a constrained environment. The developer instructions specify
how to inspect a candidate, return findings with evidence, and avoid staging or publication.
That is a reviewer responsibility, rather than a general presentation or component-creation
procedure.

Codex's name field, not the filename, is the runtime identity; matching them reduces
confusion.
