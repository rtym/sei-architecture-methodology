# SQA-1: No cross-user data access

- **Status**: open
- **Source**: authored here (kept in sync with [`../../quality-attributes/scenarios.md`](../../quality-attributes/scenarios.md))

Documented as a **six-part quality attribute scenario** and supported by its own **horizontal
six-part scenario diagram**.

| Part | Value |
|------|-------|
| **ID** | SQA-1 |
| **ISO/IEC 25010 characteristic** | Security |
| **Sub-characteristic** | confidentiality |
| **Source of stimulus** | Authenticated user acting as an attacker |
| **Stimulus** | Requests another user's transactions by guessing record IDs |
| **Artifact** | API layer and data store |
| **Environment** | Normal operation |
| **Response** | Request is rejected; the attempt is written to an append-only audit log and alerted |
| **Response measure** | 0 successful cross-user reads; 100 % of attempts logged; alert < 1 min |
| **Business goals supported** | BG-2 |
| **Priority** | Importance = H · Difficulty = H |
| **Type** | concrete |

## Six-part scenario diagram

```mermaid
flowchart LR
  %% Quality attribute scenario — SQA-1 — Security / confidentiality  (horizontal)
  src["<b>Source of stimulus</b><br/>Authenticated user acting as an attacker"]
  stim["<b>Stimulus</b><br/>Requests another user's transactions by guessing record IDs"]
  subgraph env["Environment: Normal operation"]
    art["<b>Artifact</b><br/>API layer and data store"]
  end
  resp["<b>Response</b><br/>Request is rejected; the attempt is written to an append-only audit log and alerted"]
  meas["<b>Response measure</b><br/>0 successful cross-user reads; 100 % of attempts logged; alert < 1 min"]
  src -->|generates| stim --> art
  art --> resp -->|measured by| meas
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef response fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class src,stim source
  class art artifact
  class resp,meas response
```

![SQA-1 six-part scenario](diagrams/scenario-SQA-1.png)

## Notes / assumptions

See [`../README.md`](../README.md) for traceability and the utility tree.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) · [utility tree](utility-tree.md)
