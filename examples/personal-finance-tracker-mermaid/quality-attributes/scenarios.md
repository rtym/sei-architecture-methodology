# Quality Attribute Scenarios: Personal Finance Tracker

- **Date**: 2026-09-06
- **Source material**: product brief + founder/eng-lead interview
- **Status**: reviewed
- **QA model**: ISO/IEC 25010:2023
- **Mode**: register — the per-scenario files and diagrams live in [`../drivers/quality-attributes/`](../drivers/quality-attributes/README.md); this file is the summary
- **Mode**: register — the per-scenario files and diagrams live in [`../drivers/quality-attributes/`](../drivers/quality-attributes/README.md); this file is the summary

## Business goals

| ID | Goal | Stakeholder |
|----|------|-------------|
| BG-1 | The founder needs 10 000 active users within 12 months so that the product reaches seed-round metrics | Founder |
| BG-2 | The company needs to pass a SOC 2 Type II audit so that it can sell to employers so that revenue grows | Founder |
| BG-3 | Engineering needs to ship new report types weekly so that the product keeps pace with competitors | Eng lead |
| BG-4 | Operations needs the infra bill under budget at launch scale so that runway is preserved | Founder |

## Quality attribute scenarios

QA column = `ISO/IEC 25010 characteristic / sub-characteristic`.

| ID | QA (ISO 25010) | Source | Stimulus | Artifact | Environment | Response | Response measure | BG | Imp | Diff |
|----|----------------|--------|----------|----------|-------------|----------|------------------|----|-----|------|
| PQA-1 | Performance efficiency / time behaviour | Registered user | Loads the monthly dashboard, 500 concurrent users | Dashboard read path | Normal operation | Renders totals, category chart, recent activity, goal progress | Fully interactive < 1.5 s at p95 | BG-1 | H | M |
| PQA-2 | Performance efficiency / capacity | Registered user | Imports a 5 000-row CSV bank statement | Import Worker | Normal operation | Parses, maps, bulk-inserts; interactive traffic unaffected | Import completes < 30 s; dashboard p95 stays < 1.8 s | BG-1 | M | M |
| SQA-1 | Security / confidentiality | Authenticated user (attacker) | Requests another user's transactions by guessing IDs | API layer + data store | Normal operation | Request rejected; attempt logged and alerted | 0 successful cross-user reads; 100 % logged; alert < 1 min | BG-2 | H | H |
| AQA-1 | Reliability / availability | Cloud infrastructure | A single availability zone fails | Whole system | Production | Traffic shifts to the healthy AZ; data tier fails over | Uptime ≥ 99.5 %/month; recovery < 60 s; RPO < 5 min | BG-1 | H | H |
| MQA-1 | Maintainability / modifiability | Developer | Adds a new dashboard report type | Business logic + read model | During a sprint | Change isolated to the reporting module and its tests | ≤ 1 person-day; ≤ 3 modules touched; 0 regressions | BG-3 | M | M |
| UQA-1 | Interaction capability / operability | First-time user | Records their first transaction | Transaction form | Normal operation | User completes entry without consulting help | ≥ 85 % task-completion rate in a 10-person usability test | BG-1 | M | M |

### Scenario files and diagrams (register)

| Scenario | Six-part diagram (rendered + visually verified) |
|----------|--------------------------------------------------|
| [PQA-1](../drivers/quality-attributes/PQA-1.md) | [scenario-PQA-1.png](../drivers/quality-attributes/diagrams/scenario-PQA-1.png) · [source](../drivers/quality-attributes/diagrams/scenario-PQA-1.mmd) |
| [PQA-2](../drivers/quality-attributes/PQA-2.md) | [scenario-PQA-2.png](../drivers/quality-attributes/diagrams/scenario-PQA-2.png) · [source](../drivers/quality-attributes/diagrams/scenario-PQA-2.mmd) |
| [SQA-1](../drivers/quality-attributes/SQA-1.md) | [scenario-SQA-1.png](../drivers/quality-attributes/diagrams/scenario-SQA-1.png) · [source](../drivers/quality-attributes/diagrams/scenario-SQA-1.mmd) |
| [AQA-1](../drivers/quality-attributes/AQA-1.md) | [scenario-AQA-1.png](../drivers/quality-attributes/diagrams/scenario-AQA-1.png) · [source](../drivers/quality-attributes/diagrams/scenario-AQA-1.mmd) |
| [MQA-1](../drivers/quality-attributes/MQA-1.md) | [scenario-MQA-1.png](../drivers/quality-attributes/diagrams/scenario-MQA-1.png) · [source](../drivers/quality-attributes/diagrams/scenario-MQA-1.mmd) |
| [UQA-1](../drivers/quality-attributes/UQA-1.md) | [scenario-UQA-1.png](../drivers/quality-attributes/diagrams/scenario-UQA-1.png) · [source](../drivers/quality-attributes/diagrams/scenario-UQA-1.mmd) |

## Primary functional requirements — use cases with architectural impact

| ID | Use case name | Why it shapes the architecture |
|----|---------------|--------------------------------|
| UC-1 | Record a transaction | Dominates write load; on the p95 latency path; modifiability hot spot |
| UC-2 | View the monthly dashboard | Performance-critical read path; drives the read-model / caching decision |
| UC-3 | Import a bank statement | Bulk write path; first candidate for async processing |

## Constraints

| ID | Type (business / technical / regulatory) | Description |
|----|-----------------------------------------|-------------|
| CON-1 | technical | Runs in mobile browsers (iOS Safari, Android Chrome); no native app at launch |
| CON-2 | business | One founding engineer; MVP in 3 months |
| CON-3 | business | Launch on managed cloud low tiers; a paid upgrade path must exist |
| CON-4 | regulatory | All financial data encrypted in transit (TLS 1.2+) and at rest |
| CON-5 | technical | Primary datastore is PostgreSQL |

## Utility tree

A **table** (see [`drivers/quality-attributes/utility-tree.md`](../drivers/quality-attributes/utility-tree.md)
for the full version with per-leaf status). `(V, R)` = (business value, technical risk); `★` =
architecturally significant `(H, H)`.

| Quality attribute (ISO/IEC 25010) | Refinement (concern) | Leaf scenario | Priority (V, R) |
|-----------------------------------|----------------------|---------------|:---------------:|
| Security | Confidentiality | SQA-1 — cross-user access rejected + logged; 0 reads | (H, H) `★` |
| Reliability | Availability | AQA-1 — AZ failure recovers < 60 s; ≥ 99.5 %/mo | (H, H) `★` |
| Performance efficiency | Time behaviour | PQA-1 — dashboard < 1.5 s @ p95, 500 concurrent | (H, M) |
| Performance efficiency | Capacity | PQA-2 — 5 000-row import < 30 s, interactive unaffected | (M, M) |
| Maintainability | Modifiability | MQA-1 — add a report type in ≤ 1 person-day, 0 regressions | (M, M) |
| Interaction capability | Operability | UQA-1 — first transaction without help; ≥ 85 % completion | (M, M) |

## Architectural drivers (prioritised)

1. SQA-1 (H,H) — reject and log cross-user access; 0 successful reads
2. AQA-1 (H,H) — 99.5 % monthly uptime; AZ failure recovers < 60 s
3. PQA-1 (H,M) — dashboard interactive < 1.5 s @ p95 at 500 concurrent users
4. UC-1, UC-2 — write path and performance-critical read path
5. CON-4 (hard) — encryption in transit and at rest
6. CON-2 (hard) — one engineer, 3-month MVP

---

**Navigation**: [example root](../README.md) · [drivers](../drivers/README.md) · [QAW](../qaw/qaw-report.md) · [ADD](../add/personal-finance-tracker-Architecture.md)
