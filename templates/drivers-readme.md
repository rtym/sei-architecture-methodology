# Architectural Drivers — `drivers/README.md`: <SystemName>

- **Date**: <YYYY-MM-DD>
- **Owner**: <name>
- **Status**: draft | reviewed | baselined
- **QA model**: ISO/IEC 25010:2023  (or 2011 — state which)
- **Design purpose**: greenfield system | greenfield feature | brownfield replacement | brownfield extension | brownfield migration
- **Stakeholders**: [stakeholders.md](stakeholders.md)

<!-- Template notes (do not copy into the artifact):
     This is the top aggregate file of architecture/drivers/ — GitHub renders it on directory
     browse. One file per driver lives under business-goals/, use-cases/, constraints/,
     quality-attributes/ and concerns/; each of those gets its own small README.md index
     (${CLAUDE_PLUGIN_ROOT}/templates/subdir-readme.md). This file holds the ID legend, the
     traceability matrix, the coverage check, the prioritised list, and the change log.
     Every path below must be a working relative Markdown link.
     Replace the paragraph below with two or three plain sentences for the human reader. -->

<Two or three plain sentences for the reader: what this register covers (counts of goals, use
cases, constraints, scenarios), that each driver links to its own file, and where to start —
the prioritised list for what matters most, the traceability matrix for how drivers connect.>

## Driver inventory

### Business goals — [`business-goals/`](business-goals/README.md)
| ID | Goal (short) | File |
|----|--------------|------|
| BG-1 | <who needs what so that why> | [BG-1](business-goals/BG-1.md) |

### Use cases — [`use-cases/`](use-cases/README.md)  (primary functional requirements)
| ID | Use case | Primary actor | Diagram | File |
|----|----------|---------------|---------|------|
| UC-1 | <goal-phrased name> | <role> | [UC-1](use-cases/diagrams/UC-1.png) | [UC-1](use-cases/UC-1.md) |

Overview use case diagram(s): [`use-cases/diagrams/overview-<group>.png`](use-cases/diagrams/overview-core.png)

### Constraints — [`constraints/`](constraints/README.md)
| ID | Type | Constraint (short) | Hard / negotiable | File |
|----|------|--------------------|-------------------|------|
| CON-1 | technical \| business \| regulatory | <one line> | hard | [CON-1](constraints/CON-1.md) |

### Architectural concerns — [`concerns/`](concerns/README.md)  (ADD input; not traced to a BG)
| ID | Concern (short) | Kind | Priority | File |
|----|-----------------|------|:--------:|------|
| AC-1 | <one line> | general | high | [AC-1](concerns/AC-1.md) |

### Quality attribute scenarios — [`quality-attributes/`](quality-attributes/README.md)
| ID | ISO 25010 characteristic / sub | One-line scenario | (V, R) | Diagram | File |
|----|-------------------------------|-------------------|:------:|---------|------|
| AQA-1 | Reliability / availability | <one line> | (H, H) | [scenario](quality-attributes/diagrams/scenario-AQA-1.png) | [AQA-1](quality-attributes/AQA-1.md) |

**Utility tree** (summary of the quality attributes in these drivers, **as a table**):
[`quality-attributes/utility-tree.md`](quality-attributes/utility-tree.md) — columns
*Quality attribute · Refinement (concern) · Leaf scenario · Priority (V, R) · Status*, one leaf
per row, `★` on each `(H, H)` leaf. `(V, R)` = business value and technical risk (`V ≈
Importance`, `R ≈ Difficulty`). Built from the QAW (its Step 9) when one was run; ATAM step 5
reuses it.

**QA ID legend** — scenario IDs are prefixed by attribute, numbered within each prefix. Used in
this register: <only the prefixes that actually appear, e.g. AQA availability · SQA security>.
<!-- A scenario for a new attribute gets its own prefix, added to this list; never the flat
     QAS- prefix. List only the prefixes in use — the full 19-prefix table lives in
     ${CLAUDE_PLUGIN_ROOT}/references/quality-attribute-taxonomy.md and the
     architectural-drivers SKILL.md; dumping it here buries the reader. -->

## Traceability matrix

| Driver | File | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|------|-------------|---------------------------|--------------|--------|
| UC-1 | [UC-1](use-cases/UC-1.md) | BG-1 | AQA-1, CON-4 | ADD iter 1 | open |
| AQA-1 | [AQA-1](quality-attributes/AQA-1.md) | BG-1 | — | — | open |
| CON-1 | [CON-1](constraints/CON-1.md) | BG-2 | UC-1 | — | open |

`Status` ∈ open / in design / partially / addressed / at risk (set by ATAM) / retired.

**Coverage check**: every BG supported by ≥ 1 UC or QA scenario; every UC / QA scenario / CON
traces up to ≥ 1 BG. Retired drivers and architectural concerns (`AC-`) are excluded. Gaps
found: <list or "none">.

## Prioritised driver list (input to ADD / ATAM)

1. [SQA-1](quality-attributes/SQA-1.md) (H,H) — <one line>
2. [UC-1](use-cases/UC-1.md) — <one line, architecturally significant>
3. [CON-1](constraints/CON-1.md) (hard) — <one line>
...

## Change log

| Date | Change |
|------|--------|
| <YYYY-MM-DD> | initial driver set |

---

**Navigation**: [architecture package](../README.md) · [stakeholders](stakeholders.md)
<!-- link a sibling package (../qaw/, ../add/, ../atam/, ../docs/) here only once it exists —
     the package index ../README.md is the place that lists what has been produced -->
