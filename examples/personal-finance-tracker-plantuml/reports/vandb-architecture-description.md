# Architecture Description — Personal Finance Tracker

_Views-and-Beyond architecture description_

> Generated 2026-09-06 · 9 source file(s)

## Contents

  - [How this documentation is organised](#how-this-documentation-is-organised)
  - [View selection — stakeholder concerns → views](#view-selection--stakeholder-concerns--views)
  - [Where do I look to answer…](#where-do-i-look-to-answer)
  - [Related artifacts](#related-artifacts)
- [System overview — Personal Finance Tracker](#system-overview--personal-finance-tracker)
  - [What it does](#what-it-does)
  - [Context](#context)
  - [Primary functional requirements (use cases)](#primary-functional-requirements-use-cases)
  - [Driving quality attribute scenarios](#driving-quality-attribute-scenarios)
- [View: Module decomposition  (Module / decomposition)](#view-module-decomposition--module--decomposition)
  - [1. Primary presentation](#1-primary-presentation)
  - [2. Element catalog](#2-element-catalog)
    - [2.1 Elements and their properties](#21-elements-and-their-properties)
    - [2.2 Relations and their properties](#22-relations-and-their-properties)
    - [2.3 Element interfaces](#23-element-interfaces)
    - [2.4 Element behavior](#24-element-behavior)
  - [3. Context diagram](#3-context-diagram)
  - [4. Variability guide](#4-variability-guide)
  - [5. Rationale](#5-rationale)
- [View: Runtime (Component-and-Connector / service)](#view-runtime-component-and-connector--service)
  - [1. Primary presentation](#1-primary-presentation-1)
  - [2. Element catalog](#2-element-catalog-1)
    - [2.1 Elements and their properties](#21-elements-and-their-properties-1)
    - [2.2 Relations and their properties](#22-relations-and-their-properties-1)
    - [2.3 Element interfaces](#23-element-interfaces-1)
    - [2.4 Element behavior](#24-element-behavior-1)
  - [3. Context diagram](#3-context-diagram-1)
  - [4. Variability guide](#4-variability-guide-1)
  - [5. Rationale](#5-rationale-1)
- [View: Deployment (Allocation / deployment)](#view-deployment-allocation--deployment)
  - [1. Primary presentation](#1-primary-presentation-2)
  - [2. Element catalog](#2-element-catalog-2)
    - [2.1 Elements and their properties](#21-elements-and-their-properties-2)
    - [2.2 Relations and their properties](#22-relations-and-their-properties-2)
    - [2.3 Element interfaces](#23-element-interfaces-2)
    - [2.4 Element behavior](#24-element-behavior-2)
  - [3. Context diagram](#3-context-diagram-2)
  - [4. Variability guide](#4-variability-guide-2)
  - [5. Rationale](#5-rationale-2)
- [Mapping between views — Personal Finance Tracker](#mapping-between-views--personal-finance-tracker)
  - [Module → runtime component (C&C)](#module--runtime-component-cc)
  - [Runtime component (C&C) → deployment node (Allocation)](#runtime-component-cc--deployment-node-allocation)
  - [Driver → element realising it](#driver--element-realising-it)
- [Rationale — Personal Finance Tracker](#rationale--personal-finance-tracker)
  - [ADR-1: Cache-aside read model for the dashboard](#adr-1-cache-aside-read-model-for-the-dashboard)
  - [ADR-2: Single tenant-guard choke point](#adr-2-single-tenant-guard-choke-point)
  - [ADR-3: Stateless API replicas + managed multi-AZ database](#adr-3-stateless-api-replicas--managed-multi-az-database)
- [Directory — Personal Finance Tracker](#directory--personal-finance-tracker)
  - [Index — where elements are defined](#index--where-elements-are-defined)
  - [Glossary](#glossary)
  - [Acronyms](#acronyms)
  - [Driver ID prefixes used here](#driver-id-prefixes-used-here)
- [Change log — architecture description](#change-log--architecture-description)


---

# Architecture Description — Personal Finance Tracker

Views-and-Beyond documentation package. This file is the **documentation roadmap** (GitHub
renders it on directory browse). Every diagram in this package is PlantUML / C4-PlantUML.

## How this documentation is organised

| File | V&B part | Read it to… |
|------|----------|-------------|
| [`README.md`](README.md) (this file) | Roadmap + organisation | know what exists and where to look |
| [`system-overview.md`](system-overview.md) | System overview | understand what the system does and its context |
| [`view-module-decomposition.md`](view-module-decomposition.md) | Module view (decomposition) | see the code units and who owns what |
| [`view-cnc-runtime.md`](view-cnc-runtime.md) | Component-and-Connector view (service) | see what runs and how parts interact at runtime |
| [`view-allocation-deployment.md`](view-allocation-deployment.md) | Allocation view (deployment) | see where each part runs in production |
| [`mapping-between-views.md`](mapping-between-views.md) | Mapping between views | correlate a module ↔ runtime component ↔ node |
| [`rationale.md`](rationale.md) | Rationale | understand why the big decisions were made (ADR log) |
| [`directory.md`](directory.md) | Directory | look up a term, an acronym, or where an element is defined |
| [`change-log.md`](change-log.md) | — | revision history of this description |

Only a stub view set is included in this example (one view per viewtype). A real package adds a
uses/layered module view, more C&C views, and install / work-assignment allocation views as
stakeholder concerns require.

## View selection — stakeholder concerns → views

| Stakeholder | Concern | View(s) |
|-------------|---------|---------|
| New developer | Where does the code live? What can depend on what? | [Module decomposition](view-module-decomposition.md) |
| Developer / architect | What runs at runtime? How is tenant isolation enforced? | [C&C runtime](view-cnc-runtime.md) |
| Performance | Where is the dashboard latency budget spent? | [C&C runtime](view-cnc-runtime.md) + sequence diagrams in the ADD [Architecture.md §6](../add/personal-finance-tracker-Architecture.md) |
| Operations | What is deployed where? How does it survive an AZ loss? | [Allocation deployment](view-allocation-deployment.md) |
| Security / auditor | Where is the confidentiality control? | [C&C runtime](view-cnc-runtime.md) + [`rationale.md`](rationale.md) |
| Project lead | Who is responsible for which module? | [Module decomposition](view-module-decomposition.md) (owner column) |

## Where do I look to answer…

- *"If I change the category logic, what else is affected?"* → [Module decomposition](view-module-decomposition.md) (dependencies).
- *"How is `SQA-1` (cross-user isolation) achieved?"* → [C&C runtime](view-cnc-runtime.md) §5 rationale + [`rationale.md`](rationale.md) ADR-2.
- *"What happens on a cache miss?"* → ADD [`Architecture.md`](../add/personal-finance-tracker-Architecture.md) §6.
- *"What recovers us from an AZ failure?"* → [Allocation deployment](view-allocation-deployment.md) view + [`rationale.md`](rationale.md) ADR-3.

## Related artifacts

- Drivers register: [`../drivers/README.md`](../drivers/README.md)
- Quality attribute scenarios: [`../scenarios.md`](../scenarios.md)
- ADD working architecture: [`../add/personal-finance-tracker-Architecture.md`](../add/personal-finance-tracker-Architecture.md)
- ATAM evaluation: [`../atam/atam-report.md`](../atam/atam-report.md)

---

**Navigation**: [example root](../README.md) · [drivers](../drivers/README.md) ·
[ADD architecture](../add/personal-finance-tracker-Architecture.md) · [ATAM](../atam/atam-report.md)


---

# System overview — Personal Finance Tracker

## What it does

A mobile-web application that lets an individual record income and expense transactions, organise
them into user-defined categories, see a monthly dashboard (totals, a category breakdown, recent
activity, savings-goal progress), and import transactions from a bank CSV statement.

## Context

Single-tenant-per-user SaaS. One external dependency at launch: a transactional email provider
(account verification, security alerts). No payment processing. Runs in mobile browsers; there is
no native app at launch (`CON-1`).

```plantuml
@startuml system-overview-01
!include ../../../../skills/sei-diagrams/assets/c4/C4_Context.puml
!include ../../../../skills/sei-diagrams/assets/c4/sei-c4-palette.puml
LAYOUT_LEFT_RIGHT()
title System context — Personal Finance Tracker
Person(user, "Registered user", "Mobile browser")
System(sys, "Personal Finance Tracker", "Records transactions; monthly dashboard; CSV import")
System_Ext(mail, "Email provider", "SMTP/TLS")
Rel(user, sys, "Records transactions, views the dashboard", "HTTPS")
Rel(sys, mail, "Sends verification & alert email", "SMTP")
@enduml
```

![System context — Personal Finance Tracker](diagrams/system-overview-01.png)

## Primary functional requirements (use cases)

- `UC-1` Record a transaction
- `UC-2` View the monthly dashboard
- `UC-3` Import a bank statement (CSV)

## Driving quality attribute scenarios

See [`../scenarios.md`](../scenarios.md) for the six-part detail. The architecture is shaped mainly by:

- `SQA-1` (security / confidentiality) — cross-user access rejected and logged; 0 successful reads.
- `AQA-1` (reliability / availability) — survive a single-AZ failure, recover < 60 s, ≥ 99.5 %/mo.
- `PQA-1` (performance / time behaviour) — dashboard interactive < 1.5 s at p95, 500 concurrent users.
- `MQA-1` (maintainability / modifiability) — add a report type in ≤ 1 person-day, 0 regressions.

---

**Navigation**: [docs README](README.md) · [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md)


---

# View: Module decomposition  (Module / decomposition)

- **Viewtype**: Module
- **Style**: decomposition (with a dependency overlay)
- **Stakeholders / concerns addressed**: new developers (where code lives), architect (allowed
  dependencies), project lead (ownership), maintainer (change impact — `MQA-1`)
- **Date**: 2026-09-06

## 1. Primary presentation

```plantuml
@startuml view-module-decomposition-01
!include ../../../../skills/sei-diagrams/assets/plantuml-theme.puml
skinparam linetype ortho
title Module decomposition — Personal Finance Tracker API (layered; allowed-to-use is downward)
rectangle "**edge layer**\nhttp — routing, request/response DTOs" as L1
rectangle "**admission layer**\nsecurity — auth, tenant guard (SQA-1)" as L2
rectangle "**domain layer**\ntransactions (UC-1) · categories · reporting (UC-2) · imports (UC-3)" as L3
rectangle "**infrastructure layer**\npersistence — tenant-scoped repositories · platform — config, logging, audit-log client" as L4
L1 -down-> L2 : uses
L2 -down-> L3 : uses
L3 -down-> L4 : uses
note right of L3
  Domain modules must not use one another;
  a cross-domain need is mediated by reporting
  reading via persistence.
end note
@enduml
```

> The **allowed-to-use** relation is shown between layers. `platform` is a cross-cutting utility
> used by every layer above it; those edges are omitted to keep the primary presentation legible
> (§2.2 lists them). Domain modules must not use one another.

![View: Module decomposition](diagrams/view-module-decomposition-01.png)

_visually verified: yes · relative path renders on GitHub / GitLab_

## 2. Element catalog

### 2.1 Elements and their properties

| Element | Responsibility / role | Owner | Key properties |
|---------|-----------------------|-------|----------------|
| `http` | HTTP routing, request validation, DTO mapping | Eng lead | no business logic; depends only on `security` |
| `security` | Authentication, session handling, **tenant guard** (forces `user_id` scoping) | Eng lead | the only module allowed to admit a request to the domain modules |
| `transactions` | `UC-1` create/edit/delete transactions | Eng lead | pure domain + calls to `persistence` |
| `categories` | User-defined categories | Eng lead | domain + `persistence` |
| `reporting` | `UC-2` dashboard aggregates; **report-type registry** (extension point for `MQA-1`) | Eng lead | new report types are added here without touching other modules |
| `imports` | `UC-3` CSV parse, column mapping, bulk insert; queue consumer entry point | Eng lead | uses `persistence`; runs in-process or as the worker |
| `persistence` | Tenant-scoped repositories, query builder, migrations | Eng lead | every query is parameterised and `user_id`-scoped |
| `platform` | Config, structured logging, append-only audit-log client, metrics | Eng lead | no dependencies on domain modules |

### 2.2 Relations and their properties

| From | Relation | To | Properties |
|------|----------|----|-----------|
| `http` | depends-on | `security` | the only downward edge from `http` |
| `security` | depends-on | each domain module | admits requests after tenant scoping |
| domain modules | depends-on | `persistence`, `platform` | never on each other |
| `persistence` | depends-on | `platform` | logging, config only |

**Allowed-dependency rule**: `http → security → {domain} → persistence → platform`. Domain modules
must not depend on one another; a cross-domain need is mediated by `reporting` reading via
`persistence`. Enforced in CI by a dependency-check rule.

### 2.3 Element interfaces

Module APIs are internal TypeScript module boundaries. The externally visible HTTP interface is in
the ADD [`../add/personal-finance-tracker-Architecture.md`](../add/personal-finance-tracker-Architecture.md) §8.

### 2.4 Element behavior

Runtime collaboration for the dashboard flow is the sequence diagram in the ADD `Architecture.md` §6.

## 3. Context diagram

This view covers the `api-service` deployable only. The `Web App` (React) and the `Import Worker`
process are outside it; the worker reuses the `imports` and `persistence` modules as a library.

## 4. Variability guide

- **Report types**: registered in `reporting` via a `ReportType` registry entry — add a class +
  a registry line, no other module changes (`MQA-1`).
- **Storage engine**: `persistence` isolates the query builder; swapping the SQL dialect is
  contained here (`CON-5` currently pins PostgreSQL).
- **Import formats**: `imports` has a `StatementParser` strategy; new bank formats are new
  strategy classes.

## 5. Rationale

- The `security` module is the **single choke point** for tenant scoping so `SQA-1` is enforced
  structurally and is auditable in one place (see [`rationale.md`](rationale.md) ADR-2). The alternative —
  per-endpoint checks in `http` — was rejected as too easy to miss.
- Forbidding domain-to-domain dependencies keeps change impact local, serving `MQA-1`
  (add a report type in ≤ 1 person-day, 0 regressions).
- `platform` has no domain dependencies so it can be extracted to a shared library later without
  untangling business code.

---

**Navigation**: [docs README](README.md) · [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md)


---

# View: Runtime (Component-and-Connector / service)

- **Viewtype**: Component-and-Connector
- **Style**: service-oriented (request/response + async queue)
- **Stakeholders / concerns addressed**: architect & developers (what runs, how parts interact),
  performance (`PQA-1` read path), security (`SQA-1` isolation control), operations
- **Date**: 2026-09-06

## 1. Primary presentation

```plantuml
@startuml view-cnc-runtime-01
!include ../../../../skills/sei-diagrams/assets/c4/C4_Container.puml
!include ../../../../skills/sei-diagrams/assets/c4/sei-c4-palette.puml
LAYOUT_TOP_DOWN()
title Runtime (C&C) view — Personal Finance Tracker
Person(user, "Registered user", "Mobile browser")
System_Boundary(sys, "Personal Finance Tracker") {
  Container(spa, "Web App", "React 18 / TS PWA", "Stateless; no direct DB access")
  Container(api, "API Service", "Node.js 20 / Fastify", "Tenant guard + services + Data Access; only writer")
  Container(worker, "Import Worker", "Node.js 20 queue consumer", "Parses CSV, bulk-inserts; reuses Data Access")
  ContainerDb(db, "Primary Database", "PostgreSQL 15", "System of record; encrypted at rest")
  ContainerDb(cache, "Read Cache", "Redis 7", "Cache-aside, 15-min TTL; loss = latency only")
  ContainerQueue(queue, "Import Queue", "Redis Streams", "At-least-once delivery")
}
Rel(user, spa, "HTTPS", "TLS 1.3")
Rel(spa, api, "REST / JSON")
Rel(api, db, "Tenant-scoped SQL", "SQL/TLS")
Rel(api, cache, "Read aggregates / invalidate", "RESP")
Rel(api, queue, "Enqueue import job", "RESP")
Rel(queue, worker, "Deliver job")
Rel(worker, db, "Bulk insert", "SQL/TLS")
@enduml
```

![View: Runtime (C&C)](diagrams/view-cnc-runtime-01.png)

_visually verified: yes · relative path renders on GitHub / GitLab_

## 2. Element catalog

### 2.1 Elements and their properties

| Component | Responsibility | Key properties |
|-----------|----------------|----------------|
| Web App | Render UI, call the API | stateless; no direct DB access |
| API Service | Auth, **tenant guard**, transaction/category/reporting services, Data Access | stateless, horizontally scalable; the only writer to the DB |
| Import Worker | Consume import jobs, parse CSV, bulk-insert | idempotent per job; reuses Data Access |
| Primary Database | System of record | tenant-scoped rows; encrypted at rest (`CON-4`) |
| Read Cache | Dashboard aggregates | strictly derived data; loss = latency only |
| Import Queue | Buffer import jobs | at-least-once delivery |

### 2.2 Relations and their properties

| From | Connector | To | Properties |
|------|-----------|----|-----------|
| Web App | REST/HTTPS | API Service | JSON; auth token per request |
| API Service | SQL/TLS | Primary Database | every query `user_id`-scoped via Data Access |
| API Service | RESP | Read Cache | cache-aside; write invalidates the user/month key |
| API Service | RESP (stream) | Import Queue | one job per uploaded file |
| Import Queue | RESP (stream) | Import Worker | consumer group; at-least-once |
| Import Worker | SQL/TLS | Primary Database | bulk insert; no direct client access |

### 2.3 Element interfaces

HTTP interface catalogue and events: ADD [`../add/personal-finance-tracker-Architecture.md`](../add/personal-finance-tracker-Architecture.md) §8.

### 2.4 Element behavior

Dashboard read (cache hit / miss) sequence: ADD `Architecture.md` §6.

## 3. Context diagram

External to this view: the user's browser and the email provider (notifications sent by the API
Service, omitted from the primary presentation to keep it to the runtime data paths).

## 4. Variability guide

- Import processing runs **in-process** in the API Service in local/dev (no queue/worker) and
  **out-of-process** in production; selected by config flag `IMPORTS_ASYNC`.
- Read Cache is optional: with it disabled the Dashboard Service reads straight from the DB
  (slower; used only in dev).

## 5. Rationale

- One API Service process holds the tenant guard so `SQA-1` isolation is enforced on every
  interactive path in a single auditable place ([`rationale.md`](rationale.md) ADR-2).
- Cache-aside with a bounded TTL meets `PQA-1`'s p95 budget while keeping the cache strictly
  derived, so its failure never threatens `AQA-1` correctness ([`rationale.md`](rationale.md) ADR-1).
- CSV import is pushed to a queue + worker so a large import cannot consume the request threads
  that serve interactive traffic (`PQA-2`).

---

**Navigation**: [docs README](README.md) · [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md)


---

# View: Deployment (Allocation / deployment)

- **Viewtype**: Allocation
- **Style**: deployment
- **Stakeholders / concerns addressed**: operations (what runs where, how it survives failure —
  `AQA-1`), finance (`BG-4` cost), security (network boundaries, `CON-4`)
- **Date**: 2026-09-06

## 1. Primary presentation

```plantuml
@startuml view-allocation-deployment-01
!include ../../../../skills/sei-diagrams/assets/c4/C4_Deployment.puml
!include ../../../../skills/sei-diagrams/assets/c4/sei-c4-palette.puml
LAYOUT_TOP_DOWN()
title Deployment view — Personal Finance Tracker (eu-west-1, 2 AZs)
Deployment_Node(cloud, "Managed cloud", "eu-west-1 · 2 availability zones") {
  Deployment_Node(edge, "CDN + static hosting", "Global edge cache; TLS termination") {
    Container(spa, "Web App bundle", "React 18 build", "Static assets")
  }
  Deployment_Node(platform, "Container platform", "Autoscaling, multi-AZ") {
    Container(api, "API Service", "Node.js 20", "2+ replicas across AZs")
    Container(worker, "Import Worker", "Node.js 20", "1+ replica; scales on queue depth")
  }
  Deployment_Node(datatier, "Managed data tier", "Multi-AZ") {
    ContainerDb(db, "PostgreSQL 15", "Primary + standby", "Automated failover 35-70 s (vendor)")
    ContainerDb(redis, "Redis 7", "Primary + replica", "Cache + streams; derived data")
  }
}
Rel(spa, api, "Served to browser", "HTTPS")
Rel(api, db, "Reads / writes", "SQL/TLS")
Rel(api, redis, "Cache + enqueue", "RESP/TLS")
Rel(worker, redis, "Consume jobs", "RESP/TLS")
Rel(worker, db, "Bulk insert", "SQL/TLS")
@enduml
```

![View: Deployment](diagrams/view-allocation-deployment-01.png)

_visually verified: yes · relative path renders on GitHub / GitLab_

## 2. Element catalog

### 2.1 Elements and their properties

| Environment element | Hosts | Properties |
|---------------------|-------|------------|
| CDN + static hosting | Web App bundle | global edge cache; TLS termination |
| Container platform | API Service, Import Worker | autoscaling; replicas pinned across 2 AZs; rolling deploys |
| Managed data tier — PostgreSQL | Primary Database | primary + standby in separate AZs; automated failover 35–70 s (vendor); PITR backups |
| Managed data tier — Redis | Read Cache + Import Queue | primary + replica; not a system of record |

### 2.2 Relations and their properties

| From | Relation | To | Properties |
|------|----------|----|-----------|
| API Service replica | allocated-to | Container platform (AZ-a / AZ-b) | ≥ 1 replica per AZ |
| Import Worker | allocated-to | Container platform | scales on queue depth |
| Primary Database | allocated-to | data tier, AZ-a (primary), AZ-b (standby) | sync or near-sync replication |
| Redis | allocated-to | data tier, AZ-a (primary), AZ-b (replica) | async replication acceptable (derived data) |

### 2.3 Element interfaces

Network: only the CDN and the container platform's load balancer are public; the data tier is
private-subnet only. All hops use TLS (`CON-4`).

### 2.4 Element behavior

On an AZ-a loss: the load balancer drains AZ-a API replicas, the DB standby in AZ-b is promoted,
Redis fails over to its AZ-b replica; the API is stateless so no session loss.

## 3. Context diagram

Outside this view: the user's device/network and the email provider's infrastructure.

## 4. Variability guide

- **Region**: single region at launch; a second region is a future option — no region-partitioning
  seam exists yet (ATAM risk `R-6`).
- **Tier sizing**: instance classes and replica counts are environment config; the topology is fixed.
- **Redis split**: cache and streams share one Redis at launch; they can be split onto two
  instances by config without code change.

## 5. Rationale

- Stateless API replicas across two AZs plus a managed primary/standby database with automated
  failover is the cheapest topology that meets `AQA-1` (recover < 60 s, ≥ 99.5 %/mo) on the
  low-cost managed tiers required by `CON-3` and within `BG-4`'s budget ([`rationale.md`](rationale.md) ADR-3).
- Putting only the CDN and load balancer in public subnets shrinks the attack surface for
  `SQA-1` / `CON-4`.
- The measured failover time is not yet verified against the 60 s target — tracked as ATAM risk
  `R-3`; a game-day test is scheduled before launch.

---

**Navigation**: [docs README](README.md) · [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md)


---

# Mapping between views — Personal Finance Tracker

Shows how elements correspond across the Module, C&C, and Allocation views, so a reader can move
between them and so internal consistency is demonstrable.

## Module → runtime component (C&C)

| Module (`view-module-decomposition.md`) | Runtime component (`view-cnc-runtime.md`) | Notes |
|-----------------------------------------|-------------------------------------------|-------|
| `http` | API Service — HTTP Router | 1:1 |
| `security` | API Service — Tenant Guard | 1:1; the `SQA-1` control |
| `transactions`, `categories` | API Service — Transaction Service | grouped at runtime |
| `reporting` | API Service — Dashboard Service | 1:1 |
| `imports` | Import Worker (+ API Service enqueue path) | one module, two runtime homes |
| `persistence` | API Service / Import Worker — Data Access | shared library, instantiated in both |
| `platform` | cross-cutting; not a distinct component | logging/audit/config used everywhere |

## Runtime component (C&C) → deployment node (Allocation)

| Runtime component | Deployment node (`view-allocation-deployment.md`) | Notes |
|-------------------|--------------------------------------------------|-------|
| Web App | CDN + static hosting | static build |
| API Service (2+ replicas) | Container platform, multi-AZ | stateless |
| Import Worker | Container platform, multi-AZ | queue consumer |
| Primary Database | Managed data tier — PostgreSQL primary + standby | automated failover |
| Read Cache | Managed data tier — Redis primary + replica | derived data only |
| Import Queue | Managed data tier — Redis Streams | on the same Redis or a sibling |

## Driver → element realising it

| Driver | Realised by |
|--------|-------------|
| `SQA-1` | `security` module → Tenant Guard component; append-only audit log in `platform` |
| `AQA-1` | Allocation: stateless API replicas across 2 AZs + managed primary/standby DB failover |
| `PQA-1` | `reporting` module + Read Cache component (cache-aside, 15-min TTL) |
| `MQA-1` | `reporting` module report-type registry; forbidden domain-to-domain dependencies |
| `UC-3` | `imports` module → Import Worker component → Import Queue |

---

**Navigation**: [docs README](README.md) · [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md)


---

# Rationale — Personal Finance Tracker

Cross-cutting architecture rationale and the ADR log. Per-view rationale lives in each view packet.

## ADR-1: Cache-aside read model for the dashboard

- **Status**: accepted · 2026-09-06
- **Drivers addressed**: `PQA-1`, `AQA-1`, `MQA-1`

**Context.** The dashboard (`UC-2`) must be interactive in < 1.5 s at p95 with 500 concurrent
users. Computing every load from the transaction store does not meet the budget.

**Decision.** We will precompute per-user, per-month aggregates in a Redis cache using the
cache-aside pattern with a 15-minute TTL; a transaction write invalidates the affected key.

**Rationale.** Meets `PQA-1`; keeps the cache strictly derived so its loss degrades latency but
not correctness (`AQA-1`); aggregate logic stays in the `reporting` module, so new report types
(`MQA-1`) do not require schema changes.

**Alternatives considered.** Materialised views (slower iteration for `MQA-1`); CDN edge caching
(per-user private data — unsafe); no cache (fails `PQA-1`).

**Consequences.** Dashboard data can be up to 15 minutes stale on the read path (tradeoff point
`T-1` in the ATAM). Cache warm-up cost on cold start.

## ADR-2: Single tenant-guard choke point

- **Status**: accepted · 2026-09-06
- **Drivers addressed**: `SQA-1`, `CON-4`, `BG-2`

**Context.** `SQA-1` requires that no user can read another user's data, with every attempt
logged, and `BG-2` requires passing a SOC 2 audit.

**Decision.** All interactive requests pass through one `security`-module tenant guard that
injects `user_id` scoping into every query via the `persistence` module; denied access is written
to an append-only audit log.

**Rationale.** One auditable place to enforce and demonstrate isolation; per-endpoint checks were
rejected as too easy to omit.

**Alternatives considered.** PostgreSQL row-level security (viable later; team unfamiliarity now);
per-endpoint authorization (miss-a-check risk).

**Consequences.** The Import Worker currently bypasses the guard (ATAM risk `R-1`); a follow-up
routes it through the same Data Access scoping. Audit-log tamper-evidence still to be decided
(`R-2`).

## ADR-3: Stateless API replicas + managed multi-AZ database

- **Status**: accepted · 2026-09-06
- **Drivers addressed**: `AQA-1`, `CON-3`, `CON-5`, `BG-4`

**Context.** `AQA-1` requires surviving a single-AZ failure with recovery < 60 s at ≥ 99.5 %/mo,
on low-cost managed tiers (`CON-3`) using PostgreSQL (`CON-5`) and within budget (`BG-4`).

**Decision.** Run the API as stateless replicas pinned across two AZs behind the platform load
balancer; use a managed PostgreSQL primary/standby with automated failover; Redis primary/replica.

**Rationale.** Cheapest topology meeting the recovery target without a self-managed HA setup the
one-person team cannot operate (`CON-2`).

**Alternatives considered.** Self-managed HA (operational load — `CON-2`); single instance (fails
`AQA-1`); multi-region (cost — `BG-4`, and premature).

**Consequences.** Measured failover time not yet verified against 60 s (`R-3`); no rollback
runbook yet (`R-4`); single-region only, no data-residency seam (`R-6`).

---

**Navigation**: [docs README](README.md) · [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md)


---

# Directory — Personal Finance Tracker

## Index — where elements are defined

| Element | Defined in | Also appears in |
|---------|-----------|-----------------|
| `security` module / Tenant Guard | `view-module-decomposition.md` §2 | `view-cnc-runtime.md`, [`rationale.md`](rationale.md) ADR-2 |
| `reporting` module / Dashboard Service | `view-module-decomposition.md` §2 | `view-cnc-runtime.md`, [`rationale.md`](rationale.md) ADR-1 |
| Read Cache | `view-cnc-runtime.md` §2 | `view-allocation-deployment.md`, [`rationale.md`](rationale.md) ADR-1 |
| Import Queue / Import Worker | `view-cnc-runtime.md` §2 | `view-allocation-deployment.md`, `mapping-between-views.md` |
| Primary Database | `view-cnc-runtime.md` §2 | `view-allocation-deployment.md`, ADD `Architecture.md` §7 |

## Glossary

| Term | Meaning |
|------|---------|
| Tenant guard | Middleware that forces `user_id` scoping onto every query; the `SQA-1` control |
| Cache-aside | Read pattern: check cache; on miss, load from source and populate the cache |
| Derived data | Data that can be recomputed from the system of record; safe to lose |
| System of record | The authoritative store for a piece of data (here: PostgreSQL) |
| Six-part scenario | The SEI quality attribute scenario form: source, stimulus, artifact, environment, response, response measure |

## Acronyms

| Acronym | Expansion |
|---------|-----------|
| ADD | Attribute-Driven Design |
| ATAM | Architecture Tradeoff Analysis Method |
| AZ | Availability Zone |
| C&C | Component-and-Connector |
| PWA | Progressive Web App |
| QAW | Quality Attribute Workshop |
| RPO / RTO | Recovery Point / Time Objective |
| TTL | Time To Live |
| V&B | Views and Beyond |

## Driver ID prefixes used here

`BG-` business goal · `UC-` use case · `CON-` constraint · `AQA-` availability · `SQA-` security
· `PQA-` performance · `MQA-` modifiability · `UQA-` usability · `RQA-` reliability(other).

---

**Navigation**: [docs README](README.md) · [example root](../README.md) · [drivers](../drivers/README.md) · [ADD architecture](../add/personal-finance-tracker-Architecture.md)


---

# Change log — architecture description

Revision history of this Views-and-Beyond documentation package (not of the system).

| Date | Change |
|------|--------|
| 2026-09-06 | Initial description: system overview, one view packet per viewtype (Module decomposition, C&C runtime, Allocation deployment), mapping between views, rationale + ADR-1..3, directory. |

---

**Navigation**: [docs README](README.md) · [example root](../README.md)

