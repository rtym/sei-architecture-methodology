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

Drawn with the house PlantUML pattern (this is the PlantUML tree): five boxes left-to-right — source of stimulus → stimulus → artifact → response → response measure — with the environment attached to the artifact.

```plantuml
@startuml scenario-UQA-1
!include ../../../../../skills/sei-diagrams/assets/plantuml-theme.puml
left to right direction
hide stereotype
title Quality attribute scenario — UQA-1 — Interaction capability / operability
rectangle "<b>Source of stimulus</b>
First-time user" as SRC #E7E3F3
rectangle "<b>Stimulus</b>
Attempts to record their first transaction" as STIM #E7E3F3
rectangle "<b>Artifact</b>
Transaction form" as ART #EDF2F8
rectangle "<b>Response</b>
User completes the entry without consulting help documentation" as RESP #E4F0E9
rectangle "<b>Response measure</b>
>= 85 % task-completion rate in a 10-person moderated usability test" as MEAS #E4F0E9
rectangle "<b>Environment</b>
Normal operation" as ENV #F5EEE3
SRC  --> STIM : generates
STIM --> ART  : arrives at
ART  --> RESP : produces
RESP --> MEAS : measured by
ENV  ..> ART
@enduml
```

![UQA-1 six-part scenario](diagrams/scenario-UQA-1.png)

## Notes / assumptions

See [`../README.md`](../README.md) for traceability and the utility tree.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) · [utility tree](utility-tree.md)
