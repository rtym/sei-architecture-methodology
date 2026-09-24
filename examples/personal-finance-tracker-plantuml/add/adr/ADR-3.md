# ADR-3: Stateless API replicas on a managed multi-AZ PostgreSQL

- **Status**: accepted
- **Date**: 2026-09-06
- **Deciders**: Eng lead (architect), Founder (sponsor)
- **Drivers addressed**: AQA-1, CON-3, CON-5, UC-1

## Context

The system must survive a single-availability-zone failure and recover in < 60 s with ≥ 99.5 % monthly availability (AQA-1), on a low-cost hosting tier (CON-3) and on PostgreSQL (CON-5).

## Decision

We will run two or more stateless API replicas across two availability zones behind a load balancer, with sessions externalised, on a managed PostgreSQL primary/standby with automated failover.

## Rationale

Managed failover meets the AQA-1 recovery target without operating HA ourselves (CON-2); the low-cost tier still offers multi-AZ (CON-3); statelessness lets replicas restart freely (UC-1 writes are idempotent by transaction id).

## Alternatives considered

| Alternative | Why not chosen |
|-------------|----------------|
| Self-managed HA PostgreSQL | operations cost a one-person team cannot carry (CON-2) |
| Single database instance | fails AQA-1 outright |

## Consequences

- **Positive**: AZ loss is survivable; rolling deploys without downtime.
- **Negative / accepted cost**: Failover time is a provider figure, not yet measured (ATAM R-3); rollback is manual (R-4).
- **Follow-up actions**: Game-day the failover; write and automate a rollback runbook before launch (RT-2).

## Related

[`../personal-finance-tracker-Architecture.md`](../personal-finance-tracker-Architecture.md) §9 · [`../../docs/rationale.md`](../../docs/rationale.md) · [drivers](../../drivers/README.md)
