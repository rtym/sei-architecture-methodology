# AQA-1: Survive a single-AZ failure

- **Status**: open
- **Source**: authored here (kept in sync with `../../scenarios.md`)

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
| **Type** | concrete |

## Six-part scenario diagram

```mermaid
flowchart LR
  %% Quality attribute scenario — AQA-1 — Reliability / availability  (horizontal)
  src["<b>Source of stimulus</b><br/>Cloud infrastructure"]
  stim["<b>Stimulus</b><br/>A single availability zone fails"]
  subgraph env["Environment: Production"]
    art["<b>Artifact</b><br/>Whole system"]
  end
  resp["<b>Response</b><br/>Traffic shifts to the healthy AZ; the data tier fails over automatically"]
  meas["<b>Response measure</b><br/>Uptime ≥ 99.5 %/month; recovery < 60 s; RPO < 5 min"]
  src -->|generates| stim --> art
  art --> resp -->|measured by| meas
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef response fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class src,stim source
  class art artifact
  class resp,meas response
```

![AQA-1 six-part scenario](diagrams/scenario-AQA-1.png)

## Notes / assumptions

See [`../README.md`](../README.md) for traceability and the utility tree.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) · [utility tree](utility-tree.md)
