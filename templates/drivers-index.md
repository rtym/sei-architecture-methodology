# Architectural Drivers — Index: <system>

- **Date**: <YYYY-MM-DD>
- **Owner**: <name>
- **Status**: draft | reviewed | baselined
- **QA model**: ISO/IEC 25010:2023  (or 2011 — state which)

> The only aggregate file in `architecture/drivers/`. One file per driver lives under
> `business-goals/`, `use-cases/`, `constraints/`, `quality-attributes/`. This index holds the
> ID legend, the traceability matrix, the coverage check, the prioritised list, and the change log.

## Driver inventory

### Business goals — `business-goals/`
| ID | Goal (short) | File |
|----|--------------|------|
| BG-1 | <who needs what so that why> | `business-goals/BG-1.md` |

### Use cases — `use-cases/`  (primary functional requirements)
| ID | Use case | Primary actor | Diagram | File |
|----|----------|---------------|---------|------|
| UC-1 | <goal-phrased name> | <role> | `use-cases/diagrams/UC-1.png` | `use-cases/UC-1.md` |

Overview use case diagram(s): `use-cases/diagrams/overview-<group>.png`

### Constraints — `constraints/`
| ID | Type | Constraint (short) | Hard / negotiable | File |
|----|------|--------------------|-------------------|------|
| CON-1 | technical \| business \| regulatory | <one line> | hard | `constraints/CON-1.md` |

### Quality attribute scenarios — `quality-attributes/`
| ID | ISO 25010 characteristic / sub | One-line scenario | (Imp, Diff) | Diagram | File |
|----|-------------------------------|-------------------|-------------|---------|------|
| AQA-1 | Reliability / availability | <one line> | (H, H) | `quality-attributes/diagrams/scenario-AQA-1.png` | `quality-attributes/AQA-1.md` |

**Utility tree** (summary of the quality attributes in these drivers):
`quality-attributes/utility-tree.md` — `Utility → ISO/IEC 25010 characteristic → refinement →
<ATTR>QA-<n> (Imp, Diff)`, with a rendered `mindmap`. Built from the QAW (its Step 9) when one
was run, otherwise assembled here. ATAM step 5 reuses it.

**QA ID legend** (attribute → prefix): AQA availability · RQA reliability(other) · PQA performance
· SQA security · SFQA safety · MQA modifiability · MNQA maintainability(other) · TQA testability ·
UQA usability · IQA interoperability · CQA compatibility · SCQA scalability · DQA deployability ·
PTQA portability · ADQA adaptability · OQA observability · EQA energy · INQA integrability ·
FQA functional-suitability. Coin a new `<MNEMONIC>QA` and record it here if needed. Never `QAS-`.

## Traceability matrix

| Driver | File | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|------|-------------|---------------------------|--------------|--------|
| UC-1 | `use-cases/UC-1.md` | BG-1 | AQA-1, CON-4 | ADD iter 1 | open |
| AQA-1 | `quality-attributes/AQA-1.md` | BG-1 | — | — | open |
| CON-1 | `constraints/CON-1.md` | BG-2 | UC-1 | — | open |

`Status` ∈ open / in design / partially / addressed / retired.

**Coverage check**: every BG supported by ≥ 1 UC or QA scenario; every UC / QA scenario / CON
traces up to ≥ 1 BG. Gaps found: <list or "none">.

## Prioritised driver list (input to ADD / ATAM)

1. SQA-1 (H,H) — <one line> — `quality-attributes/SQA-1.md`
2. UC-1 — <one line, architecturally significant> — `use-cases/UC-1.md`
3. CON-1 (hard) — <one line> — `constraints/CON-1.md`
...

## Change log

| Date | Change |
|------|--------|
| <YYYY-MM-DD> | initial driver set |
