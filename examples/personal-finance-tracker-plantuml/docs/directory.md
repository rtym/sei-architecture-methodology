# Directory — Personal Finance Tracker

## Index — where elements are defined

| Element | Defined in | Also appears in |
|---------|-----------|-----------------|
| `security` module / Tenant Guard | `view-module-decomposition.md` §2 | `view-cnc-runtime.md`, [`rationale.md`](rationale.md) ADR-2 |
| `reporting` module / Dashboard Service | `view-module-decomposition.md` §2 | `view-cnc-runtime.md`, [`rationale.md`](rationale.md) ADR-1 |
| Read Cache | `view-cnc-runtime.md` §2 | `view-allocation-deployment.md`, [`rationale.md`](rationale.md) ADR-1 |
| Import Queue / Import Worker | `view-cnc-runtime.md` §2 | `view-allocation-deployment.md`, `mapping-between-views.md` |
| Primary Database | `view-cnc-runtime.md` §2 | `view-allocation-deployment.md`, ADD `Architecture.md` §7 |

## Glossary

| Term | Meaning |
|------|---------|
| Tenant guard | Middleware that forces `user_id` scoping onto every query; the `SQA-1` control |
| Cache-aside | Read pattern: check cache; on miss, load from source and populate the cache |
| Derived data | Data that can be recomputed from the system of record; safe to lose |
| System of record | The authoritative store for a piece of data (here: PostgreSQL) |
| Six-part scenario | The SEI quality attribute scenario form: source, stimulus, artifact, environment, response, response measure |

## Acronyms

| Acronym | Expansion |
|---------|-----------|
| ADD | Attribute-Driven Design |
| ATAM | Architecture Tradeoff Analysis Method |
| AZ | Availability Zone |
| C&C | Component-and-Connector |
| PWA | Progressive Web App |
| QAW | Quality Attribute Workshop |
| RPO / RTO | Recovery Point / Time Objective |
| TTL | Time To Live |
| V&B | Views and Beyond |

## Driver ID prefixes used here

`BG-` business goal · `UC-` use case · `CON-` constraint · `AQA-` availability · `SQA-` security
· `PQA-` performance · `MQA-` modifiability · `UQA-` usability · `RQA-` reliability(other).

---

**Navigation**: [docs README](README.md) · [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md)
