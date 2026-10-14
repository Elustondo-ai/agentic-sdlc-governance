AI-MODIFIED - 2026-10-08T23:34Z

# Narration contract

A slide has one authoritative visual and an ordered sequence of one to three narration parts.
The first part introduces it. The second walks through the visual. The optional third adds explanation.
Existing single-file introductions remain valid; ambiguous duplicate introductions are invalid.
A details part without a walkthrough is invalid.

The build request selects one presentation and a profile: `intro` or `detailed`.
`intro` selects only the first part. `detailed` selects all parts in order and requires a walkthrough on every slide.
The build result identifies the derived PPTX, manifest, slide count, and warnings.
Every selected source must be unchanged during the build; its hash is recorded.
Missing sources, unsupported formats, invalid ordering, and unsafe paths produce errors.
No output may silently overwrite the other profile's files.

This is the language-neutral meaning; `contracts.py` and the builder are its current Python representation.
Python is allowed for this component, not imposed on other ASDLC contracts.
