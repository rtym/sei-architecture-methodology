# Architectural Drivers — Personal Finance Tracker

- **Date**: 2026-09-06
- **Owner**: Roman Tymoshuk
- **Status**: reviewed
- **QA model**: ISO/IEC 25010:2023
- **Design purpose**: greenfield system
- **Stakeholders**: [stakeholders.md](stakeholders.md) (ST-1 … ST-6)
- **Design purpose**: greenfield system
- **Stakeholders**: [stakeholders.md](stakeholders.md) (ST-1 … ST-6)

> The top aggregate file of `drivers/`. One file per driver lives under
> [`business-goals/`](business-goals/README.md), [`use-cases/`](use-cases/README.md),
> [`constraints/`](constraints/README.md), [`quality-attributes/`](quality-attributes/README.md),
> [`concerns/`](concerns/README.md);
> each of those has its own `README.md` index. This file holds the ID legend, the traceability
> matrix, the coverage check, the prioritised list, and the change log.

## Driver inventory

### Business goals — [`business-goals/`](business-goals/README.md)
| ID | Goal (short) | File |
|----|--------------|------|
| BG-1 | 10 000 active users within 12 months (seed metrics) | [BG-1](business-goals/BG-1.md) |
| BG-2 | Pass SOC 2 Type II to sell to employers | [BG-2](business-goals/BG-2.md) |
| BG-3 | Ship a new report type every week | [BG-3](business-goals/BG-3.md) |
| BG-4 | Keep the infra bill within budget at launch scale | [BG-4](business-goals/BG-4.md) |

### Use cases — [`use-cases/`](use-cases/README.md)  (primary functional requirements)
| ID | Use case | Primary actor | Diagram | File |
|----|----------|---------------|---------|------|
| UC-1 | Record a transaction | Registered user | [diagram](use-cases/diagrams/UC-1.png) | [UC-1](use-cases/UC-1.md) |
| UC-2 | View the monthly dashboard | Registered user | [diagram](use-cases/diagrams/UC-2.png) | [UC-2](use-cases/UC-2.md) |
| UC-3 | Import a bank statement (CSV) | Registered user | [diagram](use-cases/diagrams/UC-3.png) | [UC-3](use-cases/UC-3.md) |
| UC-4 | Categorise transaction (`<<include>>`d by UC-1, UC-3) | Registered user | [diagram](use-cases/diagrams/UC-4.png) | [UC-4](use-cases/UC-4.md) |

Overview use case diagram: [`use-cases/diagrams/overview-core.png`](use-cases/diagrams/overview-core.png)
(Mermaid `flowchart` fallback — this is the Mermaid tree).

### Constraints — [`constraints/`](constraints/README.md)
| ID | Type | Constraint (short) | Hard / negotiable | File |
|----|------|--------------------|-------------------|------|
| CON-1 | technical | Mobile web only at launch | hard | [CON-1](constraints/CON-1.md) |
| CON-2 | business | One engineer, 3-month MVP | hard | [CON-2](constraints/CON-2.md) |
| CON-3 | business | Low-cost managed cloud tiers | negotiable | [CON-3](constraints/CON-3.md) |
| CON-4 | regulatory | Encryption in transit and at rest | hard | [CON-4](constraints/CON-4.md) |
| CON-5 | technical | PostgreSQL primary datastore | negotiable | [CON-5](constraints/CON-5.md) |

### Architectural concerns — [`concerns/`](concerns/README.md)  (ADD input; not traced to a BG)

| ID | Concern (short) | Kind | Priority | File |
|----|-----------------|------|:--------:|------|
| AC-1 | Keep the SOC 2 surface small | general | high | [AC-1](concerns/AC-1.md) |
| AC-2 | Dashboard iteration speed must stay high | general | medium | [AC-2](concerns/AC-2.md) |

### Quality attribute scenarios — [`quality-attributes/`](quality-attributes/README.md)
| ID | ISO 25010 characteristic / sub | One-line scenario | (V, R) | Diagram | File |
|----|-------------------------------|-------------------|:------:|---------|------|
| AQA-1 | Reliability / availability | Single-AZ failure recovers < 60 s; ≥ 99.5 %/mo | (H, H) | [scenario](quality-attributes/diagrams/scenario-AQA-1.png) | [AQA-1](quality-attributes/AQA-1.md) |
| PQA-1 | Performance efficiency / time behaviour | Dashboard < 1.5 s @ p95, 500 concurrent | (H, M) | [scenario](quality-attributes/diagrams/scenario-PQA-1.png) | [PQA-1](quality-attributes/PQA-1.md) |
| PQA-2 | Performance efficiency / capacity | 5 000-row CSV import < 30 s, interactive unaffected | (M, M) | [scenario](quality-attributes/diagrams/scenario-PQA-2.png) | [PQA-2](quality-attributes/PQA-2.md) |
| SQA-1 | Security / confidentiality | Cross-user access rejected + logged; 0 reads | (H, H) | [scenario](quality-attributes/diagrams/scenario-SQA-1.png) | [SQA-1](quality-attributes/SQA-1.md) |
| MQA-1 | Maintainability / modifiability | Add a report type in ≤ 1 person-day, 0 regressions | (M, M) | [scenario](quality-attributes/diagrams/scenario-MQA-1.png) | [MQA-1](quality-attributes/MQA-1.md) |
| UQA-1 | Interaction capability / operability | First transaction without help; ≥ 85 % completion | (M, M) | [scenario](quality-attributes/diagrams/scenario-UQA-1.png) | [UQA-1](quality-attributes/UQA-1.md) |

**Utility tree** (summary of the quality attributes in these drivers, **as a table**):
[`quality-attributes/utility-tree.md`](quality-attributes/utility-tree.md) — columns
*Quality attribute · Refinement (concern) · Leaf scenario · Priority (V, R) · Status*, one leaf
per row, `★` on each `(H, H)` leaf. `(V, R)` = business value and technical risk (`V ≈
Importance`, `R ≈ Difficulty`). Built from the QAW Step 9; ATAM step 5 reuses it.

**QA ID legend**: AQA availability · RQA reliability(other) · PQA performance · SQA security ·
SFQA safety · MQA modifiability · MNQA maintainability(other) · TQA testability · UQA usability ·
IQA interoperability · CQA compatibility · SCQA scalability · DQA deployability · PTQA portability
· ADQA adaptability · OQA observability · EQA energy · INQA integrability · FQA functional-suitability.
Never `QAS-`.

## Traceability matrix

| Driver | File | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|------|-------------|---------------------------|--------------|--------|
| UC-1 | [UC-1](use-cases/UC-1.md) | BG-1, BG-3 | PQA-1, MQA-1, CON-4 | ADD iter 1 | in design |
| UC-2 | [UC-2](use-cases/UC-2.md) | BG-1 | PQA-1, UQA-1 | ADD iter 2 | open |
| UC-3 | [UC-3](use-cases/UC-3.md) | BG-1 | PQA-2 | ADD iter 3 | open |
| UC-4 | [UC-4](use-cases/UC-4.md) | BG-1 | UC-1, UC-3 (`<<include>>`) | ADD iter 1 | in design |
| AQA-1 | [AQA-1](quality-attributes/AQA-1.md) | BG-1, BG-4 | CON-3, CON-5 | ADD iter 1 | at risk |
| PQA-1 | [PQA-1](quality-attributes/PQA-1.md) | BG-1 | UC-1, UC-2 | ADD iter 2 | open |
| PQA-2 | [PQA-2](quality-attributes/PQA-2.md) | BG-1 | UC-3 | ADD iter 3 | open |
| SQA-1 | [SQA-1](quality-attributes/SQA-1.md) | BG-2 | CON-4 | ADD iter 1 | at risk |
| MQA-1 | [MQA-1](quality-attributes/MQA-1.md) | BG-3 | UC-1 | ADD iter 1 | open |
| UQA-1 | [UQA-1](quality-attributes/UQA-1.md) | BG-1 | UC-2 | ADD iter 2 | open |
| CON-1 | [CON-1](constraints/CON-1.md) | BG-1 | UC-1, UC-2 | ADD iter 1 | open |
| CON-2 | [CON-2](constraints/CON-2.md) | BG-4 | — | ADD iter 1 | open |
| CON-3 | [CON-3](constraints/CON-3.md) | BG-4 | AQA-1 | ADD iter 1 | open |
| CON-4 | [CON-4](constraints/CON-4.md) | BG-2 | SQA-1 | ADD iter 1 | in design |
| CON-5 | [CON-5](constraints/CON-5.md) | BG-1 | AQA-1 | ADD iter 1 | open |

`Status` ∈ open / in design / partially / addressed / at risk (set by ATAM) / retired.

**Coverage check**: every BG (BG-1…BG-4) is supported by ≥ 1 UC or QA scenario; every UC / QA
scenario / CON traces up to ≥ 1 BG. Gaps found: **none**.

## Prioritised driver list (input to ADD / ATAM)

1. [SQA-1](quality-attributes/SQA-1.md) (H,H) — cross-user access rejected + logged; 0 reads
2. [AQA-1](quality-attributes/AQA-1.md) (H,H) — single-AZ failure recovers < 60 s; ≥ 99.5 %/mo
3. [PQA-1](quality-attributes/PQA-1.md) (H,M) — dashboard < 1.5 s @ p95 at 500 concurrent
4. [UC-1](use-cases/UC-1.md) — record a transaction (write load + latency + modifiability hot spot)
5. [UC-2](use-cases/UC-2.md) — monthly dashboard (performance-critical read path)
6. [CON-4](constraints/CON-4.md) (hard) — encryption in transit and at rest
7. [CON-2](constraints/CON-2.md) (hard) — one engineer, 3-month MVP

## Change log

| Date | Change |
|------|--------|
| 2026-09-06 | initial driver set; reviewed with founder + eng lead; utility tree imported from the QAW |
| 2026-09-06 | ADD iterations 1–2: UC-1, UC-4, SQA-1 → in design; concerns AC-1, AC-2 recorded |
| 2026-09-07 | ATAM: SQA-1 (R-1, R-2) and AQA-1 (R-3, R-4) → at risk; see [ATAM report](../atam/atam-report.md) |

---

**Navigation**: [architecture package](../README.md) · [stakeholders](stakeholders.md) · [quality attribute scenarios](../quality-attributes/scenarios.md) ·
[QAW](../qaw/qaw-report.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md) ·
[ATAM](../atam/atam-report.md) · [Views & Beyond docs](../docs/README.md)
