# Reference — Architecture & design patterns (by quality attribute served)

A **pattern** packages several tactics into a proven, named structure with known consequences.
ADD Step 4 evaluates 2–4 candidate patterns per driver cluster; ATAM Step 4 catalogs the
patterns already in use. Each entry: **intent · primary quality served · principal tradeoff**.

## Availability / reliability

| Pattern | Intent | Principal tradeoff |
|---------|--------|--------------------|
| Active redundancy (hot spare) | All redundant nodes process every request; a failed one is dropped | Cost; state must stay in sync |
| Passive redundancy (warm spare) | Primary processes; standbys get periodic state updates; promote on failure | Failover window; possible lost updates since last sync |
| Cold spare | Standby is started only on failure | Long recovery time |
| Circuit breaker | Stop calling a failing dependency; fail fast; probe to recover | Tuning thresholds; risk of flapping |
| Health check + load-balancer eviction | Detect an unhealthy instance and stop routing to it | Detection lag; false positives drain capacity |
| Bulkhead | Isolate resource pools so one overloaded path cannot starve others | Lower peak utilisation; more pools to size |

## Performance / scalability

| Pattern | Intent | Principal tradeoff |
|---------|--------|--------------------|
| Load balancer | Spread requests across interchangeable workers | Session affinity vs. even spread; the LB is a hop and a dependency |
| Cache-aside | Serve reads from a cache; on miss, load from source and populate | Staleness bounded by TTL/invalidation; cache-stampede risk |
| Read replica / CQRS | Separate read model from write model; scale reads independently | Replication lag → read-your-writes anomalies |
| Sharding / partitioning | Split data by key so each node owns a slice | Cross-shard queries and transactions are expensive; rebalancing |
| Asynchronous queue + worker | Move slow / bursty work off the request path | Eventual completion; at-least-once → idempotency required |
| Map-reduce / fan-out-fan-in | Parallelise a large computation over data partitions | Coordination overhead; stragglers |

## Modifiability / integrability

| Pattern | Intent | Principal tradeoff |
|---------|--------|--------------------|
| Layers | Allowed-to-use is one-directional between layers | Layer-skipping temptation; extra indirection |
| Ports & adapters (hexagonal) | Domain core depends only on interfaces; adapters implement them | More types; discipline to keep the core pure |
| Publish–subscribe / event-driven | Producers and consumers are decoupled through a broker | Harder to trace a flow; delivery + ordering semantics |
| Gateway / API gateway | One entry point does cross-cutting concerns (authn, routing, rate limit) | A choke point and a single point of failure to design around |
| Strangler fig | Incrementally replace a legacy system behind a routing facade | The facade and dual-write period add complexity |
| Anti-corruption layer / adapter | Wrap an external contract so its model does not leak inward | Extra translation code; a place bugs hide |

## Security

| Pattern | Intent | Principal tradeoff |
|---------|--------|--------------------|
| Single choke point / intercepting validator | One place authenticates, authorizes, and scopes every request | That component's correctness is critical; it must not be bypassable |
| DMZ / network segmentation | Only edge components are reachable from outside; data tier is private | Operational complexity; east-west traffic still needs controls |
| Least privilege + short-lived credentials | Each component holds only the access it needs, briefly | Credential-rotation machinery; more moving parts |
| Append-only audit log | Every security-relevant event is recorded immutably | Storage growth; the log itself is an asset to protect |

## Deployability / operability

| Pattern | Intent | Principal tradeoff |
|---------|--------|--------------------|
| Microservices | Independently deployable services around business capabilities | Distributed-system cost: network, data consistency, observability |
| Sidecar | Put cross-cutting infrastructure (proxy, logging) beside each service | Resource overhead per instance; lifecycle coupling |
| Service mesh | Move traffic management / mTLS / telemetry into the platform | Control-plane complexity; another thing to operate |
| Blue/green & canary | Shift traffic gradually to a new version; roll back fast | Needs versioned interfaces and enough capacity for two versions |
| Feature toggle | Decouple deploy from release; turn behaviour on per cohort | Toggle debt; combinatorial test surface |

## Reference architectures (whole-system starting points)

- **3-tier web application** — web / application / data tiers; the default for CRUD-heavy SaaS.
- **Event-driven / streaming** — ingest → process → serve, with a durable log; good for
  high-volume, decoupled producers/consumers.
- **Pipe-and-filter / batch** — staged transformations over bounded data; good for ETL.
- **Serverless / FaaS** — event-triggered functions + managed services; scales to zero, cedes
  control of runtime and cold-start behaviour.
- **Modular monolith** — one deployable, strict internal module boundaries; the cheapest
  structure that still protects modifiability when the team is small (defers the
  microservices tax).
