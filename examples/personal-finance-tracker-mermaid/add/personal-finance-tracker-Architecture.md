# Architecture: Personal Finance Tracker

- **System**: Web app for individuals to track income, expenses and savings goals.
- **Date**: 2026-09-06
- **Session**: `personal-finance-tracker-session.md`
- **Drivers**: [`../drivers/README.md`](../drivers/README.md)

## 1. Introduction

A mobile-web personal finance tracker. This document is the ADD 3.0 working architecture after
iteration 1 (overall structure, security, availability) and iteration 2 (dashboard read path).
Drivers: [`../drivers/README.md`](../drivers/README.md).

## 2. Context diagram

### Diagram

```mermaid
flowchart TB
  %% Context — Personal Finance Tracker (C4 level 1)
  user(["Registered user<br/><i>mobile browser</i>"])
  mail["Email provider<br/><i>external · SMTP/TLS</i>"]
  subgraph sys["Personal Finance Tracker"]
    core["Personal Finance Tracker<br/><i>records transactions, shows a monthly dashboard</i>"]
  end
  user -->|"Records transactions, views the dashboard (HTTPS)"| core
  core -->|"Sends verification &amp; alert email"| mail
  classDef source  fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef external fill:#F5EEE3,stroke:#B07D3B,color:#1F2933;
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  class user source
  class mail external
  class core internal
```

![Context — Personal Finance Tracker](../diagrams/personal-finance-tracker-Architecture-01.png)

### Description

A single external dependency at launch: a transactional email provider. Everything else is owned
by the system, keeping the SOC 2 (CON-4) surface small.

## 3. Architectural drivers

### Quality Attribute Scenarios (key)

| ID | QA (ISO 25010) | Stimulus | Response | Measure | Priority |
|----|----------------|----------|----------|---------|----------|
| SQA-1 | Security / confidentiality | Cross-user data access attempt | Rejected and logged | 0 reads; 100 % logged | (H,H) |
| AQA-1 | Reliability / availability | Single-AZ failure | Recovers automatically | ≥ 99.5 %/mo; < 60 s | (H,H) |
| PQA-1 | Performance efficiency / time behaviour | 500 concurrent dashboard loads | Renders fully | < 1.5 s @ p95 | (H,M) |

### Primary functional requirements — use cases (key)

| ID | Name | Priority |
|----|------|----------|
| UC-1 | Record a transaction | high |
| UC-2 | View the monthly dashboard | high |

### Constraints (key)

| ID | Type | Description |
|----|------|-------------|
| CON-4 | regulatory | Encryption in transit (TLS 1.2+) and at rest |
| CON-5 | technical | Primary datastore is PostgreSQL |

## 4. Container diagram

### Diagram

```mermaid
flowchart TB
  %% Container diagram — Personal Finance Tracker (C4 level 2)
  user(["Registered user<br/><i>mobile browser</i>"])
  mail["Email provider<br/><i>external · SMTP/TLS</i>"]
  subgraph sys["Personal Finance Tracker"]
    direction TB
    spa["Web App<br/><i>React 18 / TS PWA</i>"]
    api["API Service<br/><i>Node.js 20 / Fastify</i>"]
    db[("Primary Database<br/><i>PostgreSQL 15 · encrypted</i>")]
    cache[("Read Cache<br/><i>Redis 7</i>")]
  end
  user -->|"Uses over HTTPS (TLS 1.3)"| spa
  spa -->|"Calls REST API (JSON)"| api
  api -->|"Reads / writes tenant-scoped rows (SQL/TLS)"| db
  api -->|"Reads aggregates, invalidates on write"| cache
  api -->|"Sends verification &amp; alert email"| mail
  classDef source  fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef external fill:#F5EEE3,stroke:#B07D3B,color:#1F2933;
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef datastore fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class user source
  class mail external
  class spa,api internal
  class db,cache datastore
```

![Container diagram — Personal Finance Tracker](../diagrams/personal-finance-tracker-Architecture-02.png)

### Description

The API service is the single write path and the single place tenant scoping (SQA-1) is enforced.
The Redis read cache serves the dashboard (PQA-1); it is a performance element, not a system of
record, so its loss degrades latency but not correctness (AQA-1).

## 5. Component diagrams

### API Service

#### Diagram

```mermaid
flowchart TB
  %% Component diagram — API Service (C4 level 3)
  spa(["Web App<br/><i>React 18 / TS</i>"])
  subgraph svc["API Service"]
    direction TB
    router["HTTP Router<br/><i>Fastify routes</i>"]
    authz["Tenant Guard<br/><i>middleware — forces user_id scoping (SQA-1)</i>"]
    txn["Transaction Service<br/><i>TS module — UC-1</i>"]
    dash["Dashboard Service<br/><i>TS module — UC-2</i>"]
    repo["Data Access<br/><i>Kysely — parameterised, tenant-scoped SQL</i>"]
  end
  db[("Primary Database<br/><i>PostgreSQL 15</i>")]
  spa -->|"Sends REST requests (JSON/HTTPS)"| router
  router -->|"Passes authenticated context"| authz
  authz -->|"Delegates write commands"| txn
  authz -->|"Delegates dashboard queries"| dash
  txn -->|"Persists transactions"| repo
  dash -->|"Reads aggregates"| repo
  repo -->|"Executes tenant-scoped SQL (SQL/TLS)"| db
  classDef source  fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef datastore fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class spa source
  class router,authz,txn,dash,repo internal
  class db datastore
```

![Component diagram — API Service](../diagrams/personal-finance-tracker-Architecture-03.png)

#### Description

Every request passes through the Tenant Guard before any service runs, so cross-tenant access
(SQA-1) is structurally prevented rather than checked per-endpoint.

## 6. Sequence diagrams

```mermaid
sequenceDiagram
  title UC-2 dashboard load — realises PQA-1
  autonumber
  participant U as Web App
  participant A as API Service
  participant C as Read Cache
  participant D as Primary Database
  U->>A: GET /dashboard (month)
  A->>C: GET aggregates(user, month)
  alt cache hit
    C-->>A: aggregates
  else cache miss
    A->>D: SELECT aggregate rows (tenant-scoped)
    D-->>A: rows
    A->>C: SET aggregates(user, month) TTL 15 min
  end
  A-->>U: 200 dashboard JSON
```

![UC-2 dashboard load — realises PQA-1](../diagrams/personal-finance-tracker-Architecture-04.png)

On a cache hit the database is not touched, which is the common path and keeps p95 under the
1.5 s budget (PQA-1). On a miss the API recomputes from tenant-scoped rows and repopulates the
cache; a stale cache is bounded by the 15-minute TTL.

## 7. Deployment diagram

### Diagram

```mermaid
flowchart TB
  %% Deployment — Personal Finance Tracker (production, eu-west-1, 2 AZs)
  subgraph cloud["Managed cloud — eu-west-1 (2 AZs)"]
    subgraph edge["CDN + static hosting"]
      spa["Web App<br/><i>React 18 build — static assets</i>"]
    end
    subgraph run["Container platform (autoscaling, multi-AZ)"]
      api["API Service<br/><i>Node.js 20 — 2+ replicas across AZs</i>"]
    end
    subgraph data["Managed data tier (multi-AZ)"]
      db[("PostgreSQL 15<br/><i>primary + standby, automated failover</i>")]
      cache[("Redis 7<br/><i>primary + replica</i>")]
    end
  end
  spa -->|"Serves SPA to browser"| api
  api -->|"SQL / TLS"| db
  api -->|"RESP"| cache
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef datastore fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class spa,api internal
  class db,cache datastore
```

![Deployment — Personal Finance Tracker](../diagrams/personal-finance-tracker-Architecture-05.png)

### Description

The API runs as stateless replicas spread across two AZs behind the platform load balancer, and
the data tier uses managed primary/standby with automated failover — together these meet AQA-1
(single-AZ failure recovers < 60 s) within the CON-3 low-cost-tier constraint.

## 8. Interfaces and events

### Interfaces

| Component | Interface | Protocol | Description |
|-----------|-----------|----------|-------------|
| API Service | `POST /transactions` | REST / HTTPS | Create a transaction (UC-1) |
| API Service | `GET /dashboard?month=` | REST / HTTPS | Monthly aggregates + recent activity (UC-2) |
| Data Access | `query(userId, spec)` | in-process | Always injects `WHERE user_id = $userId` |

### Events

| Event | Publisher | Consumers | Description |
|-------|-----------|-----------|-------------|
| `TransactionWritten` | Transaction Service | Cache invalidator | Triggers dashboard-aggregate invalidation for the user/month |

## 9. Design decisions

| Decision | Rationale (cite driver IDs) | Alternatives discarded |
|----------|-----------------------------|------------------------|
| Single API service owns all writes and enforces tenant scoping in one middleware | SQA-1 needs one auditable choke point; CON-2 favours few moving parts | Per-service authz checks (easy to miss one) |
| Redis cache-aside for dashboard aggregates with 15-min TTL | PQA-1 p95 budget; DB alone won't meet it at 500 concurrent | Materialised views (slower to iterate — MQA-1); CDN caching (per-user data) |
| Managed PostgreSQL primary/standby, multi-AZ, automated failover | AQA-1 recovery target; CON-5 mandates PostgreSQL; CON-3 low-cost tier still offers this | Self-managed HA (CON-2 time), single instance (fails AQA-1) |

---

**Navigation**: [example root](../README.md) · [drivers](../drivers/README.md) · [session log](personal-finance-tracker-session.md) · [Views & Beyond docs](../docs/README.md) · [ATAM](../atam/atam-report.md)
