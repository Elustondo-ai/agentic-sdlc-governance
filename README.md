# ASDG — Agentic SDLC Governance

## What is ASDG?

ASDG is a software development method that lets developers work with coding agents under explicit human review and approval.
It gives an existing project shared instructions, specialist roles and versioned project memory across the development lifecycle.
Each project keeps its own versioned `asdg/` folder, so its method can evolve alongside its code.

[Watch the ASDG introduction on YouTube](https://www.youtube.com/watch?v=ttQZylKeFdg) · [Browse presentations and downloads](docs/presentations/README.md).

## Quick Start — give your agent the repository URL

Use an existing Git project on macOS or Linux, with Git, Python 3.9+ and Claude Code or Codex available.
You do not need to clone this methodology repository or type Python commands yourself; the assistant runs the installation engine.

**Recommended: open your existing project in Claude Code or Codex and send this request:**

```text
Install ASDG in this project using:
https://github.com/Elustondo-ai/agentic-sdlc-governance

Read the README and follow its installation instructions.
```

<details>
<summary>Instructions for the installing agent</summary>

Confirm the target Git root and client; stop if `asdg/` already exists. Download the versioned portable ZIP linked below and its `.sha256` companion, verify the checksum, and inspect archive entries before extracting only its single `asdg/` folder into that root. Reject paths outside that folder and symbolic links; never overwrite existing files.

Read and follow the extracted `asdg/docs/install-zip-prompt.md` and its canonical `asdg-init` skill for preview, the approval request, apply and verification. The agent handles these steps; the initial request does not approve the unseen plan. Hook trust remains a separate human action; team setup and project analysis need separate requests after success.

If the README page cannot be read, use its [raw version](https://raw.githubusercontent.com/Elustondo-ai/agentic-sdlc-governance/main/README.md); if a required download fails, stop and report it. A README URL alone is reference material; the explicit install request above authorizes acquisition and extraction, while installation still requires approval of the preview.

</details>

The agent handles acquisition, preview, application and verification. Initialization waits for your approval of the exact preview; the request above is not that approval.

**Alternative — manual ZIP + Prompt:**

1. Download the [portable ZIP — 0.3.0-pilot.3](https://github.com/Elustondo-ai/agentic-sdlc-governance/releases/download/v0.3.0-pilot.3/asdg-0.3.0-pilot.3.zip).
2. Extract its single `asdg/` folder into the root of your existing Git project. **Stop if `asdg/` already exists.**
3. Open your project in Claude Code or Codex and paste `asdg/docs/install-zip-prompt.md` from the extracted package ([prompt reference](asdg/docs/install-zip-prompt.md)).
4. Review the preview and respond as requested by the selected package’s approval prompt. After verification, use `/asdg-status` in your project chat. Status reports what is ready and recommends the next skill, such as `/asdg-create-team` when team setup is still needed.

The portable ZIP and its [SHA-256 checksum](https://github.com/Elustondo-ai/agentic-sdlc-governance/releases/download/v0.3.0-pilot.3/asdg-0.3.0-pilot.3.zip.sha256) are available in the [pilot pre-release](https://github.com/Elustondo-ai/agentic-sdlc-governance/releases/tag/v0.3.0-pilot.3). Choose the portable asset; GitHub's automatic source archives are different packages.
This pilot includes Status-owned onboarding, Help, Update and lifecycle-ordered team setup; use the downloaded package’s own instructions.
This is a pilot candidate awaiting human review; installation checks do not establish native discovery, invocation or hook trust.
See [installation details](asdg/docs/installation.md) and [client integration limits](asdg/docs/client-integrations.md).

## Evolve and contribute — Clone, Promote, Upgrade

For example, LifeBuckets and iShop each keep their own versioned `asdg/` copy.
To share an improvement piloted in LifeBuckets, keep a local canonical checkout:

```sh
git clone https://github.com/Elustondo-ai/agentic-sdlc-governance.git
cd agentic-sdlc-governance
git rev-parse HEAD
```

The last command prints the full commit SHA. Use a reviewed commit containing the installer and a matching package manifest.
The [Clone installation prompt](asdg/docs/install-clone-prompt.md) takes that full SHA, the canonical clone path and the target project path, using the same preview and approval engine as ZIP installation.

`asdg promote` brings the LifeBuckets pilot improvement into the local canonical checkout for review. After reviewing and committing it, a contributor can open a pull request.
After acceptance and packaging of the canonical version, `asdg upgrade` brings that version into iShop. Both commands preview first and require explicit approval to apply; conflicts stop changes.
Use the [project-local commands and synchronization contract](asdg/docs/synchronization.md); no global `asdg` installation is required. Promotion and upgrade do not commit, push or open a pull request for you.

![A canonical provider builds a verified ZIP; each client owns its versioned methodology copy.](asdg/docs/images/distribution-flow.svg)

Use [Help](asdg/skills/asdg-help/SKILL.md) to explore commands and [Update](asdg/skills/asdg-update/SKILL.md) to prepare an existing project’s methodology and adapter updates. In Codex invoke `$asdg-help` or `$asdg-update`; in Claude Code use `/asdg-help` or `/asdg-update`.

## Methodology and maintainer references

Read the [lifecycle](asdg/docs/lifecycle-baseline.md), [role catalogue](asdg/00-governance/types/agent-catalog.json), [runtime contract](asdg/00-governance/docs/runtime-contract.md) and [CLI reference](asdg/scripts/cli.md).
Maintainers use [build and verification](asdg/docs/distribution-build.md), [source provenance](asdg/docs/provenance.md) and the [provider promotion review](docs/asdg/07-planning/02.1-review-provider-promotion.md).
`docs/` retains methodology development and presentation sources; optional presentation, component and video tools remain outside the portable core's acceptance claim.
