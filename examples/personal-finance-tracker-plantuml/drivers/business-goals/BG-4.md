# BG-4: Preserve runway at launch scale

- **Statement**: Operations needs the monthly infrastructure bill to stay under budget at launch scale so that runway is preserved.
- **Primary stakeholder**: ST-1 — Founder
- **SEI business-goal category**: financial
- **Measure of success**: Infra spend ≤ budget at 10 000 users
- **Priority**: high
- **Status**: open

## Context

Early-stage SaaS; this goal is one of the four the architecture must serve. See
[`../README.md`](../README.md) for the full driver set and traceability.

## Supported by

- Use cases: —
- Quality attribute scenarios: [AQA-1](../quality-attributes/AQA-1.md)
- Constraints: [CON-3](../constraints/CON-3.md), [CON-5](../constraints/CON-5.md)

## Notes

Budget rules out a self-managed HA setup; see [CON-3](../constraints/CON-3.md) (low-cost managed
tiers). AQA-1's recovery target must be met with managed primary/standby PostgreSQL rather than a
bespoke cluster the one-person team would have to operate.

---

**Navigation**: [business-goals index](README.md) · [drivers README](../README.md)
