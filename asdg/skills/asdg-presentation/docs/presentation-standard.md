# Presentation standard — v0.2

A presentation explains a coherent subject through readable source documents and useful visuals.

## Source contract

A presentation has one meaningful folder; its README identifies purpose, order, review state, sources, and build commands.
Each slide has a numbered, descriptive folder; the number is slide order, not lifecycle-stage numbering.
Each slide owns exactly one visual and one to three Markdown narration files, in a defined order.
The existing `speaker-text.md` or `speaker-notes.md` remains the introduction; never keep both.
For new layered slides, `speaker-notes-01-intro.md` may serve as the introduction instead.
`speaker-notes-02-walkthrough.md` reads and explains the meaningful contents of the visual.
`speaker-notes-03-details.md` adds examples, implications, caveats, and deeper explanation; it requires the walkthrough.
Keep existing sources and filenames; do not duplicate a visual to create a longer narration version.
All three parts are natural spoken text, not presenter instructions or bullet prompts.
Read [narration coverage](narration-coverage.md); length is not evidence of adequate explanation.
Follow [the documentation standard](../../../00-governance/docs/documentation-standard.md).
Keep units within 50 nonblank source lines; preserve spacing and split by topic, never minify.
Source references and review metadata are retained separately from spoken narration.
SVG is supported; PlantUML (`.puml`) and Mermaid (`.mmd`) remain allowed design formats with rendering pending.

## Local generated output

One ignored `build/` belongs beside the slide folders, not inside each slide.
The default `intro` profile uses the introduction alone and keeps the existing deck filename.
The explicit `detailed` profile assembles intro, walkthrough, and optional details in that order.
Every slide needs a walkthrough for a detailed build; missing material is an error, not silently omitted.
Detailed outputs use `-detailed` filenames and do not replace introductory outputs.
PPTX, previews, compiled narration, and manifests are derived artifacts, not authoritative sources.
One shared builder serves all decks; no existing PPTX is an input dependency.

## Verification

Validate numbering, source counts, ordered note files, nonempty narration, and supported formats.
Do not crop, stretch, or redraw the original visual during a build.
Record hashes for the visual and every selected narration source; preserve their bytes.
Reopen PPTX to verify slide counts and assembled narration; inspect visual rendering.
Flag raster-backed SVGs; introduction slides 01–04 remain preserved exceptions.
Mechanical checks do not prove semantic coverage, understanding, human approval, or authorization to publish.
