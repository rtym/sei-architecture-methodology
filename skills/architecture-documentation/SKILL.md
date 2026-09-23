---
name: architecture-documentation
description: >-
  Produce an SEI "Views and Beyond" software architecture description — module views, component-and-
  connector views, allocation views, plus the supporting documentation (roadmap, mapping between
  views, rationale, directory). Use when the user invokes /architecture-docs or asks to document an
  architecture, write an architecture description / SAD, create architecture views, or prepare an
  architecture hand-off / vision document.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
user-invocable: false
---

# Architecture documentation — Views and Beyond (V&B)

Produce an architecture description following the SEI **Views and Beyond** approach (Clements et
al., *Documenting Software Architectures*). The description is a **package of views** plus
**documentation beyond views** that ties them together.

Output: `architecture/docs/` (create it), one Markdown file per view + supporting docs, and a
`README.md` roadmap. Deep reference: `${CLAUDE_PLUGIN_ROOT}/references/views-and-beyond.md`. Templates in `${CLAUDE_PLUGIN_ROOT}/templates/`.
Diagrams: the `sei-diagrams` skill (`${CLAUDE_PLUGIN_ROOT}/skills/sei-diagrams/SKILL.md`).

**Keep prompts short.** Numbered lists. **Draft first**, refine.

## Guiding rules (full guidance in `${CLAUDE_PLUGIN_ROOT}/references/views-and-beyond.md`)

- **Know your reader.** Documentation serves four uses — education, communication, analysis &
  construction, forensics — and is both *prescriptive* (constrains open decisions) and
  *descriptive* (records made ones). Identify the real stakeholders and give each the views they
  need (PM, developer, tester/integrator, interoperating-system designer, maintainer, end user,
  analyst, infrastructure support, future architect — see the reference's stakeholder table).
- **Least-formal-that-removes-ambiguity notation**, always with a key/legend: informal
  boxes-and-lines → semi-formal (C4 for structure, UML for behaviour) → formal ADL (rare).
- **Document the relevant views + beyond-views.** All three structural viewtypes must be
  covered; add **quality views** (security / communications / error-handling / reliability /
  performance) when a concern is pervasive and spread across structures.
- **Document behaviour**, not just structure — trace-oriented (use cases, sequence,
  communication, activity) for a path; comprehensive (state machine) for all paths. Each
  behaviour diagram gets a plain-English paragraph. **Coverage rule**: the primary C&C view's
  §2.4 carries one behaviour diagram per architecturally significant use case (`UC-<n>`) in the
  drivers register — reuse the ADD `Architecture.md` §6 diagrams, re-rendered into `docs/diagrams/`.
- **Combine views** only as legible overlays (C&C+C&C; deployment+C&C-with-processes;
  decomposition+work-assignment/impl/uses/layered).
- **Record rationale as you design it** — the two-column table (*decision + location* |
  *rationale + assumptions incl. discarded alternatives*), with extra care and risk notes for
  decisions that drive a `(H,H)`/`(H,M)` scenario measure.
- **Traceability** — link each significant decision to the ASR / business goal that led to it;
  the package is "right" when every ASR is covered by a trace link.
- **Practical**: short wiki pages over a deep structure; comment-not-edit permissions for most
  stakeholders; version-control the docs and release ahead of milestones; for dynamic
  architectures document the invariants + the allowed changes (variability guide) + auto-gen
  interface docs.

## Core idea: a view = a viewtype projected for a purpose

A **view** documents the system's elements and relations of one kind, chosen to answer specific
stakeholder concerns. Views are grouped into three **viewtypes**:

| Viewtype | Elements | Relations | Answers |
|----------|----------|-----------|---------|
| **Module** | modules (implementation units) | *is-part-of*, *depends-on*, *is-a* | How is the code organised? Who owns what? Impact of a change? |
| **Component-and-Connector (C&C)** | runtime components, connectors | *attachment*, data/control flow | What runs, and how do parts interact at runtime? Performance, availability, security paths? |
| **Allocation** | software elements ↔ environment elements | *allocated-to* | Where does it run / build / get worked on? Deployment, install, work assignment? |

Common view styles (pick the ones that carry the architecture's significant decisions):

- **Module**: decomposition, uses, layered, generalization, data model, aspects.
- **C&C**: client-server, service-oriented, publish-subscribe, pipe-and-filter, shared-data,
  peer-to-peer, communicating-processes.
- **Allocation**: deployment, install, implementation (code→file), work-assignment.

## Choosing views (do this first)

The description **must** cover all three V&B viewtypes. Minimum set:

| Viewtype | Required view(s) | Add when… |
|----------|------------------|-----------|
| **Module** | decomposition **and** uses (or layered) | generalization / data-model / aspects matter |
| **Component-and-Connector** | ≥ 1 C&C view of the primary runtime structure (e.g. service / pub-sub / client-server) | multiple distinct runtime structures exist |
| **Allocation** | deployment | install, implementation (code→file), or work-assignment matter |

Procedure:
1. List the **stakeholders** and their concerns — from `architecture/drivers/stakeholders.md`
   (`ST-<n>`) when it exists; add reader roles it lacks (new joiners, future architect) there.
2. Propose the view set: the required views above plus any extra view a stakeholder concern
   demands. It is always acceptable to add views; it is not acceptable to drop a viewtype.
3. Map each stakeholder concern → the view(s) that address it. Present the **view selection
   table** and confirm before writing.

## Per-view template (Views and Beyond "view packet")

Each view file (`architecture/docs/view-<name>.md`) has these sections:

```markdown
# View: <name> (<viewtype> / <style>)

## 1. Primary presentation
<The main diagram — rendered via sei-diagrams. Shows the elements and relations of this view.
Keep to ≤ ~10 elements; split into sub-views if larger. Legend included or referenced.>

## 2. Element catalog
### 2.1 Elements and their properties
| Element | Responsibility / role | Key properties |
|---------|-----------------------|----------------|
### 2.2 Relations and their properties
| From | Relation | To | Properties |
|------|----------|----|-----------|
### 2.3 Element interfaces
<For significant elements: provided/required interfaces, operations, data, error handling —
the four agreement points (scope · interaction style · data representation & structure · error
model) from `${CLAUDE_PLUGIN_ROOT}/references/interfaces.md`. Reference §8 of the ADD Architecture.md if it exists.>
### 2.4 Element behavior
<Sequence / state diagrams for behavior not obvious from structure. Via sei-diagrams.>

## 3. Context diagram
<This view's scope boundary and what sits outside it.>

## 4. Variability guide
<Points of built-in variation (config, plug-ins, feature flags, product-line options) and how to exercise them. Omit the section only if there is genuinely none.>

## 5. Rationale
<Why the structure is this way; alternatives considered and rejected; how it serves the drivers (cite <ATTR>QA- / UC- / CON- IDs).>
```

## Document structure — the typical V&B organisation

The description is a package assembled in this order (this is the standard V&B layout):

```
architecture/docs/
├── README.md                 # 1. Documentation roadmap  +  2. How the documentation is organised
├── system-overview.md        # 3. System overview
├── view-<name>.md            # 4. Views  (one file per view; each is a "view packet", template below)
│   ...                       #    grouped Module / C&C / Allocation
├── mapping-between-views.md   # 5. Mapping between views
├── rationale.md              # 6. Rationale  (+ ADR log)
├── directory.md              # 7. Directory — index, glossary, acronym list
└── change-log.md             # revision history of the description itself
```

`README.md` (GitHub renders it on directory browse) also carries the **view selection table**
and a scenario-based "where do I look to answer X" guide for each stakeholder. Every file
reference in the package is a working **relative Markdown link**, and `README.md` ends with a
Navigation footer linking every view packet, the package index `../README.md`, and only those
sibling packages that exist.

## Documentation beyond views

Create these supporting files in `architecture/docs/`:

| File | V&B part | Contents |
|------|----------|----------|
| `README.md` | Roadmap + organisation | What documentation exists, how it's organised, how each stakeholder should read it, the view-selection table, and a scenario-based "how to find" guide. |
| `system-overview.md` | System overview | What the system does, its context, major functional requirements (use cases), and the driving quality attribute scenarios (link to `../drivers/README.md` / `../quality-attributes/scenarios.md`). |
| `mapping-between-views.md` | Mapping between views | Tables mapping elements across views (module → runtime component → deployment node). This is where internal consistency is demonstrated. |
| `rationale.md` | Rationale | Cross-cutting architecture rationale and the ADR log. If `/add` produced `../add/adr/ADR-<n>.md`, **link them — do not re-derive or duplicate**; write new ADRs (`${CLAUDE_PLUGIN_ROOT}/templates/adr.md`) only for decisions taken here. |
| `directory.md` | Directory | Index, glossary, acronym list. |
| `change-log.md` | — | Dated list of revisions to the architecture description. |

## Report format — the V&B report

The files above are the working Markdown. For a deliverable, ask the user **Markdown, HTML, or
both**, then build **one Views-and-Beyond structured report** with `--profile vandb` — it takes
the `docs/` directory and orders it as *roadmap → system overview → Module view → C&C view →
Allocation view → other views → mapping between views → rationale → directory → change log*:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/build-report.sh --profile vandb architecture/docs/ \
  --format both --embed-diagrams --title "Architecture Description — <SystemName>" \
  --out architecture/reports/architecture-description.html
```

`--embed-diagrams` renders every ```mermaid block to PNG (via the `sei-diagrams` renderer) and
inlines it; the output is one self-contained HTML file styled with the SEI palette, with a cover
page and a table of contents that follows the V&B section order.

## Procedure

1. **Gather inputs**: existing `Architecture.md` from ADD, `scenarios.md`, code layout, infra
   config, ADRs. Read what the user points at.
2. **Stakeholder + concern list** → **view selection table**. Present, confirm.
3. For each selected view: draft the **primary presentation diagram** (via `sei-diagrams`, shown
   in conversation first), then fill the element catalog, context, variability guide, rationale.
   Present each view packet; refine; write the file.
4. Write the **beyond-views** files. The `mapping-between-views.md` is mandatory — it is how the
   package proves internal consistency.
5. Write `README.md` last, once the view set is stable; end it with a Navigation footer. Update
   the `/architecture-docs` row and change log of the package index `architecture/README.md`.
6. Run `python ${CLAUDE_PLUGIN_ROOT}/tests/validate.py architecture/docs/*.md` and fix any reported issues, including
   broken relative links.

## Notation, combining views, behaviour

Deep guidance in `${CLAUDE_PLUGIN_ROOT}/references/views-and-beyond.md`:

- **Notation** — use the least formal notation that removes ambiguity for the reader: C4 for
  structure, UML for behaviour and use cases; always with a legend. The `sei-diagrams` skill
  enforces the visual rules and offers every diagram type in Mermaid **or** PlantUML.
- **Combining views** — merge two views into one overlay only when they serve overlapping
  stakeholders and the result stays ≤ ~10 elements at one abstraction level.
- **Behaviour** — §2.4 of each view packet (and §6 of the ADD architecture doc): sequence for a
  scenario path, state machine for one element's modes, activity for a workflow. Each behaviour
  diagram is followed by a plain-English paragraph.

## The seven rules for sound documentation (apply throughout)

1. Write from the reader's point of view.
2. Avoid unnecessary repetition (state each fact in one place; cross-reference).
3. Avoid ambiguity — define terms; use a consistent notation with a legend.
4. Use a standard, agreed organisation (this template).
5. Record rationale for significant decisions.
6. Keep documentation current but not too detailed — review it and update on change.
7. Review documentation for fitness of purpose with its intended stakeholders.

## Rules

- Never document a view whose elements/relations you cannot name concretely — draft the diagram
  first, and if it stays vague, the architecture decision is missing, not the doc.
- Every view packet has all five sections; "Variability guide" may state "none" but must be present.
- Every rationale cites ≥ 1 driver ID (`<ATTR>QA-`, `UC-`, `CON-`).
- The primary C&C view packet's §2.4 has a behaviour diagram for every architecturally
  significant `UC-<n>`; `rationale.md` links existing ADD ADRs instead of restating them.
- All diagrams follow the `sei-diagrams` rules and are rendered in-conversation before being saved.
- `mapping-between-views.md` must actually cross-reference the views you produced — no placeholders.
- Keep each primary presentation to ≤ ~10 elements; split rather than crowd.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until the generated artifact passes both:

1. **Automated**: `python ${CLAUDE_PLUGIN_ROOT}/tests/validate.py architecture/docs/*.md` — exits 0. It checks IDs, structure, six-part scenarios with numeric
   measures, traceability with no orphans, diagram rules, and the deprecated-`QAS-` guard.
2. **Best-practice checklist**: walk the relevant section of
   `${CLAUDE_PLUGIN_ROOT}/references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix,
   re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
