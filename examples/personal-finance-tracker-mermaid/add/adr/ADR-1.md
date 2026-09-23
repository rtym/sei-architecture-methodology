# ADR-1: Cache-aside read model for the dashboard

- **Status**: accepted
- **Date**: 2026-09-06
- **Deciders**: Eng lead (architect), Founder (sponsor)
- **Drivers addressed**: PQA-1, MQA-1, UC-2, CON-3

## Context

The dashboard (UC-2) must be interactive in < 1.5 s at p95 with 500 concurrent users (PQA-1). Aggregating transactions per request in PostgreSQL alone does not meet that budget at the low-cost tier the constraints allow (CON-3), and new report types must stay cheap to add (MQA-1).

## Decision

We will serve dashboard aggregates from a Redis read cache filled cache-aside on a miss, with a 15-minute TTL, keyed per user and month.

## Rationale

Cache-aside keeps the database the only source of truth and needs no invalidation logic beyond the TTL; the TTL bounds staleness, and the report-type registry computes new aggregates without schema changes (MQA-1). Redis is a managed, low-cost component (CON-3).

## Alternatives considered

| Alternative | Why not chosen |
|-------------|----------------|
| Materialised views in PostgreSQL | slower to iterate on new report types (MQA-1); refresh cost grows with users |
| CDN / HTTP caching | dashboard data is per user and authenticated — no shared cache key |

## Consequences

- **Positive**: Dashboard p95 met at target load on a single DB writer; report types iterate weekly.
- **Negative / accepted cost**: Up to 15 minutes of staleness after a write; a second infrastructure component to run and monitor (ATAM SP-2 / TP-1).
- **Follow-up actions**: Add cache-hit-ratio and staleness metrics; decide the invalidation policy on transaction writes in a later iteration.

## Related

[`../personal-finance-tracker-Architecture.md`](../personal-finance-tracker-Architecture.md) §9 · [`../../docs/rationale.md`](../../docs/rationale.md) · [drivers](../../drivers/README.md)
