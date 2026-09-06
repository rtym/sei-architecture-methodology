---
name: architectural-drivers
description: >-
  Collect, structure and track the four kinds of SEI architectural drivers — business goals,
  primary functional requirements (as UML use cases), constraints, and quality attribute scenarios
  — in one living register with a traceability matrix. Use when the user invokes /drivers or asks
  to capture architectural drivers, list use cases, track requirements/constraints/business goals,
  or assemble the driver inputs for an ADD or ATAM run.
version: 1.0.0
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

This skill maintains **one register** — `architecture/drivers/drivers.md` — and keeps it current
as drivers are added, changed, retired, or marked addressed. It also produces the **use case
diagram(s)** via `sei-diagrams`.

Deep reference: `references/quality-attribute-taxonomy.md` (for the QA vocabulary),
`references/add-method.md` (how drivers feed ADD). Templates: `templates/architectural-drivers.md`,
`templates/use-case.md`.

**Keep prompts short.** Numbered lists. **Draft first**, refine.

## Procedure

### Step 1 — Gather source material
Ask for / read: product brief, PRD, vision doc, backlog, SLAs, an existing requirements list,
org/regulatory context. If a QAW report or `scenarios.md` exists, plan to link (not duplicate) it.

### Step 2 — Business goals (`BG-n`)
Draft 3–7 business goals, each as *"<stakeholder> needs <outcome> so that <business value>"*.
Categories to probe (from the SEI business-goal categories): growth & market share, financial,
personal/reputational, responsibility to society/law, quality of product, quality of process,
stakeholder relationships. Present, confirm.

### Step 3 — Primary functional requirements as use cases (`UC-n`)
Identify only the use cases with **architectural impact** — those that exercise a quality
attribute, cross a trust or process boundary, drive a key integration, or dominate load. For each:

```markdown
### UC-<n> — <goal-phrased name>
- **Primary actor**: <role>
- **Supporting actors**: <systems / roles>
- **Trigger**: <event>
- **Preconditions**: <state>
- **Main success scenario**: 1. … 2. … 3. …
- **Key alternate / exception flows**: <the ones that matter architecturally>
- **Architectural significance**: <which QA scenario, integration, or boundary it drives>
- **Related drivers**: BG-1, AQA-1, CON-2
```

Then build a **use case diagram** per actor group or subsystem, using the `sei-diagrams` skill's
*Use case diagram* pattern (Mermaid convention, or PlantUML for full UML notation). Keep each
diagram to ≤ ~10 use cases; split by subsystem otherwise. Show it in the conversation, then render
to `architecture/drivers/diagrams/usecases-<group>.png`.

### Step 4 — Constraints (`CON-n`)
List each with: type (business / technical / regulatory), the constraint itself, its source, and
whether it is *hard* (cannot change) or *negotiable*. Flag constraints that conflict with a
business goal or a quality attribute scenario.

### Step 5 — Quality attributes (`<ATTR>QA-n`)
If the `quality-attributes` skill has produced `scenarios.md`, **reference** it: list the scenario IDs,
one-line summaries, and `(Importance, Difficulty)` here; keep the six-part detail there. If not,
run `/quality-attributes` now, or capture at least the top 5–8 scenarios inline using its template.

### Step 6 — Traceability matrix
Build the matrix that ties everything together and makes coverage checkable:

| Driver | Supports BG | Realised/constrained by | Addressed in | Status |
|--------|-------------|-------------------------|--------------|--------|
| UC-1 | BG-1, BG-2 | PQA-1 (perf), CON-4 (encryption) | ADD iter 1 | open |
| AQA-1 | BG-3 | — | ADD iter 2 | partially |
| CON-2 | BG-1 | UC-1, UC-4 | — | open |

`Status` ∈ `open` / `in design` / `partially` / `addressed` / `retired`. Update it as ADD
iterations and ATAM findings land. Every `BG-` must be supported by ≥ 1 `UC-` or `<ATTR>QA-`; every
`UC-`/`<ATTR>QA-`/`CON-` must trace up to ≥ 1 `BG-`. Report any gaps.

### Step 7 — Prioritised driver list
Emit the ordered list ADD/ATAM consume: `(H,H)` then `(H,M)` quality scenarios, the
architecturally significant use cases, and the hard constraints — each one line with its ID.

### Step 8 — Write / update the register
Write `architecture/drivers/drivers.md` from `templates/architectural-drivers.md`. On later runs,
**update in place**: append new IDs (never renumber), move changed drivers to their new wording
with a `> changed <date>: <what>` note, and refresh the matrix `Status` column. Keep a dated
change log at the bottom.

## Tracking across the engagement

- `/attribute-driven-design` reads this register as its Step-1 input and, after each iteration,
  reports which driver IDs moved to `partially` / `addressed` — update the matrix here.
- `/atam` reads it for business drivers and the utility tree; ATAM risk themes map back to `BG-n`.
- Re-run `/drivers` whenever scope changes; the register is the single place drivers live.

## Rules

- Four driver kinds, four ID prefixes: `BG-`, `UC-`, `CON-`, `<ATTR>QA-`. IDs are sequential and never
  reused or renumbered.
- Functional requirements that shape the architecture are written as **use cases** with at least a
  primary actor, a trigger, and a main success scenario — not one-liners.
- Every use case group is drawn as a UML use case diagram via `sei-diagrams`.
- Quality attribute detail lives in the `quality-attributes` skill's `scenarios.md`; this register
  references it, and only inlines detail when that file doesn't exist yet.
- The traceability matrix is mandatory and must have no orphan drivers (every driver connects up
  to a business goal) — report gaps explicitly.
- The register is updated in place across the engagement; nothing is silently dropped — retired
  drivers are marked `retired`, not deleted.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until the generated artifact passes both:

1. **Automated**: `python tests/validate.py architecture/drivers/drivers.md` — exits 0 (from the plugin root, or point at
   the plugin's `tests/validate.py`). It checks IDs, structure, six-part scenarios with numeric
   measures, traceability with no orphans, diagram rules, and the deprecated-`QAS-` guard.
2. **Best-practice checklist**: walk the relevant section of
   `references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix,
   re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
