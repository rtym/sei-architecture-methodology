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

Drawn with the house PlantUML pattern (this is the PlantUML tree): five boxes left-to-right — source of stimulus → stimulus → artifact → response → response measure — with the environment attached to the artifact.

```plantuml
@startuml scenario-PQA-1
!include ../../../../../skills/sei-diagrams/assets/plantuml-theme.puml
left to right direction
hide stereotype
title Quality attribute scenario — PQA-1 — Performance efficiency / time behaviour
rectangle "<b>Source of stimulus</b>
Registered user" as SRC #E7E3F3
rectangle "<b>Stimulus</b>
Loads the monthly dashboard with 500 concurrent users" as STIM #E7E3F3
rectangle "<b>Artifact</b>
Dashboard read path" as ART #EDF2F8
rectangle "<b>Response</b>
Renders totals, category chart, recent activity and savings-goal progress" as RESP #E4F0E9
rectangle "<b>Response measure</b>
Fully interactive < 1.5 s at p95" as MEAS #E4F0E9
rectangle "<b>Environment</b>
Normal operation" as ENV #F5EEE3
SRC  --> STIM : generates
STIM --> ART  : arrives at
ART  --> RESP : produces
RESP --> MEAS : measured by
ENV  ..> ART
@enduml
```

![PQA-1 six-part scenario](diagrams/scenario-PQA-1.png)

## Notes / assumptions

See [`../README.md`](../README.md) for traceability and the utility tree.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) · [utility tree](utility-tree.md)
