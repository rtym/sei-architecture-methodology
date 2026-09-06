# Architectural Drivers — Index: Personal Finance Tracker

- **Date**: 2026-09-06
- **Owner**: Roman Tymoshuk
- **Status**: reviewed
- **QA model**: ISO/IEC 25010:2023

> The only aggregate file in `drivers/`. One file per driver lives under `business-goals/`,
> `use-cases/`, `constraints/`, `quality-attributes/`.

## Driver inventory

### Business goals — `business-goals/`
| ID | Goal (short) | File |
|----|--------------|------|
| BG-1 | 10 000 active users within 12 months (seed metrics) | `business-goals/BG-1.md` |
| BG-2 | Pass SOC 2 Type II to sell to employers | `business-goals/BG-2.md` |
| BG-3 | Ship a new report type every week | `business-goals/BG-3.md` |
| BG-4 | Keep the infra bill within budget at launch scale | `business-goals/BG-4.md` |

### Use cases — `use-cases/`  (primary functional requirements)
| ID | Use case | Primary actor | Diagram | File |
|----|----------|---------------|---------|------|
| UC-1 | Record a transaction | Registered user | `use-cases/diagrams/UC-1.png` | `use-cases/UC-1.md` |
| UC-2 | View the monthly dashboard | Registered user | `use-cases/diagrams/UC-2.png` | `use-cases/UC-2.md` |
| UC-3 | Import a bank statement (CSV) | Registered user | `use-cases/diagrams/UC-3.png` | `use-cases/UC-3.md` |

Overview use case diagram: `use-cases/diagrams/overview-core.png` (PlantUML, true UML notation).

### Constraints — `constraints/`
| ID | Type | Constraint (short) | Hard / negotiable | File |
|----|------|--------------------|-------------------|------|
| CON-1 | technical | Mobile web only at launch | hard | `constraints/CON-1.md` |
| CON-2 | business | One engineer, 3-month MVP | hard | `constraints/CON-2.md` |
| CON-3 | business | Low-cost managed cloud tiers | negotiable | `constraints/CON-3.md` |
| CON-4 | regulatory | Encryption in transit and at rest | hard | `constraints/CON-4.md` |
| CON-5 | technical | PostgreSQL primary datastore | negotiable | `constraints/CON-5.md` |

### Quality attribute scenarios — `quality-attributes/`
| ID | ISO 25010 characteristic / sub | One-line scenario | (Imp, Diff) | Diagram | File |
|----|-------------------------------|-------------------|-------------|---------|------|
| AQA-1 | Reliability / availability | Single-AZ failure recovers < 60 s; ≥ 99.5 %/mo | (H, H) | `quality-attributes/diagrams/scenario-AQA-1.png` | `quality-attributes/AQA-1.md` |
| PQA-1 | Performance efficiency / time behaviour | Dashboard < 1.5 s @ p95, 500 concurrent | (H, M) | `quality-attributes/diagrams/scenario-PQA-1.png` | `quality-attributes/PQA-1.md` |
| PQA-2 | Performance efficiency / capacity | 5 000-row CSV import < 30 s, interactive unaffected | (M, M) | `quality-attributes/diagrams/scenario-PQA-2.png` | `quality-attributes/PQA-2.md` |
| SQA-1 | Security / confidentiality | Cross-user access rejected + logged; 0 reads | (H, H) | `quality-attributes/diagrams/scenario-SQA-1.png` | `quality-attributes/SQA-1.md` |
| MQA-1 | Maintainability / modifiability | Add a report type in ≤ 1 person-day, 0 regressions | (M, M) | `quality-attributes/diagrams/scenario-MQA-1.png` | `quality-attributes/MQA-1.md` |
| UQA-1 | Interaction capability / operability | First transaction without help; ≥ 85 % completion | (M, M) | `quality-attributes/diagrams/scenario-UQA-1.png` | `quality-attributes/UQA-1.md` |

**Utility tree** (summary of the quality attributes in these drivers):
`quality-attributes/utility-tree.md` — `Utility → ISO/IEC 25010 characteristic → refinement →
<ATTR>QA-<n> (Imp, Diff)`, with a rendered `mindmap`. Built from the QAW Step 9. ATAM step 5 reuses it.

**QA ID legend**: AQA availability · RQA reliability(other) · PQA performance · SQA security ·
SFQA safety · MQA modifiability · MNQA maintainability(other) · TQA testability · UQA usability ·
IQA interoperability · CQA compatibility · SCQA scalability · DQA deployability · PTQA portability
· ADQA adaptability · OQA observability · EQA energy · INQA integrability · FQA functional-suitability.
Never `QAS-`.

## Traceability matrix

| Driver | File | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|------|-------------|---------------------------|--------------|--------|
| UC-1 | `use-cases/UC-1.md` | BG-1, BG-3 | PQA-1, MQA-1, CON-4 | ADD iter 1 | in design |
| UC-2 | `use-cases/UC-2.md` | BG-1 | PQA-1, UQA-1 | ADD iter 2 | open |
| UC-3 | `use-cases/UC-3.md` | BG-1 | PQA-2 | ADD iter 3 | open |
| AQA-1 | `quality-attributes/AQA-1.md` | BG-1, BG-4 | CON-3, CON-5 | ADD iter 1 | open |
| PQA-1 | `quality-attributes/PQA-1.md` | BG-1 | UC-1, UC-2 | ADD iter 2 | open |
| PQA-2 | `quality-attributes/PQA-2.md` | BG-1 | UC-3 | ADD iter 3 | open |
| SQA-1 | `quality-attributes/SQA-1.md` | BG-2 | CON-4 | ADD iter 1 | in design |
| MQA-1 | `quality-attributes/MQA-1.md` | BG-3 | UC-1 | ADD iter 1 | open |
| UQA-1 | `quality-attributes/UQA-1.md` | BG-1 | UC-2 | ADD iter 2 | open |
| CON-1 | `constraints/CON-1.md` | BG-1 | UC-1, UC-2 | ADD iter 1 | open |
| CON-2 | `constraints/CON-2.md` | BG-4 | — | ADD iter 1 | open |
| CON-3 | `constraints/CON-3.md` | BG-4 | AQA-1 | ADD iter 1 | open |
| CON-4 | `constraints/CON-4.md` | BG-2 | SQA-1 | ADD iter 1 | in design |
| CON-5 | `constraints/CON-5.md` | BG-1 | AQA-1 | ADD iter 1 | open |

`Status` ∈ open / in design / partially / addressed / retired.

**Coverage check**: every BG (BG-1…BG-4) is supported by ≥ 1 UC or QA scenario; every UC / QA
scenario / CON traces up to ≥ 1 BG. Gaps found: **none**.

## Prioritised driver list (input to ADD / ATAM)

1. SQA-1 (H,H) — cross-user access rejected + logged; 0 reads — `quality-attributes/SQA-1.md`
2. AQA-1 (H,H) — single-AZ failure recovers < 60 s; ≥ 99.5 %/mo — `quality-attributes/AQA-1.md`
3. PQA-1 (H,M) — dashboard < 1.5 s @ p95 at 500 concurrent — `quality-attributes/PQA-1.md`
4. UC-1 — record a transaction (write load + latency + modifiability hot spot) — `use-cases/UC-1.md`
5. UC-2 — monthly dashboard (performance-critical read path) — `use-cases/UC-2.md`
6. CON-4 (hard) — encryption in transit and at rest — `constraints/CON-4.md`
7. CON-2 (hard) — one engineer, 3-month MVP — `constraints/CON-2.md`

## Change log

| Date | Change |
|------|--------|
| 2026-09-06 | initial driver set; reviewed with founder + eng lead; utility tree imported from the QAW |
