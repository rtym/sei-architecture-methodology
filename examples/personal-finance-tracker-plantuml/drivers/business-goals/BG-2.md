# BG-2: Sell to employers via SOC 2

- **Statement**: The company needs to pass a SOC 2 Type II audit so that it can sell the app to employers as a staff benefit.
- **Primary stakeholder**: Founder / Compliance
- **SEI business-goal category**: responsibility to society & law
- **Measure of success**: Clean SOC 2 Type II report before the enterprise sales push
- **Priority**: high
- **Status**: open

## Business-goal scenario (7 parts)

| Part | Value |
|------|-------|
| Goal-source | Founder / Head of Compliance |
| Goal-subject | the founding team and the enterprise sales function |
| Goal-object | the Personal Finance Tracker product and the company's audit posture |
| Environment | early-stage B2B2C SaaS entering enterprise sales; SOC 2 is table stakes for an employer-benefit deal; ~12-month runway |
| Goal | pass a SOC 2 Type II audit (Security + Confidentiality trust-services criteria) |
| Goal-measure | a clean (no-exception) SOC 2 Type II report covering a ≥ 6-month observation window, delivered before the first enterprise contract is signed |
| Pedigree & value | set by the founder; high confidence it is required; low volatility; value **high** — a blocked audit blocks the entire employer channel |

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
