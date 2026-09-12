---
name: architectural-drivers
description: >-
  Collect, structure and track the four kinds of SEI architectural drivers — business goals,
  primary functional requirements (as UML use cases), constraints, and quality attribute scenarios
  — as a directory of one-file-per-driver artifacts with a traceability index. Use when the user
  invokes /drivers or asks to capture architectural drivers, list use cases, track
  requirements/constraints/business goals, or assemble the driver inputs for an ADD or ATAM run.
version: 1.1.0
allowed-tools: [Read, Write, Bash, Glob]
---

# Architectural drivers

The **architectural drivers** are the inputs that shape the architecture. Each one worth
capturing is an **architecturally significant requirement (ASR)** — it has a *profound impact on
the architecture* **and** *high business/mission value* (deep dive:
`references/architectural-drivers.md`). ASRs come from requirements documents, stakeholder
interviews / a QAW, the architect's own utility tree, or derivation from business goals. In the
SEI method there are four kinds:

| Kind | ID code | What it is | Captured as |
|------|---------|------------|-------------|
| **Business goals** | `BG-<n>` | Why the system exists; what success means to the sponsor | goal statements, each traceable to a stakeholder |
| **Primary functional requirements** | `UC-<n>` | The architecturally significant behaviour | **UML use cases** (actor, goal, main + key alternate flows) |
| **Constraints** | `CON-<n>` | Non-negotiable boundaries: business, technical, regulatory | constraint statements with a rationale/source |
| **Quality attributes** | `<ATTR>QA-<n>` | Required qualities, measurable | six-part quality attribute scenarios (detail owned by the `quality-attributes` skill) |

### Quality attribute scenario ID scheme

Every quality attribute scenario gets an **attribute-prefixed code** — the attribute abbreviation
followed by `QA` and a number that runs **sequentially within that prefix**. `AQA-1` is the first
availability scenario, `SQA-3` the third security scenario. The ISO/IEC 25010 characteristic /
sub-characteristic is still recorded on every scenario.

| Attribute (common name) | ISO/IEC 25010:2023 home | Code |
|-------------------------|-------------------------|------|
| Availability | Reliability / availability | `AQA` |
| Reliability (other) | Reliability | `RQA` |
| Performance | Performance efficiency | `PQA` |
| Security | Security | `SQA` |
| Safety | Safety | `SFQA` |
| Modifiability | Maintainability / modifiability | `MQA` |
| Maintainability (other) | Maintainability | `MNQA` |
| Testability | Maintainability / testability | `TQA` |
| Usability | Interaction capability | `UQA` |
| Interoperability | Compatibility / interoperability | `IQA` |
| Compatibility (co-existence) | Compatibility / co-existence | `CQA` |
| Scalability / elasticity | Flexibility / scalability | `SCQA` |
| Deployability / installability | Flexibility / installability | `DQA` |
| Portability / replaceability | Flexibility | `PTQA` |
| Adaptability | Flexibility / adaptability | `ADQA` |
| Observability / monitorability | cross-cutting | `OQA` |
| Energy efficiency | cross-cutting | `EQA` |
| Integrability | cross-cutting (BCK 4th ed.) | `INQA` |
| Functional suitability (rare as a scenario) | Functional suitability | `FQA` |

If a needed attribute is not listed, coin a short uppercase mnemonic + `QA`, record it in the
register's header legend, and use it consistently. `QAS` may be used **only** as the collective
noun ("the quality attribute scenarios"), never as an ID prefix.

## Register layout — a directory, one file per driver

Drivers grow. Do **not** keep them in a single file — maintain a directory so each driver is its
own artifact, diffable and linkable:

```
architecture/drivers/
├── README.md                     # ID legend · traceability matrix · coverage check · prioritised list · change log
├── business-goals/
│   ├── README.md                 # index: one linked row per BG
│   └── BG-<n>.md                 # one file per business goal
├── use-cases/
│   ├── README.md                 # index: one linked row per UC + its diagram; links the overview diagram
│   ├── UC-<n>.md                 # one file per use case — full use case + its own UML use case diagram
│   └── diagrams/                 # <name>.mmd|.puml source + <name>.png render (per use case, and one overview per actor group)
├── constraints/
│   ├── README.md                 # index: one linked row per CON
│   └── CON-<n>.md                # one file per constraint
└── quality-attributes/
    ├── README.md                 # index: one linked row per <ATTR>QA + (V,R); prominently links utility-tree.md
    ├── <ATTR>QA-<n>.md           # one file per quality attribute — full six-part scenario + its own scenario diagram
    ├── utility-tree.md           # the tabular utility tree (summary of the QA drivers)
    └── diagrams/                 # scenario-<ATTR>QA-<n>.mmd|.puml + .png
```

- **`README.md`** is the top aggregate file (GitHub renders it on directory browse): the ID
  legend, the traceability matrix, the coverage check, the prioritised driver list, and a dated
  change log. It links to every driver file with a **relative Markdown link**.
- Each subdirectory also has its own small **`README.md` index** — one linked row per file in
  that directory. The `quality-attributes/README.md` links every `<ATTR>QA-<n>.md` **and**
  `utility-tree.md`.
- Every path mentioned in prose or a table is a working **relative Markdown link**
  (`[UC-1](use-cases/UC-1.md)`), never a bare backtick path. Each `README.md` ends with a
  **Navigation** footer (up to the package, across to `../qaw/`, `../add/`, `../atam/`,
  `../docs/`, and the project root).
- Each **driver file** is self-contained. Add a new driver = add a file + one matrix row in the
  top `README.md` + one row in the subdirectory `README.md`. Never renumber; a retired driver
  keeps its file with `**Status**: retired`.
- If `/quality-attributes` has produced `architecture/quality-attributes/scenarios.md`, each
  `quality-attributes/<ATTR>QA-<n>.md` still carries the **full six-part scenario and its
  diagram** (copied, kept in sync) and links back to `scenarios.md` for the utility tree and the
  wider set. The drivers directory is always self-sufficient as ADD/ATAM input.

Deep reference: `references/quality-attribute-taxonomy.md`, `references/add-method.md`.
Templates: `templates/drivers-readme.md`, `templates/subdir-readme.md`,
`templates/business-goal.md`, `templates/use-case.md`, `templates/constraint.md`,
`templates/quality-attribute-scenario.md`.

**Keep prompts short.** Numbered lists. **Draft first**, refine.

## Procedure

### Step 1 — Gather source material
Ask for / read: product brief, PRD, vision doc, backlog, SLAs, an existing requirements list,
org/regulatory context. Create `architecture/drivers/` and its four sub-directories. If a QAW
report or `scenarios.md` exists, plan to import (not merely link) it.

**Four ways to gather ASRs** (`references/architectural-drivers.md`): (1) *sniff* a requirements
doc for the architecturally significant categories (usage, time, external elements, networking,
orchestration, security, data, resources, project management, hardware, flexibility, named
tech) and their anticipated change; (2) *interview stakeholders* — when they say "I don't know
what the requirement should be", **play dumb** to bracket a range ("24 h OK? … 1 h? … 5 min?");
(3) *understand the business goals* — PALM: elicit goals with the 11 categories, write 7-part
business-goal scenarios, derive the QAs each implies; (4) the architect's *utility tree* when
sources aren't available.

### Step 2 — Business goals → `business-goals/BG-<n>.md`
Draft 3–7 business goals, each as *"<stakeholder> needs <outcome> so that <business value>"*.
Categories to probe (SEI business-goal categories): growth & market share, financial,
personal/reputational, responsibility to society/law, quality of product, quality of process,
stakeholder relationships. One file per goal from `templates/business-goal.md`. Present, confirm.

### Step 3 — Primary functional requirements as use cases → `use-cases/UC-<n>.md`
Identify only the use cases with **architectural impact** — those that exercise a quality
attribute, cross a trust or process boundary, drive a key integration, or dominate load. One file
per use case from `templates/use-case.md`, each with: primary actor, supporting actors, trigger,
preconditions, main success scenario (numbered), key alternate/exception flows, architectural
significance, related drivers.

**Every use case is supported by a proper UML use case diagram.** In each `UC-<n>.md`:
1. Draw a **use case diagram for that use case** via the `sei-diagrams` skill's *Use case
   diagram* pattern (Mermaid convention, or PlantUML if the user prefers) — the primary actor and
   any supporting actors **outside** the system boundary, the use case **inside**, `<<include>>`
   for always-invoked sub-behaviour and `<<extend>>` for conditional sub-behaviour (dashed,
   labelled). A supporting actor that is a **system** (a third-party API, a batch job, another
   service — not a person or role) is **not** a stick figure: draw it as a `«system»`-stereotyped
   rectangle instead (`rectangle "<Name>" <<system>>` in PlantUML; the `«system»` box convention
   in Mermaid) — it is still outside the boundary and still connects to the use case with an
   ordinary association.
2. Show the source in the conversation, render to `use-cases/diagrams/UC-<n>.png`, `Read` the PNG
   and visually cross-verify (actors outside, use case inside, include/extend dashed, no
   avoidable crossings), then embed it per the `sei-diagrams` *Embedding in Markdown* rule
   (Mermaid → fenced block + `![UC-<n> — <name>](diagrams/UC-<n>.png)`; PlantUML → that image
   line + a link to `diagrams/UC-<n>.puml`).
Also produce one **overview** use case diagram per actor group / subsystem
(`use-cases/diagrams/overview-<group>.png`, ≤ ~10 use cases) and reference it from `README.md`
and `use-cases/README.md`.

**Every use case node that appears in any diagram carries exactly one `UC-<n>` code, and that code
is described in its own `UC-<n>.md`.** This applies to an `<<include>>`/`<<extend>>` target just as
much as to a top-level use case — never draw an unlabelled bubble, and never let the same shared
sub-behaviour carry different codes in different diagrams (e.g. `UC-1a` in UC-1's diagram but
`UC-3a` in UC-3's diagram for the same "categorise transaction" flow). If a sub-behaviour is
`<<include>>`d by more than one parent use case, give it its own independent top-level code (its
own `UC-<n>.md`, its own small diagram) rather than a `<parent>a`-style suffix, since a suffix
implies single-parent ownership it doesn't have; use the `<parent>a` suffix only for a sub-flow
private to one parent. Every overview diagram must reuse the same codes as the individual `UC-<n>`
diagrams — an overview is not the place to introduce a fresh, undocumented label.

### Step 4 — Constraints → `constraints/CON-<n>.md`
One file per constraint from `templates/constraint.md`: type (business / technical / regulatory),
the constraint, its source, hard vs negotiable, and any business goal or quality attribute
scenario it conflicts with.

### Step 5 — Quality attributes → `quality-attributes/<ATTR>QA-<n>.md`
**Document every quality attribute as a six-part quality attribute scenario, and support it with
its own scenario diagram.** One file per scenario from `templates/quality-attribute-scenario.md`:
- the **six-part table**: source of stimulus, stimulus, artifact, environment, response,
  **numeric** response measure;
- the **ISO/IEC 25010:2023** characteristic + sub-characteristic;
- business goal(s) supported; priority pair `(Importance, Difficulty)`;
- the **six-part scenario diagram** via the `sei-diagrams` skill's *Quality attribute scenario
  diagram* pattern (horizontal — Mermaid `flowchart LR` or the PlantUML pattern), rendered to
  `quality-attributes/diagrams/scenario-<ATTR>QA-<n>.png`, `Read` and visually cross-verified,
  embedded per the *Embedding in Markdown* rule: Mermaid → the fenced block +
  `![<ATTR>QA-<n> six-part scenario](diagrams/scenario-<ATTR>QA-<n>.png)`; PlantUML → that image
  line + a link to the `.puml` source.

If `scenarios.md` exists, copy each scenario's six-part detail and diagram into its file here and
add a `> Source: ../../quality-attributes/scenarios.md` line. If not, this is where the detail lives.

**Then build the quality attribute utility tree** — `quality-attributes/utility-tree.md` — as the
**summary of all quality attributes in the drivers**. **It is a table, not a diagram.** One row
per leaf scenario, three grouping levels captured in the columns:

| Quality attribute | Refinement (concern) | Leaf scenario (ID — one line, with response measure) | Priority (V, R) | Status |
|-------------------|----------------------|------------------------------------------------------|:---------------:|:------:|

- "Quality attribute" is the ISO/IEC 25010 characteristic; "Refinement" is the specific concern
  (e.g. Performance efficiency → time behaviour).
- `(V, R)` = **business value** V and **technical risk** R, each `H`/`M`/`L`
  (`V ≈ Importance to the business`, `R ≈ Difficulty / architectural risk` — same pair used on
  the scenario files). Mark a `(H, H)` leaf `★` — it is architecturally significant.
- Follow the table with a short **"Reading the tree"** note: a QA/refinement with no leaf →
  investigate for an unrecorded ASR; the `★` leaves get the most attention; which leaves are
  `addressed` vs `open`.

If a QAW was run, import its tree (Step 9 of `/qaw`); otherwise construct it here from the
scenario set. `README.md` links to it. Template: `templates/utility-tree.md`.

### Step 6 — `README.md` — traceability matrix + coverage check
Write `architecture/drivers/README.md` from `templates/drivers-readme.md`, and one
`README.md` per subdirectory from `templates/subdir-readme.md`. The matrix has one row per
driver, with the "File" cell a **relative Markdown link**:

| Driver | File | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|------|-------------|---------------------------|--------------|--------|
| UC-1 | [UC-1](use-cases/UC-1.md) | BG-1, BG-2 | PQA-1, CON-4 | ADD iter 1 | open |
| AQA-1 | [AQA-1](quality-attributes/AQA-1.md) | BG-3 | — | ADD iter 2 | partially |
| CON-2 | [CON-2](constraints/CON-2.md) | BG-1 | UC-1, UC-4 | — | open |

`Status` ∈ `open` / `in design` / `partially` / `addressed` / `retired`.
**Coverage check (mandatory):** every `BG-` supported by ≥ 1 `UC-` or `<ATTR>QA-`; every
`UC-` / `<ATTR>QA-` / `CON-` traces up to ≥ 1 `BG-`. Report any gaps explicitly.

### Step 7 — Prioritised driver list (in `README.md`)
The ordered list ADD/ATAM consume: `(H,H)` then `(H,M)` quality scenarios, the architecturally
significant use cases, then the hard constraints — each one line with its ID and a relative link.

### Step 8 — Change log
Append a dated line to the top `README.md`'s change log for every run: what was added / changed
/ retired.

## Tracking across the engagement

- `/attribute-driven-design` reads this directory as its Step-1 input and, after each iteration,
  reports which driver IDs moved to `partially` / `addressed` — update those files' `**Status**`
  and the `README.md` matrix.
- `/atam` reads it for business drivers and the utility tree; ATAM risk themes map back to `BG-n`.
- Re-run `/drivers` whenever scope changes; add files, never rewrite history — retire, don't delete.

## Rules

- Four driver kinds, four ID prefixes: `BG-`, `UC-`, `CON-`, `<ATTR>QA-`. IDs are sequential
  within their prefix and never reused or renumbered.
- **One file per driver** under the matching sub-directory; the top `README.md` is the aggregate
  file; each sub-directory has a small `README.md` index. Every cross-reference is a relative
  Markdown link.
- Functional requirements that shape the architecture are written as **use cases** (primary actor,
  trigger, numbered main success scenario) — never one-liners — and **each has its own proper UML
  use case diagram** (actors outside the boundary, use case inside, include/extend dashed),
  rendered and visually cross-verified.
- **Every quality attribute is a six-part quality attribute scenario** with a numeric response
  measure, an ISO/IEC 25010 classification, **and its own six-part scenario diagram**, rendered
  and visually cross-verified.
- Every driver file carries `**Status**`; every diagram is embedded as a ```mermaid /
  ```plantuml block + a relative `![](diagrams/…​.png)` image line (renders on GitHub / GitLab).
- The utility tree (`quality-attributes/utility-tree.md`) is a **table** with a `(V, R)` pair
  per leaf — never a diagram.
- The `README.md` traceability matrix is mandatory and must have no orphan drivers — report gaps.
- Nothing is silently dropped — retired drivers keep their file marked `retired`.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until it passes both:

1. **Automated**: `python tests/validate.py architecture/drivers/` (recurses the directory) —
   exits 0. Checks IDs, per-file structure, six-part scenarios with numeric measures, a use case
   diagram in every `UC-*.md`, a scenario diagram in every `<ATTR>QA-*.md`, the tabular utility
   tree, `README.md` traceability with no orphans, no broken relative links, diagram rules, and
   the deprecated-`QAS-` guard.
2. **Best-practice checklist**: walk the *Architectural drivers* section of
   `references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix, re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
