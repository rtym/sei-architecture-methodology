---
name: quality-attributes
description: >-
  Turn vague quality goals ("fast", "secure", "scalable") into measurable SEI six-part quality
  attribute scenarios and a prioritised driver list. Use when the user invokes /quality-attributes
  or asks to define quality attributes, write NFRs / non-functional requirements as scenarios,
  build a utility tree, or produce architectural drivers for an ADD or ATAM run.
version: 1.0.0
allowed-tools: [Read, Write, Bash, Glob]
---

# Quality attribute scenarios

Produce **measurable** quality attribute scenarios in the SEI six-part form, plus a prioritised
driver list that ADD and ATAM can consume directly.

Output file: `architecture/quality-attributes/scenarios.md` (create the folder).
Deep reference: `references/quality-attribute-taxonomy.md` at the plugin root.

**Keep prompts short.** Draft first, refine second. Offer choices as numbered lists.

## The six-part scenario

Every scenario has exactly these parts (SEI / Bass-Clements-Kazman):

| Part | Question it answers | Example |
|------|---------------------|---------|
| **Source of stimulus** | Who or what generates the stimulus? | A registered user; a downstream service; an operator; a code commit |
| **Stimulus** | What event arrives at the system? | 1 000 concurrent dashboard requests; a malformed message; a request to add a report type |
| **Artifact** | What part is stimulated? | The whole system; the checkout service; the data store; the CI pipeline |
| **Environment** | What is the system's state when it happens? | Normal operation; peak load; degraded mode; during deployment |
| **Response** | What must the system do? | Processes all requests; rejects and logs; change is made with no ripple |
| **Response measure** | How is success measured, numerically? | p95 latency < 1.5 s; 0 successful cross-tenant reads; ≤ 1 person-day, 0 regressions |

A scenario without a **numeric response measure** is not finished — push until there is one.

## Quality attribute taxonomy — ISO/IEC 25010:2023

Classify every scenario against the **ISO/IEC 25010:2023** product quality model. This is the
standard taxonomy; the SEI six-part scenario is the *form*, ISO 25010 supplies the *vocabulary*.
Full definitions, the sub-characteristic breakdown, the **general-scenario "portions"** menu
(the range of values each of the six parts can take), and the per-attribute tactics-based
questionnaire are in `references/quality-attribute-taxonomy.md` (with tactic and pattern lists
in `references/tactics-catalog.md` and `references/architecture-patterns.md`). The full
**general-scenario portion tables for all 10 attributes** (availability, deployability, energy
efficiency, integrability, modifiability, performance, safety, security, testability, usability)
— the menu of values for each of the six parts, plus a worked concrete example — are in
`references/quality-attribute-scenarios.md`. Build each concrete scenario by choosing values
from the portions and making the response measure numeric.
For a cloud or mobile system, `references/runtime-environments.md` lists the environment-specific
stimuli worth a scenario (cold start, zone loss, autoscale lag, offline operation, battery,
OS eviction).

| # | ISO/IEC 25010:2023 characteristic | Sub-characteristics | SEI / BCK term often used |
|---|-----------------------------------|---------------------|--------------------------|
| 1 | **Functional suitability** | completeness, correctness, appropriateness | (functional — usually FRs, not QAS) |
| 2 | **Performance efficiency** | time behaviour, resource utilization, capacity | performance |
| 3 | **Compatibility** | co-existence, interoperability | interoperability |
| 4 | **Interaction capability** | appropriateness recognizability, learnability, operability, user error protection, user engagement, inclusivity, user assistance, self-descriptiveness | usability |
| 5 | **Reliability** | faultlessness, availability, fault tolerance, recoverability | availability |
| 6 | **Security** | confidentiality, integrity, non-repudiation, accountability, authenticity, resistance | security |
| 7 | **Maintainability** | modularity, reusability, analysability, modifiability, testability | modifiability, testability |
| 8 | **Flexibility** | adaptability, scalability, installability, replaceability | scalability, portability, deployability |
| 9 | **Safety** | operational constraint, risk identification, fail safe, hazard warning, safe integration | safety |

For each characteristic (and, where useful, each sub-characteristic) decide:
**not a concern** / **implicit (default is fine)** / **architecturally significant → write a scenario**.

Record every scenario with its ISO characteristic **and** sub-characteristic, e.g.
`QA: Reliability / availability`. If the project mandates the older **ISO/IEC 25010:2011** 8-model
(no *Flexibility* / *Safety*; *Usability* and *Portability* instead), say so in the file header and
use that column set.

## Procedure

### Step 1 — Gather raw material

Ask for whatever exists: a product brief, PRD, business goals, SLA/SLO text, an existing NFR list,
a system description. Read any files the user points at. If nothing exists, ask three questions:
what does the system do, who uses it, what would make it fail in the eyes of its sponsor.

### Step 2 — Elicit business goals

List the **business goals** (`BG-1`, `BG-2`, …) the architecture must serve — each in the form
*"<stakeholder> needs <outcome> so that <business value>"*. Scenarios trace back to these. Keep to
3–7 goals. Present and confirm.

### Step 3 — Draft scenarios

Propose a **complete first-draft set** of 8–15 scenarios covering the significant attributes from
the taxonomy. For each, fill all six parts and give:

- an **attribute-prefixed ID** — `<ATTR>QA-<n>`, numbered per prefix: availability `AQA-1`,
  security `SQA-1`, performance `PQA-1`, modifiability `MQA-1`, usability `UQA-1`, … (full code
  table in the `architectural-drivers` skill),
- the **ISO/IEC 25010 characteristic and sub-characteristic**,
- the **business goal(s)** it supports,
- a **priority pair** `(Importance, Difficulty)` each `H` / `M` / `L` — Importance = to the
  business; Difficulty = expected architectural/technical challenge (the architect's estimate).

Present as a table. Tell the user which parts you guessed so they correct the right cells.

### Step 4 — Refine and fill gaps

For weak scenarios: replace generic sources ("user") with specific roles, replace "should be fast"
with a number and a percentile, name the concrete artifact, state the environment explicitly.
Add scenarios for any taxonomy attribute the user flags as significant but uncovered.

### Step 5 — Visualise each scenario as a UML scenario diagram

Every quality attribute scenario is also drawn as the canonical SEI **six-part scenario diagram**
so the whole picture — *source → stimulus → (artifact, in environment) → response → response
measure* — is visible at a glance. Use the `sei-diagrams` skill's **"Quality attribute scenario"**
diagram pattern (`skills/sei-diagrams/SKILL.md`, section *Quality attribute scenario diagram*).

For each `<ATTR>QA-n`:
1. Render the Mermaid `flowchart LR` for that scenario, filled with its six parts, using the
   shared theme. Show it in the conversation.
2. On request, batch-render all scenario diagrams to PNG into
   `architecture/quality-attributes/diagrams/<ATTR>QA-<n>.png` with `scripts/render.sh`.
3. Embed the diagram (or a link to the PNG) directly under the scenario's row/section in
   `scenarios.md`.

### Step 6 — Build the utility tree (optional but recommended)

Organise the scenarios into a **utility tree — a table, not a diagram**: one row per leaf
scenario with columns *Quality attribute · Refinement (concern) · Leaf scenario (ID + response
measure) · Priority (V, R) · Status*. `(V, R)` = business value and technical risk, each H/M/L
(`V ≈ Importance`, `R ≈ Difficulty`); mark a `(H, H)` leaf `★`. This is the same structure ATAM
step 5 uses. Template: `templates/utility-tree.md`.

### Step 7 — Prioritised driver list

Emit the final **architectural drivers** section: the `(H,H)` and `(H,M)` scenarios first — these
are what ADD iterations and ATAM analysis target. List functional requirements with architectural
impact — recorded as use cases (`UC-n`) — and constraints (`CON-n`) alongside.

### Step 8 — Write the file

Write `architecture/quality-attributes/scenarios.md` from the template below. Confirm the path.

## Output template

```markdown
# Quality Attribute Scenarios: <system>

- **Date**: <YYYY-MM-DD>
- **Source material**: <brief / PRD / interview>
- **Status**: draft | reviewed | baselined

## Business goals

| ID | Goal | Stakeholder |
|----|------|-------------|
| BG-1 | <stakeholder needs outcome so that value> | <role> |

## Quality attribute scenarios

QA column = `ISO/IEC 25010 characteristic / sub-characteristic`.

| ID | QA (ISO 25010) | Source | Stimulus | Artifact | Environment | Response | Response measure | BG | Imp | Diff |
|----|----------------|--------|----------|----------|-------------|----------|------------------|----|-----|------|
| PQA-1 | Performance efficiency / time behaviour | Registered user | Loads dashboard (500 concurrent) | Dashboard service | Normal operation | Renders charts + recent activity | Interactive < 1.5 s @ p95 | BG-1 | H | M |

### PQA-1 — scenario diagram

<Mermaid six-part scenario diagram, or link to architecture/quality-attributes/diagrams/PQA-1.png>


## Primary functional requirements — use cases with architectural impact

| ID | Use case name | Why it shapes the architecture |
|----|---------------|--------------------------------|
| UC-1 | | |

## Constraints

| ID | Type (business / technical / regulatory) | Description |
|----|-----------------------------------------|-------------|

## Utility tree

| Quality attribute | Refinement (concern) | Leaf scenario (ID — one line + measure) | Priority (V, R) | Status |
|-------------------|----------------------|----------------------------------------|:---------------:|:------:|
| Security | Confidentiality | SQA-1 — 0 cross-tenant reads; 100 % logged | (H, H) `★` | open |
| Performance efficiency | Time behaviour | PQA-1 — dashboard < 1.5 s @ p95, 500 concurrent | (H, M) | open |

_Reading the tree_: a refinement with no leaf → look for an unrecorded ASR; the `★` `(H,H)`
leaves get the most attention.

## Architectural drivers (prioritised)

1. SQA-1 (H,H) — <one line>
2. PQA-1 (H,M) — <one line>
...
```

## Rules

- Every scenario has all six parts **and** a numeric response measure.
- Every scenario is classified against **ISO/IEC 25010:2023** (characteristic + sub-characteristic);
  note in the header if the 2011 model is used instead.
- Every scenario is visualised as a six-part UML scenario diagram (Step 5) and the diagram is
  embedded or linked next to the scenario.
- IDs: `BG-`, `UC-` (use cases), `CON-`, and attribute-prefixed QA scenarios (`AQA-`, `SQA-`, `PQA-`, … — see the architectural-drivers skill). Sequential within each prefix; never reused.
- Every scenario cites ≥ 1 business goal.
- Priority is the `(Importance, Difficulty)` pair, not a single word.
- Keep the total set small enough to act on: 8–15 scenarios; more than 20 means the net is too wide.
- The file is the source of truth — write it before declaring the activity done.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until the generated artifact passes both:

1. **Automated**: `python tests/validate.py architecture/quality-attributes/scenarios.md` — exits 0 (from the plugin root, or point at
   the plugin's `tests/validate.py`). It checks IDs, structure, six-part scenarios with numeric
   measures, traceability with no orphans, diagram rules, and the deprecated-`QAS-` guard.
2. **Best-practice checklist**: walk the relevant section of
   `references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix,
   re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
