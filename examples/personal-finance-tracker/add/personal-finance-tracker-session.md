# ADD Session: Personal Finance Tracker

- **Date**: 2026-09-06
- **Purpose**: Web app for individuals to track income, expenses and savings goals.
- **Status**: active
- **Architecture**: `personal-finance-tracker-Architecture.md`
- **Drivers imported from**: `../drivers.md`

## Drivers

### Quality Attribute Scenarios
IDs are attribute-prefixed (see `../drivers.md`).

| ID | QA (ISO 25010) | Source | Stimulus | Artifact | Environment | Response | Measure | Priority (Imp,Diff) |
|----|----------------|--------|----------|----------|-------------|----------|---------|---------------------|
| SQA-1 | Security / confidentiality | Authenticated attacker | Requests another user's data | API + store | Normal | Reject + log | 0 reads; 100 % logged | (H,H) |
| AQA-1 | Reliability / availability | Infra | Single-AZ failure | Whole system | Production | Auto-recovers | ≥ 99.5 %/mo; < 60 s | (H,H) |
| PQA-1 | Performance efficiency / time behaviour | User | 500 concurrent dashboard loads | Dashboard read path | Normal | Renders fully | < 1.5 s @ p95 | (H,M) |
| MQA-1 | Maintainability / modifiability | Developer | Add a report type | Business logic | Sprint | Localised change | ≤ 1 person-day; 0 regressions | (M,M) |

### Primary functional requirements (use cases)

| ID | Use case name | Primary actor | Architectural significance | Priority |
|----|---------------|---------------|---------------------------|----------|
| UC-1 | Record a transaction | Registered user | write load + latency + modifiability hot spot | high |
| UC-2 | View the monthly dashboard | Registered user | performance-critical read path | high |

### Constraints

| ID | Type | Description |
|----|------|-------------|
| CON-2 | business | One engineer, 3-month MVP |
| CON-4 | regulatory | Encryption in transit and at rest |
| CON-5 | technical | PostgreSQL primary datastore |

### Architectural Concerns

| ID | Concern |
|----|---------|
| AC-1 | Keep the SOC 2 surface small — few external dependencies |
| AC-2 | Dashboard iteration speed must stay high (weekly report types) |

## Iteration Plan

| Iteration | Goal | Drivers |
|-----------|------|---------|
| 1 | Establish overall structure, security choke point, availability topology | SQA-1, AQA-1, MQA-1, UC-1, CON-2, CON-4, CON-5, AC-1 |
| 2 | Dashboard read path meets the latency budget | PQA-1, UC-2, AC-2 |
| 3 | Bulk CSV import without hurting interactive latency | (deferred — PQA-2, UC-3) |

## Iteration 1 — Establish overall structure, security, availability

- **Drivers selected**: SQA-1, AQA-1, MQA-1, UC-1, CON-4, CON-5
- **Element(s) refined**: whole system

### Step 2 — Iteration goal
**Goal:** Choose a reference architecture and a security/availability topology that satisfies the two (H,H) scenarios within the one-engineer constraint.

| Driver | Importance | Difficulty |
|--------|------------|------------|
| SQA-1 | H | H |
| AQA-1 | H | H |
| MQA-1 | M | M |
| UC-1 | H | M |

### Step 3 — Element(s) chosen
The whole system (greenfield, iteration 1).

### Step 4 — Design concepts

| Design concept | Decision | Rationale (cite driver IDs) | Alternatives discarded |
|----------------|----------|-----------------------------|------------------------|
| 3-tier web app (SPA + single API + relational DB) | chosen | Minimises moving parts under CON-2; one API means one place to enforce SQA-1; supports MQA-1 via a modular monolith | Microservices (CON-2 time), serverless functions (cold-start vs PQA-1, harder SOC 2 story) |
| Tenant-scoping middleware (single guard) | chosen | SQA-1 needs one auditable choke point rather than per-endpoint checks | Row-level security in PostgreSQL (viable later; team unfamiliarity now) |
| Managed PostgreSQL, multi-AZ primary/standby, automated failover | chosen | AQA-1 recovery target; CON-5 mandate; available on CON-3 tiers | Self-managed HA (CON-2), single instance (fails AQA-1) |
| Stateless API replicas across 2 AZs | chosen | AQA-1; enables horizontal scale for PQA-1 later | Sticky sessions (limits failover) |

### Step 5 — Instantiation, responsibilities, interfaces

| Instantiation decision | Responsibility |
|------------------------|----------------|
| Web App (React PWA) | UI on mobile browsers (CON-1) |
| API Service (Fastify) | Auth, tenant guard, transaction + dashboard services, data access |
| Tenant Guard middleware | Inject `user_id` scoping into every query; log denied access (SQA-1) |
| Primary Database (PostgreSQL) | System of record; encrypted at rest (CON-4) |

| Element | Provided interface | Required interface | Protocol |
|---------|-------------------|-------------------|----------|
| API Service | `POST /transactions`, `GET /dashboard` | PostgreSQL | REST / HTTPS; SQL / TLS |
| Data Access | `query(userId, spec)` | PostgreSQL | in-process; SQL / TLS |

### Step 6 — Views and design decisions
Updated Architecture.md: §2 Context, §3 Drivers, §4 Container, §5 Component (API Service), §7 Deployment, §8 Interfaces, §9 Decisions.

| Decision | Rationale (cite driver IDs) | Alternatives discarded |
|----------|-----------------------------|------------------------|
| Single API owns all writes + tenant guard | SQA-1 choke point; CON-2 simplicity | per-service checks |
| Managed multi-AZ PostgreSQL with failover | AQA-1; CON-5 | self-managed HA; single instance |

### Step 7 — Analysis

| Driver | Achieved? | Notes |
|--------|-----------|-------|
| SQA-1 | partially | Structural guard in place; needs pen-test + audit-log alerting (iteration 1b) |
| AQA-1 | yes | Multi-AZ managed data tier + stateless replicas meet the recovery target |
| MQA-1 | partially | Modular monolith supports it; report-type extension point designed in iteration 2 |
| UC-1 | yes | Write path defined end to end |

- **Iteration goal achieved:** partially
- **Remaining drivers/concerns:** SQA-1 hardening (alerting, pen-test); PQA-1, UC-2 (iteration 2); AC-2 extension point (iteration 2)
