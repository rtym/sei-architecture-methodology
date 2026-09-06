# Reference — Runtime environments: virtualization, the cloud, mobile

How the execution environment shapes the architecture — mainly the **allocation / deployment
view** and the **availability, performance, scalability, deployability, and energy** scenarios.

## Virtualization — the spectrum of isolation vs. sharing

| Mechanism | Isolation | Start-up | State | Architectural implication |
|-----------|-----------|----------|-------|---------------------------|
| **Bare metal / shared host** | none (processes) | instant | ambient | contention on shared resources must be budgeted (rule S8) |
| **Virtual machine** | full OS | tens of seconds | in the VM image / attached volumes | heavy; good for strong isolation and lift-and-shift |
| **Container** | process + namespaces; shared kernel | ~1 s | **externalise it** — containers are cattle, replaced not repaired | the unit of deployment and scaling; drives "stateless service + managed data tier" |
| **Pod** (co-scheduled containers) | as container | ~1 s | as container | the sidecar pattern lives here (proxy, log shipper beside the app) |
| **Serverless / FaaS** | per-invocation | cold start (100 ms–seconds) | **none** — pass state in the event or an external store | scales to zero; cedes control of the runtime; cold-start latency is a performance scenario |

Consequences for the architecture:
- Make every process **relocatable** (rule S6). Do not pin behaviour to a host.
- **Externalise session and application state** so instances are interchangeable — this is what
  makes horizontal scaling and fast failover possible.
- The **container image + its declared config/secrets** is the deployable artifact; the
  deployment view shows images placed on nodes, not code on servers.

## The cloud

- **Failure is normal, not exceptional.** Any instance, zone, or managed service can disappear
  without notice. Design so that losing one is a latency event, not a correctness event:
  stateless replicas, health checks, automatic replacement, managed multi-AZ data tier with
  automated failover, and **derived data** (caches, read models) that can be recomputed.
- **Multiple instances buy both availability and performance.** N stateless replicas behind a
  load balancer survive the loss of one and absorb more load; **autoscaling** adds/removes
  replicas on a signal (CPU, queue depth, request rate). Autoscaling only works if instances are
  stateless and start fast.
- **State is the hard part.** Push it to managed stores (relational, document, key-value,
  object, queue/stream) chosen per access pattern; keep the compute tier stateless. Replication
  lag, quorum, and failover time become **sensitivity points** — measure the vendor's failover
  time against the availability scenario's target.
- **Cost tracks architecture.** Right-size instances, scale to zero where latency allows, prefer
  managed services over self-run HA on a one-person team, and keep a paid upgrade path off the
  free tier (a common constraint).
- **The deployment view** for a cloud system shows: region → availability zones → edge (CDN/WAF)
  → compute platform (autoscaling group / cluster) → managed data tier (primary + standby /
  replica) → observability, with every hop's protocol and the public/private network boundary.

## Mobile systems

Extra forces the architecture must account for, each a potential quality-attribute scenario:
- **Energy** — the battery is a first-class resource. Reduce polling, batch network calls,
  defer background work to charging/Wi-Fi, and meter consumption. (Energy efficiency scenario.)
- **Network connectivity** — intermittent, variable-bandwidth, high-latency. Design for offline
  operation: local cache/queue, optimistic UI, sync-on-reconnect, conflict resolution.
- **Resources** — constrained CPU, memory, storage; the OS may evict the app at any time.
- **Life cycle** — the OS controls foreground/background/terminated transitions; persist state
  aggressively so a killed app resumes cleanly.
- **Sensors and actuators** — the device is a source of stimuli (GPS, camera, accelerometer) and
  a target of responses; treat them as external systems with their own failure modes.
