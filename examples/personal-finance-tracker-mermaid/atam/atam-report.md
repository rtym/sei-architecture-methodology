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
- Diagrams: `../diagrams/container.png`, `../diagrams/personal-finance-tracker-Architecture-05.png` (visually verified: yes)

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

### SQA-1 — Cross-user access attempt rejected and logged (H, H)
- **Attribute / refinement**: Security / confidentiality + accountability
- **Approaches invoked**: AA-2 (tenant-guard choke point), AA-1 (layering keeps data access behind one module)
- **Analysis questions & answers**:
  - Q: Can any code path reach the database without passing the tenant guard? A: Only the import
    worker, which shares the Data Access module but not the guard — flagged.
  - Q: Is the audit log tamper-evident? A: Not yet; append-only store not decided — flagged.

| Finding | Type | Element / decision | Affected attribute(s) | Note |
|---------|------|--------------------|-----------------------|------|
| R-1 | Risk | Import worker bypasses the tenant-guard middleware | Security | worker builds its own DB calls via Data Access; a bug could cross tenants |
| R-2 | Risk | Audit log has no tamper-evidence decision | Security / accountability | SOC 2 (BG-2) auditors expect this |
| N-1 | Non-risk | All interactive traffic passes one guard | Security | holds while no service calls Data Access directly except via the guard |
| S-1 | Sensitivity point | Placement of the tenant-scoping check (one middleware vs per-query) | Security | one place → auditable; per-query → easy to miss one |

### AQA-1 — Survive a single-AZ failure, recover < 60 s (H, H)
- **Attribute / refinement**: Reliability / availability + recoverability
- **Approaches invoked**: AA-4 (stateless replicas + managed failover), AA-3 (cache is not a system of record)
- **Analysis questions & answers**:
  - Q: What is the measured failover time of the managed PostgreSQL tier? A: Vendor states 35–70 s; not yet tested — flagged.
  - Q: Does a cache-tier loss affect correctness? A: No; only latency (cache-aside recomputes).

| Finding | Type | Element / decision | Affected attribute(s) | Note |
|---------|------|--------------------|-----------------------|------|
| R-3 | Risk | Managed DB failover time not measured against the < 60 s target | Availability | upper bound of vendor range exceeds the target |
| R-4 | Risk | No runbook / automation for a bad-deploy rollback | Availability / recoverability | recovery time depends on manual steps by a one-person team |
| N-2 | Non-risk | Redis read-cache loss degrades latency only | Availability | holds while the cache stays strictly derived data |
| S-2 | Sensitivity point | Redis TTL (15 min) | Performance / correctness | higher TTL → better latency, staler aggregates |
| T-1 | Tradeoff point | Redis TTL | Performance ↑ vs. dashboard data freshness ↓ | see S-2 |

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

### Recommendations / next steps
- Run `/add` iteration 1b for RT-1 and iteration 3 for RT-3.
- Schedule a DB failover game-day; add a rollback runbook (RT-2).
- Re-run this ATAM after the risk themes are addressed.

---

**Navigation**: [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md) · [Views & Beyond docs](../docs/README.md)
