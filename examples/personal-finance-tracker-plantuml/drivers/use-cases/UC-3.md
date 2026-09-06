# UC-3: Import a bank statement (CSV)

- **Scope**: Personal Finance Tracker
- **Level**: user goal
- **Primary actor**: Registered user
- **Supporting actors**: Bank Import API
- **Trigger**: The user uploads a CSV file
- **Preconditions**: The user is authenticated
- **Postconditions**: the requested change is persisted and the dashboard reflects it
- **Priority**: high
- **Status**: open

## Main success scenario

1. The user uploads a CSV file.
2. The system parses the file and maps rows to transactions.
3. The system asks the user to confirm the category mapping.
4. The system bulk-inserts the transactions asynchronously.
5. The system updates the dashboard aggregates and reports per-row results.

## Extensions / alternate flows

- **2a.** Unrecognised format → the system offers a guided column-mapping step.
- **4a.** Partial failure → the system returns a per-row result report.

## Architectural significance

- **Drivers exercised**: Bulk write path; `<<include>>`s categorisation; the first candidate for asynchronous processing (PQA-2).

## Related drivers

`BG-1, PQA-2`

## Use case diagram

Native PlantUML `usecase` notation (this is the PlantUML tree): stick-figure actors outside the
boundary rectangle, ellipse use cases inside, dashed `<<include>>` dependency. Source:
[`diagrams/UC-3.puml`](diagrams/UC-3.puml) · rendered + visually verified.

```plantuml
@startuml UC-3
!include ../../../../../skills/sei-diagrams/assets/plantuml-theme.puml
skinparam actorStyle awesome
left to right direction
title Use case — UC-3 Import a bank statement (CSV)
actor "Registered user" as pa
actor "Bank Import API" as sa
rectangle "Personal Finance Tracker" {
  usecase "UC-3
Import a bank statement (CSV)" as uc3
  usecase "UC-3a
Categorise transaction" as uc3a
}
pa --> uc3
sa --> uc3
uc3 ..> uc3a : <<include>>
@enduml
```

![UC-3 — Import a bank statement (CSV)](diagrams/UC-3.png)

---

**Navigation**: [use-cases index](README.md) · [drivers README](../README.md)
