# BG-2: Sell to employers via SOC 2

- **Statement**: The company needs to pass a SOC 2 Type II audit so that it can sell the app to employers as a staff benefit.
- **Primary stakeholder**: Founder / Compliance
- **SEI business-goal category**: responsibility to society & law
- **Measure of success**: Clean SOC 2 Type II report before the enterprise sales push
- **Priority**: high
- **Status**: open

## Context

Early-stage SaaS; this goal is one of the four the architecture must serve. See
[`../README.md`](../README.md) for the full driver set and traceability.

## Supported by

- Use cases: —
- Quality attribute scenarios: [SQA-1](../quality-attributes/SQA-1.md)
- Constraints: [CON-4](../constraints/CON-4.md)

## Notes

Audit scope drives the security scenario (SQA-1 — no cross-user data access, every attempt
logged) and the encryption constraint (CON-4). The architecture keeps the external surface small
to keep the SOC 2 boundary auditable.

---

**Navigation**: [business-goals index](README.md) · [drivers README](../README.md)
