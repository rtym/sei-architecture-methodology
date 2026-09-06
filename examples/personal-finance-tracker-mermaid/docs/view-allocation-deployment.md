# View: Deployment (Allocation / deployment)

- **Viewtype**: Allocation
- **Style**: deployment
- **Stakeholders / concerns addressed**: operations (what runs where, how it survives failure —
  `AQA-1`), finance (`BG-4` cost), security (network boundaries, `CON-4`)
- **Date**: 2026-09-06

## 1. Primary presentation

```mermaid
flowchart TB
  %% Deployment view — Personal Finance Tracker (eu-west-1, 2 AZs)
  subgraph cloud["Managed cloud — eu-west-1 (2 availability zones)"]
    subgraph edge["CDN + static hosting"]
      spa["Web App bundle<br/><i>React 18 build</i>"]
    end
    subgraph platform["Container platform (autoscaling, multi-AZ)"]
      api["API Service<br/><i>Node.js 20 · 2+ replicas across AZs</i>"]
      worker["Import Worker<br/><i>Node.js 20 · 1+ replica</i>"]
    end
    subgraph datatier["Managed data tier (multi-AZ)"]
      db[("PostgreSQL 15<br/><i>primary + standby · automated failover</i>")]
      redis[("Redis 7<br/><i>primary + replica · cache + streams</i>")]
    end
  end
  spa -->|"served to browser (HTTPS)"| api
  api -->|"SQL / TLS"| db
  api -->|"RESP / TLS"| redis
  worker -->|"RESP / TLS"| redis
  worker -->|"SQL / TLS"| db
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef datastore fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class spa,api,worker internal
  class db,redis datastore
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
