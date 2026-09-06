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

The **architectural drivers** are the inputs that shape the architecture. In the SEI method there
are four kinds:

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
├── index.md                      # ID legend · traceability matrix · coverage check · prioritised list · change log
├── business-goals/
│   └── BG-<n>.md                 # one file per business goal
├── use-cases/
│   ├── UC-<n>.md                 # one file per use case — full use case + its own UML use case diagram
│   └── diagrams/                 # <name>.mmd source + <name>.png render (per use case, and one overview per actor group)
├── constraints/
│   └── CON-<n>.md                # one file per constraint
└── quality-attributes/
    ├── <ATTR>QA-<n>.md           # one file per quality attribute — full six-part scenario + its own scenario diagram
    └── diagrams/                 # scenario-<ATTR>QA-<n>.mmd + .png
```

- **`index.md`** is the only aggregate file: the ID legend, the traceability matrix, the coverage
  check, the prioritised driver list, and a dated change log. It links to every driver file.
- Each **driver file** is self-contained. Add a new driver = add a file + one matrix row in
  `index.md`. Never renumber; a retired driver keeps its file with `**Status**: retired`.
- If `/quality-attributes` has produced `architecture/quality-attributes/scenarios.md`, each
  `quality-attributes/<ATTR>QA-<n>.md` still carries the **full six-part scenario and its
  diagram** (copied, kept in sync) and links back to `scenarios.md` for the utility tree and the
  wider set. The drivers directory is always self-sufficient as ADD/ATAM input.

Deep reference: `references/quality-attribute-taxonomy.md`, `references/add-method.md`.
Templates: `templates/drivers-index.md`, `templates/business-goal.md`, `templates/use-case.md`,
`templates/constraint.md`, `templates/quality-attribute-scenario.md`.

**Keep prompts short.** Numbered lists. **Draft first**, refine.

## Procedure

### Step 1 — Gather source material
Ask for / read: product brief, PRD, vision doc, backlog, SLAs, an existing requirements list,
org/regulatory context. Create `architecture/drivers/` and its four sub-directories. If a QAW
report or `scenarios.md` exists, plan to import (not merely link) it.

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
   labelled).
2. Show the source in the conversation, render to `use-cases/diagrams/UC-<n>.png`, `Read` the PNG
   and visually cross-verify (actors outside, use case inside, include/extend dashed, no
   avoidable crossings), then embed it in the file as the ```mermaid block **plus**
   `![UC-<n> — <name>](diagrams/UC-<n>.png)`.
Also produce one **overview** use case diagram per actor group / subsystem
(`use-cases/diagrams/overview-<group>.png`, ≤ ~10 use cases) and reference it from `index.md`.

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
  diagram* pattern — a **horizontal `flowchart LR`** — rendered to
  `quality-attributes/diagrams/scenario-<ATTR>QA-<n>.png`, `Read` and visually cross-verified,
  embedded as the ```mermaid block **plus**
  `![<ATTR>QA-<n> six-part scenario](diagrams/scenario-<ATTR>QA-<n>.png)`.

If `scenarios.md` exists, copy each scenario's six-part detail and diagram into its file here and
add a `> Source: ../../quality-attributes/scenarios.md` line. If not, this is where the detail lives.

**Then build the quality attribute utility tree** — `quality-attributes/utility-tree.md` — as the
**summary of all quality attributes in the drivers**: `Utility → ISO/IEC 25010 characteristic →
refinement → <ATTR>QA-<n> (Importance, Difficulty)`. Render it as an indented list **and** a
Mermaid `mindmap` (`quality-attributes/diagrams/utility-tree.png`, visually verified). If a QAW
was run, import its tree (Step 9 of `/qaw`); otherwise construct it here from the scenario set.
`index.md` links to it. Template: `templates/utility-tree.md`.

### Step 6 — `index.md` — traceability matrix + coverage check
Write `index.md` from `templates/drivers-index.md`. The matrix has one row per driver:

| Driver | File | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|------|-------------|---------------------------|--------------|--------|
| UC-1 | `use-cases/UC-1.md` | BG-1, BG-2 | PQA-1, CON-4 | ADD iter 1 | open |
| AQA-1 | `quality-attributes/AQA-1.md` | BG-3 | — | ADD iter 2 | partially |
| CON-2 | `constraints/CON-2.md` | BG-1 | UC-1, UC-4 | — | open |

`Status` ∈ `open` / `in design` / `partially` / `addressed` / `retired`.
**Coverage check (mandatory):** every `BG-` supported by ≥ 1 `UC-` or `<ATTR>QA-`; every
`UC-` / `<ATTR>QA-` / `CON-` traces up to ≥ 1 `BG-`. Report any gaps explicitly.

### Step 7 — Prioritised driver list (in `index.md`)
The ordered list ADD/ATAM consume: `(H,H)` then `(H,M)` quality scenarios, the architecturally
significant use cases, then the hard constraints — each one line with its ID and file link.

### Step 8 — Change log
Append a dated line to `index.md`'s change log for every run: what was added / changed / retired.

## Tracking across the engagement

- `/attribute-driven-design` reads this directory as its Step-1 input and, after each iteration,
  reports which driver IDs moved to `partially` / `addressed` — update those files' `**Status**`
  and the `index.md` matrix.
- `/atam` reads it for business drivers and the utility tree; ATAM risk themes map back to `BG-n`.
- Re-run `/drivers` whenever scope changes; add files, never rewrite history — retire, don't delete.

## Rules

- Four driver kinds, four ID prefixes: `BG-`, `UC-`, `CON-`, `<ATTR>QA-`. IDs are sequential
  within their prefix and never reused or renumbered.
- **One file per driver** under the matching sub-directory; `index.md` is the only aggregate file.
- Functional requirements that shape the architecture are written as **use cases** (primary actor,
  trigger, numbered main success scenario) — never one-liners — and **each has its own proper UML
  use case diagram** (actors outside the boundary, use case inside, include/extend dashed),
  rendered and visually cross-verified.
- **Every quality attribute is a six-part quality attribute scenario** with a numeric response
  measure, an ISO/IEC 25010 classification, **and its own six-part scenario diagram**, rendered
  and visually cross-verified.
- Every driver file carries `**Status**`; every diagram is embedded as ```mermaid + a relative
  `![](diagrams/…​.png)` image line (renders on GitHub / GitLab).
- The `index.md` traceability matrix is mandatory and must have no orphan drivers — report gaps.
- Nothing is silently dropped — retired drivers keep their file marked `retired`.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until it passes both:

1. **Automated**: `python tests/validate.py architecture/drivers/` (recurses the directory) —
   exits 0. Checks IDs, per-file structure, six-part scenarios with numeric measures, a use case
   diagram in every `UC-*.md`, a scenario diagram in every `<ATTR>QA-*.md`, `index.md`
   traceability with no orphans, diagram rules, and the deprecated-`QAS-` guard.
2. **Best-practice checklist**: walk the *Architectural drivers* section of
   `references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix, re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
