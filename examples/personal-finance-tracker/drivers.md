# Architectural Drivers: Personal Finance Tracker

- **Date**: 2026-09-06
- **Owner**: Roman Tymoshuk
- **Status**: reviewed
- **Related artifacts**: `scenarios.md`, `qaw-report.md`
- **QA model**: ISO/IEC 25010:2023
- **QA ID legend**: AQA availability · SQA security · PQA performance · MQA modifiability ·
  UQA usability · RQA reliability(other)

> Worked example. Shows the four SEI driver kinds with the attribute-prefixed ID scheme and a
> full traceability matrix.

---

## 1. Business goals

| ID | Goal | Category | Stakeholder | Status |
|----|------|----------|-------------|--------|
| BG-1 | The founder needs 10 000 active users within 12 months so that the product reaches seed-round metrics | growth / market position | Founder | open |
| BG-2 | The company needs to pass a SOC 2 Type II audit so that it can sell to employers offering the app as a benefit | responsibility to society & law | Founder / Compliance | open |
| BG-3 | Engineering needs to ship new report types weekly so that the product keeps pace with competitor feature velocity | quality of process | Eng lead | open |
| BG-4 | Operations needs the monthly infra bill to stay under budget at launch scale so that runway is preserved | financial | Founder | open |

## 2. Primary functional requirements — use cases

### UC-1 — Record a transaction
- **Primary actor**: Registered user
- **Supporting actors**: —
- **Trigger**: User submits the "add transaction" form
- **Preconditions**: User is authenticated
- **Main success scenario**: 1. User enters amount, date, category, note. 2. System validates. 3. System persists the transaction. 4. System updates the dashboard aggregates. 5. System confirms.
- **Key alternate / exception flows**: 2a. Validation fails → field-level errors, no write. 3a. Store unavailable → queued write, user told "saved, syncing".
- **Architectural significance**: dominates write load; on the p95 latency path (PQA-1); touched by every modifiability change (MQA-1).
- **Related drivers**: BG-1, PQA-1, MQA-1

### UC-2 — View the monthly dashboard
- **Primary actor**: Registered user
- **Supporting actors**: —
- **Trigger**: User opens the app or navigates to "Dashboard"
- **Preconditions**: User is authenticated; has ≥ 0 transactions
- **Main success scenario**: 1. System loads the user's month-to-date aggregates. 2. System renders totals, a category breakdown chart, recent transactions, and savings-goal progress.
- **Key alternate / exception flows**: 1a. Aggregates cache miss → recompute from the transaction store.
- **Architectural significance**: the performance-critical read path (PQA-1); shapes the read-model / caching decision.
- **Related drivers**: BG-1, PQA-1, UQA-1

### UC-3 — Import a bank statement (CSV)
- **Primary actor**: Registered user
- **Supporting actors**: —
- **Trigger**: User uploads a CSV file
- **Preconditions**: User is authenticated
- **Main success scenario**: 1. User uploads CSV. 2. System parses and maps rows to transactions. 3. System asks the user to confirm category mapping. 4. System bulk-inserts. 5. System updates aggregates.
- **Key alternate / exception flows**: 2a. Unrecognised format → guided column mapping. 4a. Partial failure → per-row result report.
- **Architectural significance**: bulk write path; `<<include>>`s categorisation; first candidate for async processing.
- **Related drivers**: BG-1, PQA-2

### Use case diagram

`diagrams/usecases-core.mmd` → `diagrams/usecases-core.png` (visually verified: yes)

## 3. Constraints

| ID | Type | Constraint | Source | Hard / negotiable | Conflicts with |
|----|------|-----------|--------|-------------------|----------------|
| CON-1 | technical | Must run in the browser on iOS Safari and Android Chrome; no native app at launch | Product | hard | — |
| CON-2 | business | One founding engineer; MVP in 3 months | Founder | hard | BG-3 (velocity risk) |
| CON-3 | business | Launch on managed cloud free/low tiers; a paid upgrade path must exist | Founder | negotiable | — |
| CON-4 | regulatory | All financial data encrypted in transit (TLS 1.2+) and at rest | SOC 2 scope | hard | — |
| CON-5 | technical | Primary datastore must be PostgreSQL (team skill, managed availability) | Eng lead | negotiable | — |

## 4. Quality attributes

Detail in `scenarios.md`. Summary:

| ID | ISO/IEC 25010 characteristic / sub | One-line scenario | (Imp, Diff) |
|----|-----------------------------------|-------------------|-------------|
| PQA-1 | Performance efficiency / time behaviour | Dashboard interactive < 1.5 s @ p95 under 500 concurrent users | (H, M) |
| PQA-2 | Performance efficiency / capacity | CSV import of 5 000 rows completes < 30 s, dashboard stays responsive | (M, M) |
| SQA-1 | Security / confidentiality | Cross-user data access attempt is rejected and logged; 0 successful reads | (H, H) |
| AQA-1 | Reliability / availability | ≥ 99.5 % monthly uptime; single-AZ failure recovers < 60 s | (H, H) |
| MQA-1 | Maintainability / modifiability | Add a new report type in ≤ 1 person-day with 0 regressions | (M, M) |
| UQA-1 | Interaction capability / operability | First-time user records a transaction without help docs; ≥ 85 % task completion | (M, M) |

## 5. Traceability matrix

| Driver | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|-------------|---------------------------|--------------|--------|
| UC-1 | BG-1 | PQA-1, MQA-1, CON-4 | ADD iter 1 | in design |
| UC-2 | BG-1 | PQA-1, UQA-1 | ADD iter 2 | open |
| UC-3 | BG-1 | PQA-2 | ADD iter 3 | open |
| PQA-1 | BG-1 | UC-1, UC-2 | ADD iter 2 | open |
| PQA-2 | BG-1 | UC-3 | ADD iter 3 | open |
| SQA-1 | BG-2 | CON-4 | ADD iter 1 | in design |
| AQA-1 | BG-1, BG-4 | CON-3, CON-5 | ADD iter 1 | open |
| MQA-1 | BG-3 | UC-1 | ADD iter 1 | open |
| UQA-1 | BG-1 | UC-2 | ADD iter 2 | open |
| CON-1 | BG-1 | UC-1, UC-2 | ADD iter 1 | open |
| CON-2 | BG-4 | — | ADD iter 1 | open |
| CON-3 | BG-4 | AQA-1 | ADD iter 1 | open |
| CON-4 | BG-2 | SQA-1 | ADD iter 1 | in design |
| CON-5 | BG-1 | AQA-1 | ADD iter 1 | open |

`Status` ∈ open / in design / partially / addressed / retired.
**Coverage check**: every BG (BG-1…BG-4) has ≥ 1 UC or QA scenario; every UC / QA scenario / CON
traces to ≥ 1 BG. Gaps found: none.

## 6. Prioritised driver list (input to ADD / ATAM)

1. SQA-1 (H,H) — reject and log cross-user access; 0 successful reads
2. AQA-1 (H,H) — 99.5 % monthly uptime; AZ failure recovers < 60 s
3. PQA-1 (H,M) — dashboard interactive < 1.5 s @ p95 at 500 concurrent users
4. UC-1 — record a transaction (write-load + latency + modifiability hot spot)
5. UC-2 — monthly dashboard (performance-critical read path)
6. CON-4 (hard) — encryption in transit and at rest
7. CON-2 (hard) — one engineer, 3-month MVP

## Change log

| Date | Change |
|------|--------|
| 2026-09-06 | initial register; reviewed with founder + eng lead |
