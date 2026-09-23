# Rationale — Personal Finance Tracker

Cross-cutting architecture rationale and the ADR log. Per-view rationale lives in each view packet.
The three ADRs were taken during ADD and are canonical there — [`ADR-1`](../add/adr/ADR-1.md),
[`ADR-2`](../add/adr/ADR-2.md), [`ADR-3`](../add/adr/ADR-3.md); the sections below summarise them.

## ADR-1: Cache-aside read model for the dashboard

- **Status**: accepted · 2026-09-06
- **Drivers addressed**: `PQA-1`, `AQA-1`, `MQA-1`

**Context.** The dashboard (`UC-2`) must be interactive in < 1.5 s at p95 with 500 concurrent
users. Computing every load from the transaction store does not meet the budget.

**Decision.** We will precompute per-user, per-month aggregates in a Redis cache using the
cache-aside pattern with a 15-minute TTL; a transaction write invalidates the affected key.

**Rationale.** Meets `PQA-1`; keeps the cache strictly derived so its loss degrades latency but
not correctness (`AQA-1`); aggregate logic stays in the `reporting` module, so new report types
(`MQA-1`) do not require schema changes.

**Alternatives considered.** Materialised views (slower iteration for `MQA-1`); CDN edge caching
(per-user private data — unsafe); no cache (fails `PQA-1`).

**Consequences.** Dashboard data can be up to 15 minutes stale on the read path (tradeoff point
`T-1` in the ATAM). Cache warm-up cost on cold start.

## ADR-2: Single tenant-guard choke point

- **Status**: accepted · 2026-09-06
- **Drivers addressed**: `SQA-1`, `CON-4`, `BG-2`

**Context.** `SQA-1` requires that no user can read another user's data, with every attempt
logged, and `BG-2` requires passing a SOC 2 audit.

**Decision.** All interactive requests pass through one `security`-module tenant guard that
injects `user_id` scoping into every query via the `persistence` module; denied access is written
to an append-only audit log.

**Rationale.** One auditable place to enforce and demonstrate isolation; per-endpoint checks were
rejected as too easy to omit.

**Alternatives considered.** PostgreSQL row-level security (viable later; team unfamiliarity now);
per-endpoint authorization (miss-a-check risk).

**Consequences.** The Import Worker currently bypasses the guard (ATAM risk `R-1`); a follow-up
routes it through the same Data Access scoping. Audit-log tamper-evidence still to be decided
(`R-2`).

## ADR-3: Stateless API replicas + managed multi-AZ database

- **Status**: accepted · 2026-09-06
- **Drivers addressed**: `AQA-1`, `CON-3`, `CON-5`, `BG-4`

**Context.** `AQA-1` requires surviving a single-AZ failure with recovery < 60 s at ≥ 99.5 %/mo,
on low-cost managed tiers (`CON-3`) using PostgreSQL (`CON-5`) and within budget (`BG-4`).

**Decision.** Run the API as stateless replicas pinned across two AZs behind the platform load
balancer; use a managed PostgreSQL primary/standby with automated failover; Redis primary/replica.

**Rationale.** Cheapest topology meeting the recovery target without a self-managed HA setup the
one-person team cannot operate (`CON-2`).

**Alternatives considered.** Self-managed HA (operational load — `CON-2`); single instance (fails
`AQA-1`); multi-region (cost — `BG-4`, and premature).

**Consequences.** Measured failover time not yet verified against 60 s (`R-3`); no rollback
runbook yet (`R-4`); single-region only, no data-residency seam (`R-6`).

---

**Navigation**: [docs README](README.md) · [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md)
