# CON-4: Encryption in transit and at rest

- **Type**: regulatory
- **Constraint**: All financial data encrypted in transit (TLS 1.2+) and at rest.
- **Source**: SOC 2 scope
- **Nature**: hard
- **Priority**: high
- **Status**: open

## Rationale

Required by the SOC 2 audit scope ([BG-2](../business-goals/BG-2.md)); non-negotiable.

## Impact on the architecture

Adds a tenant guard plus encrypted stores; encryption in transit and at rest is part of every
data-path decision and directly supports [SQA-1](../quality-attributes/SQA-1.md).

## Conflicts

None.

## Traces up to

- Business goals: [BG-2](../business-goals/BG-2.md)

---

**Navigation**: [constraints index](README.md) · [drivers README](../README.md)
