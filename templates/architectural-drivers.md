# Architectural Drivers: <system>

- **Date**: <YYYY-MM-DD>
- **Owner**: <name>
- **Status**: draft | reviewed | baselined
- **Related artifacts**: `../quality-attributes/scenarios.md`, `../qaw/qaw-report.md`

> The four SEI architectural driver kinds: **business goals**, **primary functional requirements
> (use cases)**, **constraints**, **quality attributes**. IDs are sequential and never reused.

---

## 1. Business goals

| ID | Goal (`<stakeholder> needs <outcome> so that <business value>`) | Category | Stakeholder | Status |
|----|---------------------------------------------------------------|----------|-------------|--------|
| BG-1 | | growth / financial / reputation / society & law / product quality / process quality / stakeholder relations | | open |

## 2. Primary functional requirements — use cases

Only use cases with architectural impact. Full detail per use case:

### UC-1 — <goal-phrased name>
- **Primary actor**:
- **Supporting actors**:
- **Trigger**:
- **Preconditions**:
- **Main success scenario**: 1. … 2. … 3. …
- **Key alternate / exception flows**:
- **Architectural significance**: <which QA scenario, integration, or trust/process boundary it drives>
- **Related drivers**: BG-, <ATTR>QA-, CON-

### Use case diagram(s)

<Mermaid or PlantUML use case diagram per actor group / subsystem — via the `sei-diagrams` skill.
Rendered PNG: `diagrams/usecases-<group>.png`. Visually verified: yes/no.>

## 3. Constraints

| ID | Type | Constraint | Source | Hard / negotiable | Conflicts with |
|----|------|-----------|--------|-------------------|----------------|
| CON-1 | business \| technical \| regulatory | | | hard | — |

## 4. Quality attributes

Detail lives in `../quality-attributes/scenarios.md`. Summary here:

| ID | ISO/IEC 25010 characteristic / sub | One-line scenario | (Imp, Diff) |
|----|-----------------------------------|-------------------|-------------|
| PQA-1 | Performance efficiency / time behaviour | | (H, M) |

## 5. Traceability matrix

| Driver | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|-------------|---------------------------|--------------|--------|
| UC-1 | BG-1 | PQA-1, CON-4 | ADD iter 1 | open |
| PQA-1 | BG-1 | — | — | open |
| CON-1 | BG-2 | UC-1 | — | open |

`Status` ∈ open / in design / partially / addressed / retired.
**Coverage rule**: every BG supported by ≥ 1 UC or QA scenario; every UC / QA scenario / CON traces up to ≥ 1 BG.
Gaps found: <list or "none">.

## 6. Prioritised driver list (input to ADD / ATAM)

1. SQA-1 (H,H) — <one line>
2. UC-1 — <one line, architecturally significant>
3. CON-1 (hard) — <one line>
...

## Change log

| Date | Change |
|------|--------|
| <YYYY-MM-DD> | initial register |
