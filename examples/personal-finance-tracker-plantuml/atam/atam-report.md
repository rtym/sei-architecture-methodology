# ATAM Evaluation — Personal Finance Tracker

- **Date(s)**: 2026-09-05
- **Evaluation team**: external reviewer (lead), scenario scribe
- **Architect(s)**: Eng lead
- **Architecture evaluated**: `../add/personal-finance-tracker-Architecture.md` (after ADD iteration 1–2)
- **Status**: Phase 3 complete

> Condensed record exercising the full nine-step structure.

## Phase 0 — Partnership and preparation

- **Scope**: the launch architecture; focus on security, availability, performance.
- **Stakeholders for Phase 2**: founder, eng lead, security advisor, contractor QA.
- **Schedule**: one half-day Phase 1, one half-day Phase 2.

## Step 1 — Present the ATAM
Method, phases, and the seven output kinds explained.

## Step 2 — Present the business drivers

| ID | Business goal |
|----|---------------|
| BG-1 | 10 000 active users within 12 months |
| BG-2 | Pass SOC 2 Type II |
| BG-3 | Weekly report-type releases |
| BG-4 | Infra bill within budget at launch scale |

- **Primary functional requirements**: UC-1 record transaction, UC-2 dashboard, UC-3 CSV import.
- **Constraints**: CON-1..CON-5.
- **Most important quality attributes**: security, availability, performance, modifiability.

## Step 3 — Present the architecture

- **Technical constraints**: mobile web, one engineer, low-cost cloud, PostgreSQL, encryption.
- **External systems**: transactional email provider.
- **Overview**: SPA → single API (tenant guard + services + data access) → PostgreSQL, with a
  Redis read cache for dashboard aggregates and a Redis-Streams queue + worker for CSV import.
  Stateless API replicas across two AZs; managed primary/standby PostgreSQL.
- Diagrams: `../diagrams/container.png`, `../add/diagrams/deployment.png` (visually verified: yes)

## Step 4 — Identify architectural approaches

| ID | Approach / style / tactic | Where applied | Intended quality attribute |
|----|---------------------------|---------------|----------------------------|
| AA-1 | Modular monolith / layered | whole API service | modifiability |
| AA-2 | Single security choke point (tenant-guard middleware) | API request pipeline | security (confidentiality) |
| AA-3 | Cache-aside (Redis, 15-min TTL) | dashboard read path | performance |
| AA-4 | Stateless replicas + managed multi-AZ primary/standby | API + data tier | availability |
| AA-5 | Async queue + worker | CSV import path | performance (isolation of bulk work) |

## Step 5 — Quality attribute utility tree

A **table** (the same tree the drivers register carries —
[`../drivers/quality-attributes/utility-tree.md`](../drivers/quality-attributes/utility-tree.md)).
`(V, R)` = (business value, technical risk); `★` = architecturally significant `(H, H)`.

| Quality attribute (ISO/IEC 25010) | Refinement (concern) | Leaf scenario | Priority (V, R) | Status |
|-----------------------------------|----------------------|---------------|:---------------:|:------:|
| Security | Confidentiality | SQA-1 — cross-user access rejected and logged; 0 reads | (H, H) `★` | in design |
| Reliability | Availability | AQA-1 — survive an AZ loss, recover < 60 s; ≥ 99.5 %/mo | (H, H) `★` | open |
| Performance efficiency | Time behaviour | PQA-1 — dashboard < 1.5 s @ p95, 500 concurrent | (H, M) | open |
| Performance efficiency | Capacity | PQA-2 — 5 000-row import < 30 s, interactive unaffected | (M, M) | open |
| Maintainability | Modifiability | MQA-1 — add a report type in ≤ 1 person-day, 0 regressions | (M, M) | open |

_Reading the tree_: the `★` `(H,H)` leaves — **SQA-1, AQA-1** — plus the `(H,M)` leaf **PQA-1**
are what Step 6 analyses.

## Step 6 — Analyse architectural approaches (Phase 1 scenarios)

### SQA-1 — Cross-user access attempt rejected and logged  (V=H, R=H)

Scenario analysis in the ATAM template (Fig. 21.1 shape).

- **Attribute(s)**: Security / confidentiality + accountability
- **Environment · Stimulus · Response**: normal operation · an authenticated user requests
  another user's transactions by guessing record IDs · request rejected, attempt written to an
  append-only audit log and alerted (0 cross-user reads; 100 % logged; alert < 1 min)
- **Approaches invoked**: AA-2 (tenant-guard choke point), AA-1 (layering keeps Data Access behind one module)

| Architectural decision | Sensitivity | Trade-off | Risk | Nonrisk |
|------------------------|-------------|----------|------|----------|
| Single tenant-guard middleware (vs. per-endpoint checks) | S-1 | | | |
| Import worker builds its own Data Access calls, bypassing the guard | | | R-1 | |
| Audit-log store — tamper-evidence not yet decided | | | R-2 | |
| All *interactive* traffic passes exactly one guard | | | | N-1 |

**Reasoning.** S-1: placing the `user_id` scoping in one middleware makes SQA-1 auditable in a
single place; per-query scoping is functionally equivalent but easy to miss on a new endpoint.
R-1: the import worker shares the Data Access module but not the guard, so a bug there could
cross tenants — endangers SQA-1 / BG-2. R-2: SOC 2 auditors expect an append-only,
tamper-evident audit trail. N-1 holds only while no service reaches Data Access except via the
guard (assumption stated).

### AQA-1 — Survive a single-AZ failure, recover < 60 s  (V=H, R=H)

- **Attribute(s)**: Reliability / availability + recoverability
- **Environment · Stimulus · Response**: production · a single availability zone fails · traffic
  shifts to the healthy AZ and the data tier fails over automatically (≥ 99.5 %/mo; recovery
  < 60 s; RPO < 5 min)
- **Approaches invoked**: AA-4 (stateless replicas + managed primary/standby failover), AA-3 (the cache is not a system of record)

| Architectural decision | Sensitivity | Trade-off | Risk | Nonrisk |
|------------------------|-------------|----------|------|----------|
| Managed PostgreSQL primary/standby, automated failover (vendor: 35–70 s, unmeasured) | | | R-3 | |
| No runbook / automation for a bad-deploy rollback | | | R-4 | |
| Redis read cache holds strictly derived data | | | | N-2 |
| Redis aggregate TTL = 15 min | S-2 | T-1 | | |

**Reasoning.** R-3: the vendor's upper bound (70 s) exceeds the 60 s target and it has not been
game-day-tested — endangers AQA-1. R-4: recovery time for a bad deploy depends on manual steps
by a one-person team. N-2 holds while the cache stays strictly derived (assumption). S-2 / T-1:
a higher TTL improves dashboard latency (PQA-1) but worsens data freshness — a performance ↔
correctness tradeoff.

## Step 7 — Brainstorm and prioritise scenarios (Phase 2)

**Vote budget** = ceil(0.30 × 6) = **2** per stakeholder.

| ID | Scenario | Type (use-case / growth / exploratory) | Votes |
|----|----------|----------------------------------------|-------|
| P-1 | 10× user growth in a month | growth | 3 |
| P-2 | A dependency (email provider) is down for an hour | exploratory | 2 |
| P-3 | New compliance regime adds data-residency rules | exploratory | 2 |
| P-4 | Analyst adds a report type end-to-end | use-case | 1 |

Ranked: P-1 (3) > P-2 (2) = P-3 (2) > P-4 (1). Agreement with utility tree: growth/availability
themes align; data-residency (P-3) is new and not in the tree.

## Step 8 — Analyse architectural approaches (Phase 2 scenarios)

### P-1 — 10× user growth in a month (growth)
- **Approaches invoked**: AA-4 (stateless replicas scale horizontally), AA-3 (cache absorbs read load)

| Finding | Type | Element / decision | Affected attribute(s) | Note |
|---------|------|--------------------|-----------------------|------|
| R-5 | Risk | Single-writer PostgreSQL primary; no read-replica plan | Scalability / performance | write and heavy-read load both land on the primary |
| N-3 | Non-risk | API tier scales out without code change | Scalability | holds while sessions stay externalised (they do) |

### P-3 — Data-residency rules added (exploratory)

| Finding | Type | Element / decision | Affected attribute(s) | Note |
|---------|------|--------------------|-----------------------|------|
| R-6 | Risk | Single-region deployment, no data-partitioning-by-region seam | Flexibility / adaptability | a residency requirement would force a larger refactor |

## Step 9 — Results

### Architectural approaches
AA-1 modular monolith · AA-2 security choke point · AA-3 cache-aside · AA-4 stateless + managed HA · AA-5 async import.

### Risks
| ID | Risk | Affected attribute | Related driver |
|----|------|--------------------|----------------|
| R-1 | Import worker bypasses the tenant guard | Security | SQA-1, BG-2 |
| R-2 | No audit-log tamper-evidence decision | Security | BG-2 |
| R-3 | DB failover time unmeasured vs target | Availability | AQA-1 |
| R-4 | No rollback runbook/automation | Availability | AQA-1 |
| R-5 | Single-writer DB, no read-replica plan | Scalability | BG-1 |
| R-6 | No region-partitioning seam | Adaptability | BG-2 |

### Non-risks
| ID | Non-risk | Assumption under which it holds |
|----|----------|--------------------------------|
| N-1 | One security choke point for interactive traffic | no code path reaches Data Access except via the guard |
| N-2 | Cache loss = latency only | Redis holds strictly derived data |
| N-3 | API tier scales out freely | sessions stay externalised |

### Sensitivity points
| ID | Element property | Attribute affected | Direction |
|----|------------------|--------------------|-----------|
| S-1 | Tenant-scoping check placement | Security | one place → far fewer miss-a-check defects |
| S-2 | Redis aggregate TTL | Performance / freshness | TTL up → latency down, staleness up |

### Tradeoff points
| ID | Element property | Attribute A ↑ | Attribute B ↓ |
|----|------------------|---------------|---------------|
| T-1 | Redis aggregate TTL | Performance (dashboard latency) | Correctness (dashboard freshness) |

### Risk themes
| Theme | Risks | Business driver(s) endangered | Recommendation |
|-------|-------|------------------------------|----------------|
| RT-1 Incomplete security-control coverage | R-1, R-2 | BG-2 | ADD iteration 1b: route the import worker through the tenant guard; choose an append-only audit store |
| RT-2 Unproven recovery | R-3, R-4 | BG-1, BG-4 | Game-day test of DB failover; write and automate a rollback runbook before launch |
| RT-3 Growth head-room on the data tier | R-5, R-6 | BG-1, BG-2 | ADD iteration 3: add a read-replica + repository read/write split; introduce a region seam in the data model |

### CBAM — ranked remediation backlog

Turn the risk themes into a prioritised backlog by rough ROI (utility gained ÷ cost).

| # | Action (risk theme) | Utility gained | Cost | ROI |
|---|--------------------|----------------|------|-----|
| 1 | Route the import worker through the tenant guard + choose an append-only audit store (RT-1) | High — closes the SQA-1 / BG-2 gap; unblocks SOC 2 | ~1 ADD iteration (1b) | **highest** |
| 2 | Game-day the managed-DB failover; write + automate a rollback runbook (RT-2) | High — proves AQA-1; removes a launch blocker | ~2 person-days | high |
| 3 | Read-replica + repository read/write split; region seam in the data model (RT-3) | Medium — head-room for BG-1 growth and future data-residency | ~1 ADD iteration (3) | medium — defer until growth signal |

### Recommendations / next steps
- Run `/add` iteration 1b for RT-1 and iteration 3 for RT-3.
- Schedule a DB failover game-day; add a rollback runbook (RT-2).
- Re-run this ATAM after the risk themes are addressed. A full ATAM is not needed each time — a **Lightweight Architecture Evaluation** (steps 3–8, internal team, ~half a day, no report) each ADD round or before a release keeps the registers current.

---

**Navigation**: [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md) · [Views & Beyond docs](../docs/README.md)
