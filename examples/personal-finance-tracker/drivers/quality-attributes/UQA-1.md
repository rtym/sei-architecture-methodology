# UQA-1: First transaction without help

- **Status**: open
- **Source**: authored here (kept in sync with `../../scenarios.md`)

Documented as a **six-part quality attribute scenario** and supported by its own **horizontal
six-part scenario diagram**.

| Part | Value |
|------|-------|
| **ID** | UQA-1 |
| **ISO/IEC 25010 characteristic** | Interaction capability |
| **Sub-characteristic** | operability |
| **Source of stimulus** | First-time user |
| **Stimulus** | Attempts to record their first transaction |
| **Artifact** | Transaction form |
| **Environment** | Normal operation |
| **Response** | User completes the entry without consulting help documentation |
| **Response measure** | ≥ 85 % task-completion rate in a 10-person moderated usability test |
| **Business goals supported** | BG-1 |
| **Priority** | Importance = M · Difficulty = M |
| **Type** | concrete |

## Six-part scenario diagram

```mermaid
flowchart LR
  %% Quality attribute scenario — UQA-1 — Interaction capability / operability  (horizontal)
  src["<b>Source of stimulus</b><br/>First-time user"]
  stim["<b>Stimulus</b><br/>Attempts to record their first transaction"]
  subgraph env["Environment: Normal operation"]
    art["<b>Artifact</b><br/>Transaction form"]
  end
  resp["<b>Response</b><br/>User completes the entry without consulting help documentation"]
  meas["<b>Response measure</b><br/>≥ 85 % task-completion rate in a 10-person moderated usability test"]
  src -->|generates| stim --> art
  art --> resp -->|measured by| meas
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef response fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class src,stim source
  class art artifact
  class resp,meas response
```

![UQA-1 six-part scenario](diagrams/scenario-UQA-1.png)

## Notes / assumptions

See `../index.md` for traceability and the utility tree.
