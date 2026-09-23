# AQA-1: Survive a single-AZ failure

- **Status**: at risk (ATAM R-3, R-4)
- **Source**: authored here (kept in sync with [`../../quality-attributes/scenarios.md`](../../quality-attributes/scenarios.md))

Documented as a **six-part quality attribute scenario** and supported by its own **horizontal
six-part scenario diagram**.

| Part | Value |
|------|-------|
| **ID** | AQA-1 |
| **ISO/IEC 25010 characteristic** | Reliability |
| **Sub-characteristic** | availability |
| **Source of stimulus** | Cloud infrastructure |
| **Stimulus** | A single availability zone fails |
| **Artifact** | Whole system |
| **Environment** | Production |
| **Response** | Traffic shifts to the healthy AZ; the data tier fails over automatically |
| **Response measure** | Uptime ≥ 99.5 %/month; recovery < 60 s; RPO < 5 min |
| **Business goals supported** | BG-1, BG-4 |
| **Priority** | Importance = H · Difficulty = H |
| **Candidate tactics** | **Availability** — *detect faults*: monitor, health check (ping/echo); *recover, preparation & repair*: active redundancy (stateless API replicas across two AZs), passive redundancy (managed DB primary/standby), retry, rollback; *recover, reintroduction*: state resynchronization |
| **Type** | concrete |

## Six-part scenario diagram

Drawn with the house PlantUML pattern (this is the PlantUML tree): five boxes left-to-right — source of stimulus → stimulus → artifact → response → response measure — with the environment attached to the artifact.

![AQA-1 six-part scenario](diagrams/scenario-AQA-1.png)

Source: [`diagrams/scenario-AQA-1.puml`](diagrams/scenario-AQA-1.puml) · rendered + visually verified.

## Notes / assumptions

See [`../README.md`](../README.md) for traceability and the utility tree.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) · [utility tree](utility-tree.md)
