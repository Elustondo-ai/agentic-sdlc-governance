# Human-readable source companions

Every maintained programming source file has a Markdown companion beside it.
This applies to application code, embedded tooling, scripts and tests: Python, TypeScript, JavaScript and other maintained languages.
Generated code and third-party dependencies are excluded; document the maintained generator or integration boundary instead.
Use the same stem, such as `example.py` → `example.md`.
If multiple source extensions share a stem, use unambiguous names such as `example.py.md` and `example.ts.md`.
Preserve an existing useful companion rather than replacing it with a template.

## Explain the component as an engineer would

Use Class–Responsibility–Collaborator (CRC) thinking for a class, module, script or component; do not invent classes where none exist.

| Reader's question | What the companion explains |
| --- | --- |
| Why does it exist? | Purpose, owning responsibility and important boundaries. |
| What can I call or supply? | Public classes, types, functions, signatures, inputs, defaults and required data shapes. |
| What happens? | Results, mutations, files/network/process effects, errors and relevant ordering or timing. |
| Who does it work with? | Concrete collaborators, their roles and links to their interface guides. |
| How do I use it? | A small realistic example and its prerequisites. |

Include important internal functions when they explain behavior or constraints; distinguish them from supported public entry points.
For tests, explain fixtures, helpers, covered behavior and how to run them; simulated acceptance is not real approval.
For executable scripts, stdin, stdout, arguments and exit codes are interfaces even when no functions are exported.
For untyped code, describe observed data shapes and clearly distinguish inferred types from declared types.

## Visual first, technical detail beneath

Embed a small collaboration or data-flow diagram, or a CRC table, that explains the component at a glance.
Keep names consistent with the implementation and show who calls whom or how data moves.
Use the surrounding prose as supporting explanation, with enough precision to use the interface correctly.
A signature list alone is insufficient; explain the contract and why collaborators are involved.
Keep diagrams editable and readable in the rendered Markdown; retain accessible image descriptions.
Split larger references into linked topics, keeping the same-name companion as the entry point.

## Keep the explanation trustworthy

Read the current implementation and relevant callers before writing; do not infer behavior from filenames alone.
Update the companion in the same change when responsibilities, interfaces, types, collaborators or effects change.
On a source rename/delete, reconcile the companion and incoming links.
Check coverage and links separately from technical accuracy; file presence never proves completeness.
Record exact-hash documentation changes under the existing review convention; do not transfer old approval.
Historical reports retain their original evidence and dates; a new explanation may link to them.
