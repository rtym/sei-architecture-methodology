# Reference — Brownfield intake (reverse-engineering the drivers)

The SEI activities all start from **drivers**. On a greenfield system those come from people. On
an **existing** system the code, its configuration and its history already answer many of the
questions — and answer some of them better than memory does. This note is the procedure for
extracting a *first draft* of the drivers and the as-built views from a repository, so a
`/drivers` or `/atam` engagement opens with something concrete to correct rather than a blank page.

Used by the `sei-architecture` router (brownfield intake), by `/drivers` Step 1 when the project
has a codebase, and by `/atam` when the architecture is undocumented.

## The one rule that matters

**Code shows you the architecture, never the requirement.** A cache in the read path is evidence
that someone cared about latency; it is *not* a performance scenario, and it certainly does not
tell you the number. Every driver derived here is a **hypothesis to confirm with a stakeholder**,
and must be marked as such until they do. Writing `p95 < 1.5 s` because the cache TTL is 15
minutes is inventing a requirement, which is worse than having none.

Corollaries:

- A tactic found in the code is a *candidate* answer to an unrecorded ASR. Record the tactic as
  evidence and raise the question, do not back-fill the scenario.
- An **absent** tactic (no retry, no audit log, no health check) is a **finding** for the
  evaluation, not a driver. Keep those in a separate list.
- What the code does and what the team believes it does often differ. Record both; the gap is
  usually the most valuable thing the intake produces.

## What to read, in order

Stop at the first few that exist; this is a reconnaissance pass, not a code review.

| # | Source | What it yields |
|---|--------|----------------|
| 1 | `README`, `docs/`, wiki exports, existing ADRs (`adr/`, `docs/adr/`, `decisions/`) | stated purpose, decisions already recorded — never re-derive an ADR that exists, link it |
| 2 | Build and dependency manifests (`pom.xml`, `build.gradle`, `package.json`, `go.mod`, `pyproject.toml`, `*.csproj`, `Cargo.toml`) | languages, frameworks, the **reference architecture** in use, third-party components, licence constraints |
| 3 | Top-level source layout | candidate **modules** — the seed of the module decomposition view |
| 4 | Entry points (`main`, HTTP servers, message consumers, schedulers, CLIs, lambda handlers) | candidate **containers** and the architecturally significant **use cases** each serves |
| 5 | Outbound integrations (HTTP/SDK clients, queue and topic names, DB drivers, SFTP/SMTP, file drops) | **external systems** for the context diagram; integrability concerns |
| 6 | Persistence (migrations, schema, ORM models, cache clients) | **datastores**, data ownership, the shared-data structure |
| 7 | Deployment config (`Dockerfile`, compose, Kubernetes manifests, Helm, Terraform, CI/CD workflows) | the **allocation view**: nodes, replicas, zones, environments, deploy strategy |
| 8 | Runtime configuration (env vars, config files, feature flags) | the **variability guide**; where binding is deferred |
| 9 | Cross-cutting code (auth filters, tenancy guards, logging, metrics, retries, circuit breakers, caches) | **tactics already present** — evidence of which quality attributes were designed for |
| 10 | Tests and their coverage | testability; which behaviour is actually pinned |
| 11 | Observability config (dashboards, alert rules, SLOs) | the **only place a real response measure is likely to be written down** — harvest it |
| 12 | Git history: churn hotspots, `CODEOWNERS`, commit cadence | architecture debt candidates, the work-assignment view, team structure |

## What to produce

A single intake note (`architecture/brownfield-intake.md`, deleted or folded in once `/drivers`
has run), with every claim carrying its evidence:

| Claim | Evidence | Confidence |
|-------|----------|------------|
| The read path caches monthly aggregates for 15 min | `src/reporting/cache.ts:42` | high — read from code |
| Availability target is 99.5 %/month | `ops/alerts.yaml:17` (page threshold) | medium — an alert threshold is not a contract |
| Cross-tenant isolation is enforced in one middleware | `src/security/tenantGuard.ts` | high |

Then draft, each marked **derived — confirm**:

1. **Business goals** — usually *not* derivable. Take what the README and product docs assert;
   otherwise leave `BG-?` open and ask. Do not invent them from technical choices.
2. **Use cases** (`UC-`) — from entry points and endpoints, filtered to the architecturally
   significant ones (crosses a trust or process boundary, dominates load, drives an integration).
3. **Constraints** (`CON-`) — mandated platform, language, datastore, licences, deployment target,
   regulatory hooks visible in the code (audit logs, retention, residency).
4. **Quality attribute scenarios** (`<ATTR>QA-`) — one per tactic family found, with the six parts
   drafted from the code path and the **response measure left blank or quoted from observability
   config**. Mark every one `Status: open` and `derived — confirm`.
5. **Architectural concerns** (`AC-`) — team size and skills, debt hotspots, version pins, anything
   the history shows hurting.
6. **As-built views** — a container view (C4 L2) and a module decomposition, both drawn from what
   is actually there, through the `sei-diagrams` skill and visually verified like any other diagram.
7. **Gap list** — as-built versus as-intended, and the absent tactics. This feeds the evaluation
   directly and should not be mixed into the drivers.

## Hand-off

Intake note → `/drivers` (it becomes the register, with the hypotheses confirmed or dropped in a
review with the stakeholders) → `/quality-attributes` to put numbers on the scenarios → `/atam` to
evaluate, with the gap list as a starting scenario set → targeted `/add` iterations for the risk
themes. The as-built views are the first draft of the Views-and-Beyond package.

## Scope control

An intake is bounded reconnaissance: enough to open the conversation, not a full reverse-engineering.
If the repository is large, restrict to the deployable(s) under discussion and say so in the note.
Reading everything before talking to anyone is the failure mode this procedure is meant to avoid.
