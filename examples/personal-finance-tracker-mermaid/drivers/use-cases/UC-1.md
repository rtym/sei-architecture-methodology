# UC-1: Record a transaction

- **Scope**: Personal Finance Tracker
- **Level**: user goal
- **Primary actor**: Registered user
- **Supporting actors**: —
- **Trigger**: The user submits the "add transaction" form
- **Preconditions**: The user is authenticated
- **Postconditions**: the requested change is persisted and the dashboard reflects it
- **Priority**: high
- **Status**: in design

## Main success scenario

1. The user enters amount, date, category and an optional note.
2. The system validates the input.
3. The system persists the transaction (tenant-scoped).
4. The system updates the affected dashboard aggregates.
5. The system confirms the save.

## Extensions / alternate flows

- **2a.** Validation fails → the system shows field-level errors and writes nothing.
- **3a.** The data store is unavailable → the write is queued and the user is told "saved, syncing".

## Architectural significance

- **Drivers exercised**: Dominates write load; sits on the p95 latency path (PQA-1); every modifiability change touches it (MQA-1).

## Related drivers

`BG-1, PQA-1, MQA-1, CON-4`

## Use case diagram

Mermaid `flowchart` fallback (this is the Mermaid tree): the actor sits outside the system
boundary, the use cases inside, and `include` is a dashed dependency. Source:
[`diagrams/UC-1.mmd`](diagrams/UC-1.mmd) · rendered + visually verified.

```mermaid
flowchart LR
  %% Use case diagram — UC-1 Record a transaction
  pa(["Registered user"])
  subgraph sys["System: Personal Finance Tracker"]
    uc1("UC-1 Record a transaction")
    uc1a("UC-1a Categorise transaction")
  end
  pa --> uc1
  uc1 -. include .-> uc1a
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  class pa source
  class uc1,uc1a artifact
```

![UC-1 — Record a transaction](diagrams/UC-1.png)

---

**Navigation**: [use-cases index](README.md) · [drivers README](../README.md)
