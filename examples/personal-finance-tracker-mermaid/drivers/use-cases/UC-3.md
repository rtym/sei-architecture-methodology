# UC-3: Import a bank statement (CSV)

- **Scope**: Personal Finance Tracker
- **Level**: user goal
- **Primary actor**: Registered user
- **Supporting actors**: none — the user uploads the file; no external system takes part
- **Trigger**: The user uploads a CSV file
- **Preconditions**: The user is authenticated
- **Postconditions**: the requested change is persisted and the dashboard reflects it
- **Priority**: medium
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

- **Drivers exercised**: Bulk write path; `<<include>>`s [UC-4](UC-4.md) (categorisation); the first candidate for asynchronous processing (PQA-2).

## Related drivers

`BG-1, PQA-2`

## Use case diagram

Mermaid `flowchart` fallback. Source:
[`diagrams/UC-3.mmd`](diagrams/UC-3.mmd).

```mermaid
flowchart LR
  %% Use case diagram — UC-3 Import a bank statement (CSV)
  pa(["fa:fa-user Registered user"])
  subgraph sys["System: Personal Finance Tracker"]
    uc3("UC-3 Import a bank statement (CSV)")
    uc4("UC-4 Categorise transaction")
  end
  pa --> uc3
  uc3 -. include .-> uc4
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  class pa source
  class uc3,uc4 artifact
```

![UC-3 — Import a bank statement (CSV)](diagrams/UC-3.png)

---

**Navigation**: [use-cases index](README.md) · [drivers README](../README.md)
