# CON-2: One engineer, 3-month MVP

- **Type**: business
- **Constraint**: One founding engineer builds the MVP; target delivery in 3 months.
- **Source**: Founder
- **Nature**: hard
- **Priority**: high
- **Status**: open

## Rationale

Funding reality; sets the complexity budget for the whole architecture and follows from
[BG-4](../business-goals/BG-4.md) (preserve runway).

## Impact on the architecture

Rules out microservices and self-managed HA; favours a modular monolith with managed data
services.

## Conflicts

[BG-3](../business-goals/BG-3.md) (weekly releases) — a one-person team limits throughput; that
tension is itself a driver for [MQA-1](../quality-attributes/MQA-1.md).

## Traces up to

- Business goals: [BG-4](../business-goals/BG-4.md)

---

**Navigation**: [constraints index](README.md) · [drivers README](../README.md)
