---
name: sei-architecture
description: >-
  Entry point and router for the SEI (Carnegie Mellon Software Engineering Institute) architecture
  practice. Use when the user invokes /sei, mentions the SEI architecture methodology, or asks to
  run an architecture assessment / architecture vision and is not sure which activity (quality
  attributes, QAW, ADD, ATAM, documentation, diagrams) they need. Explains the workflow and hands
  off to the matching sub-skill.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
user-invocable: false
---

# SEI Architecture Methodology — router

This plugin automates the core activities of the SEI software-architecture practice. Each activity
is its own skill with its own procedure and templates. This skill decides which one the user needs
and hands off.

**Keep prompts short.** One or two sentences. Offer choices as numbered lists.

## The activities

| # | Activity | Skill | Use it to… | Produces |
|---|----------|-------|------------|----------|
| 0 | **Architectural drivers** | `architectural-drivers` | Collect & track the four driver kinds — business goals, primary functional requirements (as UML **use cases**), constraints, quality attributes — with a traceability matrix | `architecture/drivers/` (one file per driver) + use-case diagrams |
| 1 | **Quality attributes** | `quality-attributes` | Turn vague "-ilities" into measurable 6-part quality attribute scenarios (ISO/IEC 25010), each drawn as a UML scenario diagram | `architecture/quality-attributes/scenarios.md` |
| 2 | **Quality Attribute Workshop (QAW)** | `quality-attribute-workshop` | Facilitate the SEI 8-step stakeholder workshop that elicits, consolidates, prioritises and refines scenarios *before* the architecture exists | `architecture/qaw/qaw-report.md` |
| 3 | **Attribute-Driven Design (ADD 3.0)** | `attribute-driven-design` | Design or evolve the architecture in driver-focused iterations | `architecture/add/<slug>-session.md` + `<slug>-Architecture.md` |
| 4 | **Architecture Tradeoff Analysis Method (ATAM)** | `atam` | Evaluate an existing or proposed architecture against its drivers; surface risks, sensitivity points, tradeoffs | `architecture/atam/atam-report.md` |
| 5 | **Architecture documentation (Views & Beyond)** | `architecture-documentation` | Produce an SEI Views-and-Beyond architecture description — **Module, C&C and Allocation** views (+ extra views as needed) and the beyond-views supporting docs | `architecture/docs/` package |
| 6 | **Diagrams** | `sei-diagrams` | Draw clean, low-crossing UML / C4 diagrams, render them to PNG with a curated palette, and visually cross-verify each | `architecture/diagrams/*.png` |

## How the activities connect

```
[0] Architectural drivers  ── business goals + use cases + constraints + quality attributes
      │           ▲                       │
      │           │  (refined scenarios)  ▼
      │       [2] QAW  ◄──────────  [1] Quality attributes  ──► scenarios.md
      │                                   │
      ▼                                   ▼
      └──────────────► drivers register ──► consumed as input by …
                                     │
                                     ▼
                            [3] ADD 3.0  ──► architecture + views + decisions
                                     │
                                     ▼
                     [5] Views & Beyond documentation
                                     │
                                     ▼
                            [4] ATAM evaluation ──► risks, tradeoffs, risk themes
                                     ▲                         │
                                     └── [6] diagrams          └─► feed back to [0] as status
                                         support every artifact above
```

Typical engagements:

- **Architecture vision / greenfield**: 0 → 1 (or 2) → 3 → 5 → 6.
- **Architecture assessment of an existing system**: 0 → 1 → 4 → (targeted 3 to fix risk themes) → 5.
- **Just need drivers / scenarios**: 0 and/or 1.
- **Just need a diagram rendered**: 6.

## Router procedure

1. If the user already named an activity or invoked a specific command (`/drivers`, `/qaw`, `/add`,
   `/atam`, `/quality-attributes`, `/architecture-docs`, `/sei-diagram`), skip straight to that skill.
2. Otherwise ask one question: *"Which are we doing?"* and list the seven activities above with a
   one-line description each.
3. If the user describes a goal instead of picking, map it:
   - "drivers", "business goals", "use cases", "requirements", "constraints" → **architectural-drivers**
   - "measurable NFRs / -ilities / scenarios" → **quality-attributes**
   - "workshop", "stakeholders in a room", "elicit scenarios" → **quality-attribute-workshop**
   - "design the architecture", "how should I structure this" → **attribute-driven-design**
   - "evaluate", "review", "assess", "find risks", "tradeoffs" → **atam**
   - "document", "architecture description", "views", "hand-off doc" → **architecture-documentation**
   - "draw", "diagram", "render", "PNG", "UML", "C4" → **sei-diagrams**
4. State which skill you're using in one line, then follow that skill's `SKILL.md` exactly.

## Shared conventions (all sub-skills follow these)

- **Working directory**: everything is written under `architecture/` in the current project, one
  sub-folder per activity. Create `architecture/` if it does not exist. Never write outside it
  unless the user gives a path.
- **Markdown is the source of truth.** No database, no server. Update artifact files as you go,
  not only at the end.
- **Drafts first.** For every step, propose a complete first draft from what you already know,
  then refine with the user. Do not interview question-by-question when you can draft and correct.
- **Traceability.** Every design decision, risk, or analysis row cites at least one driver ID
  (`BG-1`, `UC-2`, `CON-3`, and attribute-prefixed QA scenarios like `AQA-1`, `SQA-2`).
- **Diagrams** always go through the `sei-diagrams` skill: Mermaid (or PlantUML) with C4 / UML
  notation, a `title` line, aliases without spaces, concrete technology on every element, specific
  relationship labels, ≤ 10 nodes per diagram, explicit boundaries, minimised edge crossings —
  **and every diagram is rendered to PNG and visually cross-verified** (`Read` the image, check
  correctness + crossings, iterate) before it is embedded anywhere.
- **Reporting**: the working artifacts are Markdown. When the user wants a deliverable report, ask
  **Markdown, HTML, or both**, then build it with `${CLAUDE_PLUGIN_ROOT}/scripts/build-report.sh <file.md> --format
  <fmt> [--embed-diagrams]`. HTML output is a single self-contained file styled with the SEI
  palette, with a cover page and table of contents.
- **References**: deeper method notes live in `${CLAUDE_PLUGIN_ROOT}/references/` at the plugin root — see
  `${CLAUDE_PLUGIN_ROOT}/references/README.md` for the index. Core: `architecture-fundamentals.md` (structures,
  views, the "good architecture" rules of thumb), `architectural-drivers.md`,
  `quality-attribute-taxonomy.md`, `tactics-catalog.md`, `architecture-patterns.md`,
  `design-concepts.md`, `qaw-method.md`, `add-method.md`, `atam-method.md`,
  `design-reviews.md`, `views-and-beyond.md`, `interfaces.md`,
  `architecture-in-the-lifecycle.md` (debt, Agile, distributed dev),
  `runtime-environments.md` (virtualization, cloud, mobile). Read the relevant one when a step
  needs more depth.

## Source material

These skills encode the public SEI body of knowledge, principally:

- Bass, Clements, Kazman — *Software Architecture in Practice* (3rd/4th ed.).
- Cervantes, Kazman — *Designing Software Architectures: A Practical Approach* (2nd ed.) — the ADD 3.0 reference.
- Clements et al. — *Documenting Software Architectures: Views and Beyond* (2nd ed.).
- SEI technical reports: ATAM (CMU/SEI-2000-TR-004), QAW (CMU/SEI-2003-TR-016), ADD (CMU/SEI-2006-TR-023).
