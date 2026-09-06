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
