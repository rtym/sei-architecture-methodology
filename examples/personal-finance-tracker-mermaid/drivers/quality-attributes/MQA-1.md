# MQA-1: Cheap to add a report type

- **Status**: open
- **Source**: authored here (kept in sync with [`../../quality-attributes/scenarios.md`](../../quality-attributes/scenarios.md))

Documented as a **six-part quality attribute scenario** and supported by its own **horizontal
six-part scenario diagram**.

| Part | Value |
|------|-------|
| **ID** | MQA-1 |
| **ISO/IEC 25010 characteristic** | Maintainability |
| **Sub-characteristic** | modifiability |
| **Source of stimulus** | Developer |
| **Stimulus** | Adds a new dashboard report type |
| **Artifact** | Reporting module and read model |
| **Environment** | During a sprint |
| **Response** | Change is isolated to the reporting module and its tests; no other module is touched |
| **Response measure** | ≤ 1 person-day; ≤ 3 modules touched; 0 regressions |
| **Business goals supported** | BG-3 |
| **Priority** | Importance = M · Difficulty = M |
| **Type** | concrete |

## Six-part scenario diagram

```mermaid
flowchart LR
  %% Quality attribute scenario — MQA-1 — Maintainability / modifiability  (horizontal)
  src["<b>Source of stimulus</b><br/>Developer"]
  stim["<b>Stimulus</b><br/>Adds a new dashboard report type"]
  subgraph env["Environment: During a sprint"]
    art["<b>Artifact</b><br/>Reporting module and read model"]
  end
  resp["<b>Response</b><br/>Change is isolated to the reporting module and its tests; no other module is touched"]
  meas["<b>Response measure</b><br/>≤ 1 person-day; ≤ 3 modules touched; 0 regressions"]
  src -->|generates| stim --> art
  art --> resp -->|measured by| meas
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef response fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class src,stim source
  class art artifact
  class resp,meas response
```

![MQA-1 six-part scenario](diagrams/scenario-MQA-1.png)

## Notes / assumptions

See [`../README.md`](../README.md) for traceability and the utility tree.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) · [utility tree](utility-tree.md)
