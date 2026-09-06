# PQA-1: Dashboard fast under load

- **Status**: open
- **Source**: authored here (kept in sync with `../../scenarios.md`)

Documented as a **six-part quality attribute scenario** and supported by its own **horizontal
six-part scenario diagram**.

| Part | Value |
|------|-------|
| **ID** | PQA-1 |
| **ISO/IEC 25010 characteristic** | Performance efficiency |
| **Sub-characteristic** | time behaviour |
| **Source of stimulus** | Registered user |
| **Stimulus** | Loads the monthly dashboard with 500 concurrent users |
| **Artifact** | Dashboard read path |
| **Environment** | Normal operation |
| **Response** | Renders totals, category chart, recent activity and savings-goal progress |
| **Response measure** | Fully interactive < 1.5 s at p95 |
| **Business goals supported** | BG-1 |
| **Priority** | Importance = H · Difficulty = M |
| **Type** | concrete |

## Six-part scenario diagram

```mermaid
flowchart LR
  %% Quality attribute scenario — PQA-1 — Performance efficiency / time behaviour  (horizontal)
  src["<b>Source of stimulus</b><br/>Registered user"]
  stim["<b>Stimulus</b><br/>Loads the monthly dashboard with 500 concurrent users"]
  subgraph env["Environment: Normal operation"]
    art["<b>Artifact</b><br/>Dashboard read path"]
  end
  resp["<b>Response</b><br/>Renders totals, category chart, recent activity and savings-goal progress"]
  meas["<b>Response measure</b><br/>Fully interactive < 1.5 s at p95"]
  src -->|generates| stim --> art
  art --> resp -->|measured by| meas
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef response fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class src,stim source
  class art artifact
  class resp,meas response
```

![PQA-1 six-part scenario](diagrams/scenario-PQA-1.png)

## Notes / assumptions

See `../index.md` for traceability and the utility tree.
