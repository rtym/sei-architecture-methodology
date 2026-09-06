# PQA-2: Bulk import stays responsive

- **Status**: open
- **Source**: authored here (kept in sync with `../../scenarios.md`)

Documented as a **six-part quality attribute scenario** and supported by its own **horizontal
six-part scenario diagram**.

| Part | Value |
|------|-------|
| **ID** | PQA-2 |
| **ISO/IEC 25010 characteristic** | Performance efficiency |
| **Sub-characteristic** | capacity |
| **Source of stimulus** | Registered user |
| **Stimulus** | Imports a 5 000-row CSV bank statement |
| **Artifact** | Import Worker |
| **Environment** | Normal operation |
| **Response** | Parses, maps and bulk-inserts asynchronously; interactive traffic is unaffected |
| **Response measure** | Import completes < 30 s; dashboard p95 stays < 1.8 s during the import |
| **Business goals supported** | BG-1 |
| **Priority** | Importance = M · Difficulty = M |
| **Type** | concrete |

## Six-part scenario diagram

```mermaid
flowchart LR
  %% Quality attribute scenario — PQA-2 — Performance efficiency / capacity  (horizontal)
  src["<b>Source of stimulus</b><br/>Registered user"]
  stim["<b>Stimulus</b><br/>Imports a 5 000-row CSV bank statement"]
  subgraph env["Environment: Normal operation"]
    art["<b>Artifact</b><br/>Import Worker"]
  end
  resp["<b>Response</b><br/>Parses, maps and bulk-inserts asynchronously; interactive traffic is unaffected"]
  meas["<b>Response measure</b><br/>Import completes < 30 s; dashboard p95 stays < 1.8 s during the import"]
  src -->|generates| stim --> art
  art --> resp -->|measured by| meas
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef response fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class src,stim source
  class art artifact
  class resp,meas response
```

![PQA-2 six-part scenario](diagrams/scenario-PQA-2.png)

## Notes / assumptions

See [`../README.md`](../README.md) for traceability and the utility tree.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) · [utility tree](utility-tree.md)
