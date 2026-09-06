# MQA-1: Cheap to add a report type

- **Status**: open
- **Source**: authored here (kept in sync with `../../scenarios.md`)

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

Drawn with the house PlantUML pattern (this is the PlantUML tree): five boxes left-to-right — source of stimulus → stimulus → artifact → response → response measure — with the environment attached to the artifact.

```plantuml
@startuml scenario-MQA-1
!include ../../../../../skills/sei-diagrams/assets/plantuml-theme.puml
left to right direction
hide stereotype
title Quality attribute scenario — MQA-1 — Maintainability / modifiability
rectangle "<b>Source of stimulus</b>
Developer" as SRC #E7E3F3
rectangle "<b>Stimulus</b>
Adds a new dashboard report type" as STIM #E7E3F3
rectangle "<b>Artifact</b>
Reporting module and read model" as ART #EDF2F8
rectangle "<b>Response</b>
Change is isolated to the reporting module and its tests; no other module is touched" as RESP #E4F0E9
rectangle "<b>Response measure</b>
<= 1 person-day; <= 3 modules touched; 0 regressions" as MEAS #E4F0E9
rectangle "<b>Environment</b>
During a sprint" as ENV #F5EEE3
SRC  --> STIM : generates
STIM --> ART  : arrives at
ART  --> RESP : produces
RESP --> MEAS : measured by
ENV  ..> ART
@enduml
```

![MQA-1 six-part scenario](diagrams/scenario-MQA-1.png)

## Notes / assumptions

See [`../README.md`](../README.md) for traceability and the utility tree.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) · [utility tree](utility-tree.md)
