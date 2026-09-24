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
  %% name: context
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

![Context — Personal Finance Tracker](../diagrams/context.png)

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
  %% name: container
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

![Container diagram — Personal Finance Tracker](../diagrams/container.png)

### Description

The API service is the single write path and the single place tenant scoping (SQA-1) is enforced.
The Redis read cache serves the dashboard (PQA-1); it is a performance element, not a system of
record, so its loss degrades latency but not correctness (AQA-1).

## 5. Component and module views

### API Service

#### Diagram

```mermaid
flowchart TB
  %% Component diagram — API Service (C4 level 3)
  %% name: component-api
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

![Component diagram — API Service](../diagrams/component-api.png)

#### Description

Every request passes through the Tenant Guard before any service runs, so cross-tenant access
(SQA-1) is structurally prevented rather than checked per-endpoint.

### Module decomposition

#### Diagram

```mermaid
flowchart TB
  %% Module decomposition — Personal Finance Tracker API (layered)
  %% name: module-decomposition
  subgraph api["api-service (deployable)"]
    direction TB
    subgraph L1["edge layer"]
      http["http<br/><i>routing, request/response DTOs</i>"]
    end
    subgraph L2["admission layer"]
      security["security<br/><i>auth, tenant-guard</i>"]
    end
    subgraph L3["domain layer"]
      direction LR
      txn["transactions<br/><i>UC-1: create/edit/delete</i>"]
      categories["categories<br/><i>user categories</i>"]
      reporting["reporting<br/><i>UC-2: aggregates + report-type registry</i>"]
      imports["imports<br/><i>UC-3: CSV parse + map + bulk insert</i>"]
    end
    subgraph L4["infrastructure layer"]
      direction LR
      persistence["persistence<br/><i>tenant-scoped repositories, migrations</i>"]
      platform["platform<br/><i>config, logging, audit-log client</i>"]
    end
  end
  http --> security
  security --> txn & categories & reporting & imports
  txn & categories & reporting & imports --> persistence
  persistence --> platform
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  class http,security,txn,categories,reporting,imports,persistence,platform internal
```

![Module decomposition — Personal Finance Tracker API](../diagrams/module-decomposition.png)

#### Description

Four layers inside the single deployable; a layer may use only the layer below it, and the four
domain modules may not use one another (a cross-domain need is mediated by `reporting` reading
through `persistence`). The `security` layer is the one place tenant scoping is applied (SQA-1,
ADR-2); the `reporting` module's report-type registry is what keeps MQA-1 to a one-day change.
This is the seed of the Views-and-Beyond [module decomposition view](../docs/view-module-decomposition.md).

## 6. Sequence diagrams

```mermaid
sequenceDiagram
  title UC-2 dashboard load — realises PQA-1
  %% name: sequence-dashboard
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

![UC-2 dashboard load — realises PQA-1](../diagrams/sequence-dashboard.png)

On a cache hit the database is not touched, which is the common path and keeps p95 under the
1.5 s budget (PQA-1). On a miss the API recomputes from tenant-scoped rows and repopulates the
cache; a stale cache is bounded by the 15-minute TTL.

## 7. Deployment diagram

### Diagram

```mermaid
flowchart TB
  %% Deployment — Personal Finance Tracker (production, eu-west-1, 2 AZs)
  %% name: deployment
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

![Deployment — Personal Finance Tracker](../diagrams/deployment.png)

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

### `POST /transactions` — full interface spec (the four agreement points)

The one interface `UC-1` and `SQA-1` both run through, specified per `references/interfaces.md`:

| Agreement point | Specification |
|-----------------|---------------|
| **Scope** | available to the Web App only, via the CDN + Tenant Guard; not exposed to any other actor. The Tenant Guard is the actor for the Transaction Service. |
| **Interaction style** | synchronous request/response over REST + HTTPS (TLS 1.3); idempotency key header so a client retry is safe; no long-poll. |
| **Data representation & structure** | request `{amount: integer (minor units), date: ISO-8601 date, categoryId: uuid, note?: string ≤ 280}`; response `201 {id: uuid, ...echo}`; JSON (matches the SPA's parser; compact; interceptable for debugging). `user_id` is **never** in the body — it is taken from the verified JWT. |
| **Error model** | `400` field-level validation errors (nothing written) · `401` missing/expired token · `403` cross-tenant attempt (written to the append-only audit log, alert < 1 min — `SQA-1`) · `409` duplicate idempotency key · `503` store unavailable → the client is told "saved, syncing" and the write is queued (`UC-1` 3a). |

### Events

| Event | Publisher | Consumers | Description |
|-------|-----------|-----------|-------------|
| `TransactionWritten` | Transaction Service | Cache invalidator | Triggers dashboard-aggregate invalidation for the user/month |

## 9. Design decisions

Each significant decision is an ADR in [`adr/`](adr/ADR-1.md); this table is the log.

| Decision | Rationale (cite driver IDs) | Alternatives discarded | ADR |
|----------|-----------------------------|------------------------|-----|
| Single API service owns all writes and enforces tenant scoping in one middleware | SQA-1 needs one auditable choke point; CON-2 favours few moving parts | Per-service authz checks (easy to miss one) | [ADR-2](adr/ADR-2.md) |
| Redis cache-aside for dashboard aggregates with 15-min TTL | PQA-1 p95 budget; DB alone won't meet it at 500 concurrent | Materialised views (slower to iterate — MQA-1); CDN caching (per-user data) | [ADR-1](adr/ADR-1.md) |
| Managed PostgreSQL primary/standby, multi-AZ, automated failover | AQA-1 recovery target; CON-5 mandates PostgreSQL; CON-3 low-cost tier still offers this | Self-managed HA (CON-2 time), single instance (fails AQA-1) | [ADR-3](adr/ADR-3.md) |

---

**Navigation**: [architecture package](../README.md) · [ADRs](adr/ADR-1.md) · [drivers](../drivers/README.md) · [session log](personal-finance-tracker-session.md) · [Views & Beyond docs](../docs/README.md) · [ATAM](../atam/atam-report.md)
