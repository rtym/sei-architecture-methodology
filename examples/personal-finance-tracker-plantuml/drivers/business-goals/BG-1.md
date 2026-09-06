# BG-1: Reach seed-round user metrics

- **Statement**: The founder needs 10 000 active users within 12 months so that the product reaches seed-round metrics.
- **Primary stakeholder**: Founder
- **SEI business-goal category**: growth & market share
- **Measure of success**: 10 000 monthly-active users by month 12
- **Priority**: high
- **Status**: open

## Context

Early-stage SaaS; this goal is one of the four the architecture must serve. See
[`../README.md`](../README.md) for the full driver set and traceability.

## Supported by

- Use cases: [UC-1](../use-cases/UC-1.md), [UC-2](../use-cases/UC-2.md), [UC-3](../use-cases/UC-3.md)
- Quality attribute scenarios: [PQA-1](../quality-attributes/PQA-1.md), [PQA-2](../quality-attributes/PQA-2.md), [AQA-1](../quality-attributes/AQA-1.md), [UQA-1](../quality-attributes/UQA-1.md)

## Notes

Growth pressure drives the performance and availability scenarios: the dashboard must stay fast
under load (PQA-1) and the system must survive an availability-zone loss (AQA-1) without eroding
trust while the user base scales toward the seed-round target.

---

**Navigation**: [business-goals index](README.md) · [drivers README](../README.md)
