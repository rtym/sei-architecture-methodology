# UC-2: View the monthly dashboard

- **Scope**: Personal Finance Tracker
- **Level**: user goal
- **Primary actor**: Registered user
- **Supporting actors**: —
- **Trigger**: The user opens the app or navigates to "Dashboard"
- **Preconditions**: The user is authenticated and has zero or more transactions
- **Postconditions**: the requested change is persisted and the dashboard reflects it
- **Priority**: high
- **Status**: open

## Main success scenario

1. The system loads the user's month-to-date aggregates.
2. The system renders totals, a category breakdown chart, recent transactions and savings-goal progress.

## Extensions / alternate flows

- **1a.** Aggregates cache miss → the system recomputes from the tenant-scoped transaction store and repopulates the cache.

## Architectural significance

- **Drivers exercised**: The performance-critical read path (PQA-1); shapes the read-model / caching decision; first-use experience (UQA-1).

## Related drivers

`BG-1, PQA-1, UQA-1`

## Use case diagram

Mermaid `flowchart` fallback (this is the Mermaid tree). Source:
[`diagrams/UC-2.mmd`](diagrams/UC-2.mmd) · rendered + visually verified.

```mermaid
flowchart LR
  %% Use case diagram — UC-2 View the monthly dashboard
  pa(["Registered user"])
  subgraph sys["System: Personal Finance Tracker"]
    uc2("UC-2 View the monthly dashboard")
  end
  pa --> uc2
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  class pa source
  class uc2 artifact
```

![UC-2 — View the monthly dashboard](diagrams/UC-2.png)

---

**Navigation**: [use-cases index](README.md) · [drivers README](../README.md)
