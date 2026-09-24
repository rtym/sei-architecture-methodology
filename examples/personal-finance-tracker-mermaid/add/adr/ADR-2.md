# ADR-2: Single tenant-guard choke point in the API service

- **Status**: accepted
- **Date**: 2026-09-06
- **Deciders**: Eng lead (architect), Founder (sponsor)
- **Drivers addressed**: SQA-1, CON-2, CON-4

## Context

Every request must be scoped to the authenticated user with zero successful cross-user reads and every attempt logged (SQA-1). A team of one (CON-2) cannot review per-endpoint authorisation checks reliably.

## Decision

We will route all data access through one API service whose tenant-guard middleware injects the user scope into every repository call and writes rejected attempts to an append-only audit log.

## Rationale

One auditable place to test and to show an auditor (SQA-1, BG-2); fewer moving parts for a small team (CON-2); the encryption mandate (CON-4) is applied once at the same boundary.

## Alternatives considered

| Alternative | Why not chosen |
|-------------|----------------|
| Per-endpoint authorisation checks | easy to miss one; no single place to audit |
| Row-level security in PostgreSQL only | kept as defence in depth, but an application-side guard is needed for logging and alerting |

## Consequences

- **Positive**: SQA-1 is verifiable by one middleware test suite; audit evidence for SOC 2.
- **Negative / accepted cost**: The import worker also touches data and must pass through the same guard — flagged as ATAM risk R-1; the audit store's tamper-evidence is still open (R-2).
- **Follow-up actions**: ADD iteration 1b: route the import worker through the tenant guard; choose an append-only audit store.

## Related

[`../personal-finance-tracker-Architecture.md`](../personal-finance-tracker-Architecture.md) §9 · [`../../docs/rationale.md`](../../docs/rationale.md) · [drivers](../../drivers/README.md)
