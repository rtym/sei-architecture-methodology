---
name: atam
description: >-
  Run a SEI Architecture Tradeoff Analysis Method (ATAM) evaluation of an existing or proposed
  software architecture. Use when the user invokes /atam or asks to evaluate / review / assess an
  architecture, build a quality-attribute utility tree, or identify architectural risks,
  sensitivity points, tradeoff points and risk themes.
version: 1.0.0
allowed-tools: [Read, Write, Bash, Glob]
---

# Architecture Tradeoff Analysis Method (ATAM)

Facilitate a SEI ATAM evaluation. ATAM assesses whether an architecture satisfies its quality
attribute goals and reveals how quality attributes **trade off** against one another.

Output file: `architecture/atam/atam-report.md` (create the folder). Update after every step.
Deep reference: `references/atam-method.md`. Report template: `templates/atam-report.md`.
Tactic and pattern catalogs for Step 6: `references/tactics-catalog.md`,
`references/architecture-patterns.md`.

### Full ATAM or a lightweight evaluation?

Ask up front which mode fits:

- **Full ATAM** (this skill's default) — external or cross-team evaluators, two phases, a formal
  report; for high-risk, high-cost, or contentious architectures.
- **Lightweight Architecture Evaluation** — the same conceptual steps (business drivers →
  approaches → utility tree → analyse the `(H,H)`/`(H,M)` scenarios → risks / sensitivity /
  tradeoff points → risk themes) run in ~half a day by the internal team, no formal report, no
  Phase 2 stakeholder round. Use it as a routine self-check each iteration or before a release.
  Produce the same registers in `atam-report.md`; skip Steps 7–8 and mark the report
  `Lightweight`.

**Keep prompts short.** Numbered lists. Announce each step in one line. **Draft first**, refine.

## Inputs to gather up front

- The **architecture documentation** (point me at it — ADD `Architecture.md`, a Views & Beyond
  package, C4 diagrams, ADRs, or a description).
- The **business drivers** / context and, if they exist, quality attribute scenarios
  (`architecture/quality-attributes/scenarios.md` or a QAW report).
- Who the **stakeholders** are (for Phase 2).

If the architecture is undocumented, run enough of `/architecture-docs` first to have something
concrete to analyse, or capture a minimal container + deployment view here.

## Outputs (ATAM's deliverables — all in the report)

| Deliverable | What it is |
|-------------|------------|
| **Architectural approaches** | The patterns / tactics / styles the architecture uses |
| **Utility tree** | A table of prioritised quality-attribute scenarios, each leaf `(V, R)` = (business value, technical risk) |
| **Scenario analysis** | Per scenario: approaches invoked, questions, findings |
| **Risks** | Decisions that may lead to undesirable consequences given the drivers |
| **Non-risks** | Decisions that are safe *given the current drivers* (record the assumption) |
| **Sensitivity points** | A property of one element that materially affects one quality attribute measure |
| **Tradeoff points** | A sensitivity point affecting **more than one** quality attribute in opposite directions |
| **Risk themes** | Groups of related risks that point to a systemic weakness; each mapped to a business driver it endangers |

## The nine steps (three evaluation phases)

### Phase 0 — Partnership and preparation
Confirm scope, the architecture package to be evaluated, the stakeholder list for Phase 2, and the
schedule. Record in the report.

### Phase 1 — Evaluation (with the architect and a small team)

**Step 1 — Present the ATAM.** State the method, phases, and the seven output kinds above.

**Step 2 — Present the business drivers.** Capture: system purpose, primary business goals
(`BG-n`), major functional requirements, constraints, and the quality attributes the business
cares most about. Confirm the summary.

**Step 3 — Present the architecture.** Capture technical constraints, external systems the
architecture interacts with, and the architectural approaches used, at an appropriate level of
detail (context → containers → key components; key runtime flows; deployment). Reference or
render the diagrams via `sei-diagrams`.

**Step 4 — Identify architectural approaches.** List the styles, reference architectures, and
tactics in use (`AA-1`, `AA-2`, …) — layered, microservices, event-driven, CQRS, circuit breaker,
replication, cache-aside, bulkhead, etc. Note where each is applied.

**Step 5 — Generate the quality attribute utility tree.** Build it **as a table** (not a
diagram): one row per leaf scenario, columns *Quality attribute (ISO/IEC 25010) · Refinement ·
Leaf scenario (ID + response measure) · Priority (V, R) · Status*. `(V, R)` = business value and
technical risk, each H/M/L (`V ≈ Importance`, `R ≈ Difficulty`); mark a `(H, H)` leaf `★`.
Import from `scenarios.md` / QAW if available; otherwise generate a first draft from the
business drivers and refine. The `★` **high/high** and **high/medium** leaves are what Step 6
analyses. Template: `templates/utility-tree.md`.

**Step 6 — Analyse the architectural approaches.** For each high-priority utility-tree scenario:
1. Walk the architecture and identify which approaches (`AA-n`) are invoked to satisfy it.
2. Ask analysis **questions** about those approaches — use the **tactics-based questionnaire**
   for the relevant quality attribute (`references/tactics-catalog.md`) as the question bank.
3. Record findings as **risks**, **non-risks**, **sensitivity points** (`S-n`), **tradeoff
   points** (`T-n`). Use the analysis table below.

Scenario analysis table (one per analysed scenario):

```markdown
#### <ATTR>QA-id — <one-line scenario> (Imp, Diff)
- **Attribute / refinement**: <ISO 25010 characteristic / refinement>
- **Approaches invoked**: AA-2 (layered), AA-5 (cache-aside)
- **Analysis questions & answers**: …

| Finding | Type | Element / decision | Affected attribute(s) | Note |
|---------|------|--------------------|-----------------------|------|
| R-1 | Risk | Single Redis node, no replica | Availability | SPOF; AQA-1 requires 99.5% |
| N-1 | Non-risk | Stateless API replicas behind LB | Availability | valid while sessions stay externalised |
| S-1 | Sensitivity | Cache TTL vs dashboard freshness | Performance | TTL up → latency down, staleness up |
| T-1 | Tradeoff | Cache TTL | Performance vs. correctness/consistency | see S-1 |
```

### Phase 2 — Evaluation (with the broader stakeholder group)

**Step 7 — Brainstorm and prioritise scenarios.** Round-robin scenario brainstorming with the
full stakeholder group (use-case, growth, and exploratory scenarios). Then vote-prioritise
(same rule as QAW: vote budget = 30 % of scenario count, rounded up). Compare the prioritised
list with the Step-5 utility tree; note agreements and gaps.

**Step 8 — Analyse architectural approaches (again).** Repeat Step 6 for the highly-ranked
scenarios from Step 7 that were not already covered.

### Phase 3 — Reporting

**Step 9 — Present results.** Consolidate:
- all architectural approaches,
- the utility tree,
- all scenarios analysed,
- the full **risks / non-risks / sensitivity points / tradeoff points** registers,
- **risk themes** — cluster the risks, name each theme, and map it to the business driver(s)
  (`BG-n`) it threatens,
- recommendations (often: targeted `/add` iterations to address the top risk themes).

## Rules

- Every risk, non-risk, sensitivity, and tradeoff cites the element/decision and the affected
  quality attribute(s) (ISO/IEC 25010 characteristic).
- A **non-risk** always records the assumption under which it is safe.
- A **tradeoff point** must show ≥ 2 attributes moving in tension — otherwise it is only a
  sensitivity point.
- Every **risk theme** maps to ≥ 1 business driver.
- The utility tree is a **table**; each leaf row carries a `(V, R)` = (business value, technical
  risk) pair; Step 6 analyses the `★` H/H and H/M leaves.
- The report is written incrementally, section per step.
- ATAM **evaluates**; it does not redesign. Fixes are recommendations → hand off to `/add`.
- **Report format**: `atam-report.md` is the working file. For the deliverable, ask the user
  **Markdown, HTML, or both** and build it with
  `scripts/build-report.sh architecture/atam/atam-report.md --format <fmt> --embed-diagrams
  --title "ATAM Evaluation — <system>"`.
- Approach diagrams go through `sei-diagrams` and are visually cross-verified from their
  rendered PNG before inclusion. The utility tree is a table — it has no diagram.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until the generated artifact passes both:

1. **Automated**: `python tests/validate.py architecture/atam/atam-report.md` — exits 0 (from the plugin root, or point at
   the plugin's `tests/validate.py`). It checks IDs, structure, six-part scenarios with numeric
   measures, traceability with no orphans, diagram rules, and the deprecated-`QAS-` guard.
2. **Best-practice checklist**: walk the relevant section of
   `references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix,
   re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
