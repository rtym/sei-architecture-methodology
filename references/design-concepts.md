# Reference — Design concepts: the building blocks of architecture design

ADD Step 4 turns drivers into structure by selecting and combining **design concepts**. "A good
engineer makes a design that works with as few original ideas as possible" — most of the time
you identify, adapt, and combine existing solutions rather than invent.

## The five categories (coarse → fine)

| Category | What it is | When it enters the design |
|----------|------------|---------------------------|
| **Reference architectures** | a domain-proven blueprint for the whole system (3-tier web app, microservices, event-driven/streaming, pipe-and-filter/batch, serverless, modular monolith, big-data lambda, service mesh) | earliest iterations — "what is the overall structure?" |
| **Deployment patterns** | how software is packaged and rolled out (blue/green, canary, rolling, sidecar, service mesh, feature toggle) | early — alongside the reference architecture |
| **Architecture & design patterns** | a proven arrangement of a few elements solving a recurring problem (layers, ports & adapters, CQRS, saga, broker, publish-subscribe, gateway, circuit breaker, bulkhead, cache-aside, strangler fig, anti-corruption layer) | throughout — see `references/architecture-patterns.md` |
| **Tactics** | a single design decision affecting one quality-attribute response (the level below patterns; a pattern usually bundles several) | throughout — full lists in `references/tactics-catalog.md` |
| **Externally developed components** | frameworks, platforms, middleware, cloud services, SaaS, libraries you adopt rather than build | early for full-stack frameworks tied to the reference architecture; later for specific needs |

To address one driver you often **combine** categories — e.g. a security driver may take a
security pattern **and** a tactic **and** a framework.

## Identifying candidates

Use a combination of:
- **best-practice catalogs** — patterns, tactic taxonomies, framework docs (many alternatives,
  vetting costs time; author bias unknown);
- **your own experience** — fast and confident for a familiar system type; risks the
  "everything looks like a nail" trap;
- **peers** — a short brainstorm brings in experience you lack.

## Selecting among candidates

1. Put the alternatives in a **pros/cons table** keyed to the iteration's drivers, and choose.
2. For a high-stakes or contested choice, add a deeper analysis:
   - **SWOT** — strengths / weaknesses / opportunities / threats per candidate;
   - **CBAM** (cost/benefit analysis method) — for each candidate strategy, estimate the utility
     it adds (as levels of quality-attribute response), its cost, and its schedule; rank by ROI.
     Designed to run after ATAM, but usable during design.
3. Record the choice **and** the discarded alternatives with the reason, citing driver IDs
   (ADR-style; ADD `Architecture.md` §9).

## Design concepts by quality attribute (starting points)

- **Performance** — load balancer, cache-aside, read replica / CQRS, async queue + worker,
  sharding, connection pooling, CDN; tactics: manage work requests, introduce concurrency,
  maintain multiple copies of data/computation, bound queues, schedule resources.
- **Availability** — active/passive redundancy, spare, circuit breaker, health-check + LB
  eviction, bulkhead, managed multi-AZ data tier; tactics: detect / recover / prevent faults.
- **Modifiability** — layers, ports & adapters, publish-subscribe, plug-in / microkernel,
  strangler fig; tactics: split module, increase cohesion, reduce coupling, defer binding.
- **Integrability** — gateway / API gateway, anti-corruption layer, adapter, message broker,
  published contracts + schema registry; tactics: encapsulate, use an intermediary, adhere to
  standards, tailor interface.
- **Security** — single choke point / intercepting validator, DMZ / segmentation, least
  privilege + short-lived credentials, append-only audit log, secrets manager; tactics: detect
  / resist / react to / recover from attacks.
- **Deployability** — microservices, sidecar, service mesh, blue/green + canary, feature
  toggle, containers + orchestration; tactics: manage the pipeline, manage the deployed system.
- **Testability** — dependency injection / seams, contract tests, record-playback, sandbox,
  test doubles; tactics: control and observe state, limit complexity.
