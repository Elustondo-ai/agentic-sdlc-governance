AI-MODIFIED - 2026-09-28T15:00Z

# SDLC2 — Formalization Gradient: Slide Plan

**Scope:** Eleven main slides plus two optional technical annex slides. Pablo authorized production of the complete set on 28 September 2026, with review afterward.
**Purpose:** Explain how domain meaning becomes explicit, checkable and executable, and ground it in SDLC2 governance and Codex mechanisms.
**Source:** Formalization_Gradient_in_Agentic_AI_Software_Development.docx (28 September 2026), plus the subsequent discussion and corrections.
**Destination:** [Current SDLC2 presentation folder](https://drive.google.com/drive/folders/1acmDtyNTpuNj3hPjMmhbNgvd41SL9dcc).
**Numbering:** FG01–FG09 plus inserted FG03a and FG05a are chapter-local planning IDs. Proposed deck positions 13–23 follow the current twelve slides; final placement remains adjustable. A1/A2 below are local technical-annex IDs, separate from reference slides R01/R02.

## Main sequence

| ID / proposed position | Title | Visual concept | Spoken narration objective |
| --- | --- | --- | --- |
| FG01 / 13 | How much should we formalize? | The same sprint-completion request shown as prose, a structured contract and an executable operation. | Introduce a concrete problem immediately: selecting a representation is an architectural choice with practical consequences. |
| FG02 / 14 | The formalization gradient | A compact spectrum from prose through defined vocabulary, records and contracts to executable behavior. | Explain progressive precision; retain prose for intent and judgment. These forms can coexist rather than replace one another. |
| FG03 / 15 | Domain-Specific Language: Giving Our Concepts Precise Meaning | Vocabulary, rules of expression and meaning/constraints, illustrated by Sprint, Evidence and Approval; annotate an illustrative ReadyForReview request. | Define a DSL, distinguish it from a glossary, and explain its SDLC2 role: connect human intent, agent interpretation and verifiable action. Formal syntax alone grants no authority. |
| FG03a / 16 | LifeBuckets: a personal assistant | Architecture diagram connecting UI/chat, cloud agent, Google Drive and everyday apps. | Introduce the open-source personal assistant and its life domains before its first mention. Distinguish target architecture from completed integrations. |
| FG04 / 17 | When “Person” becomes a defined concept | One illustrative Person concept traced through a domain definition, UML model, type signature and validation rule. | Show how a defined term can appear within ordinary English while retaining its agreed meaning. Label the example as illustrative, not an assertion about the current LifeBuckets model. |
| FG05 / 18 | Three languages working together | Three interacting domains with concrete examples: LifeBuckets product concepts; SDLC2 stages, evidence and approvals; Codex operating mechanisms. | Separate what we build, how we govern development and how the agent receives and executes work. Preserve SDLC2 meaning independently of a particular agent platform. |
| FG05a / 19 | Why we use Codex as our reference | Shared SDLC2 meaning mapped to Codex and other agents, alongside AAIF standards context. | Explain the practical platform choice, Claude Code’s AGENTS.md support, and vendor-neutral governance with isolated tool-specific configuration. |
| FG06 / 20 | Where these ideas live in Codex | Responsibility map of project guidance, skills, schemas, scripts and tools. | Explain each mechanism’s role and interpreter. A skill can combine prose, structured inputs and scripts; “Codex DSL” is shorthand for several conventions, not a single language. |
| FG07 / 21 | Worked example: the SDLC2 commit | Vertical sequence: agent prepares code and status → human reviews/stages → validation → commit → outcome; branch to failure and separately authorized push. | Make the gradient operational. Preserve human-only staging, check the approved snapshot and distinguish local commit from remote push. Show observable failures instead of claiming unconditional atomicity. |
| FG08 / 22 | Choose the right degree of formalization | Three implementations of one workflow—interpretative, hybrid and executable—compared for flexibility, checking, maintenance and human comprehension. | Explain tradeoffs and the meta-rule: present meaningful implementation alternatives. Formalization, determinism and correctness are distinct; executable code is not automatically the most precise specification. |
| FG09 / 23 | One meaning, several representations | Traceability diagram linking domain definition, human explanation, design, types/contracts, workflow and tests, with implementation feedback. | Close with the governing principle: define meaning first, choose representation and enforcement at each boundary, and keep representations aligned as the system evolves. |

## Optional technical annex

| ID | Title | Visual and narration objective |
| --- | --- | --- |
| A1 | Codex vocabulary and mechanisms | Compact reference map for AGENTS.md, SKILL.md, invocation conventions, configuration, tools and enforcement boundaries. Verify current official documentation and distinguish CLI/IDE from ChatGPT Work before authoring. |
| A2 | A small SDLC2 implementation | Illustrative module/folder layout, status record, operation signature and failure cases. Identify proposed artifacts explicitly; use Node.js/TypeScript for the agreed commit example without claiming the repository already implements it. |

## Production and review contract

- Create one folder per slide when that slide is produced; each contains exactly two artifacts: slide.svg (or agreed editable UML/diagram equivalent) and speaker-text.md.
- Speaker text is the actual natural narration for later synthetic speech, not presenter instructions or bullet prompts. Keep production directions in this plan.
- Use substantive, visually striking slides with one clear argument; favor UML, compact Mermaid or precise SVG. Use imagery when it adds meaning, not decoration.
- Keep Markdown artifacts within 50 lines; avoid dense paragraphs used merely to evade the limit. Keep diagrams readable without horizontal scrolling.
- Introduce the sprint-completion problem in FG01 and resolve it concretely in FG07. The Person example explains domain meaning; it should not interrupt the main narrative.
- Agent prepares all governed changes, including status, before human staging. Agent and agent-invoked scripts must not stage or silently replace approved content; subsequent edits require renewed review/staging.
- Define completion evidence against the relevant snapshot. Do not require a tracked status file to contain the hash of the commit that contains that same file; report the resulting SHA separately.
- Treat commit and push as separate operations with explicit outcomes. Generated explanations and structured records are not proof that checks passed or actions succeeded.
- Ground current Codex details in official sources during slide authoring. Keep platform conventions, proposed SDLC2 notation and verified project implementation clearly distinguished.
- Per Pablo’s latest instruction, produce the complete batch before human review. Review each visual with its narration afterward; do not infer whole-file approval from agreement with the concept.

## Current position

All eleven main slides and both optional technical annex slides are drafted with SVG visuals and full speaker scripts. [Review folder](https://drive.google.com/drive/folders/1qCXFWyQx21NCRF7-eHSZ8BOCv-X4gu83) contains the thirteen slide folders and a combined review PDF. LifeBuckets and why-Codex additions await review; prior slide visuals and narration remain unchanged. The chapter also supports a future standalone Medium article; article drafting follows slide review. Existing presentation slides and reference folders are unchanged.
