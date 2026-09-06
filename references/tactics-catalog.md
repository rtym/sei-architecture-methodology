# Reference — Architectural tactics catalog

A **tactic** is a design decision that influences a single quality-attribute response. Tactics
are the fine-grained building blocks below patterns and reference architectures. ADD Step 4
picks tactics for the iteration's drivers; ATAM Step 6 walks the **tactics-based questionnaire**
for each attribute to find risks.

Format below: **tactic category → named tactics** (one line each). Use the questionnaire form
"Is <tactic> used? Where? What is the risk if it is not?" when analysing an architecture.

---

## Availability

Goal: keep faults from becoming failures, or bound the effect and enable repair.

- **Detect faults**: monitor · ping/echo · heartbeat · timestamp · condition monitoring ·
  sanity checking · voting (replication / functional redundancy / analytic redundancy) ·
  exception detection · self-test.
- **Recover — preparation & repair**: redundant spare (active / passive / cold) · exception
  handling · rollback · software upgrade · retry · ignore faulty behaviour · graceful
  degradation · reconfiguration.
- **Recover — reintroduction**: shadow · state resynchronization · escalating restart ·
  non-stop forwarding.
- **Prevent faults**: removal from service · transactions · predictive model · exception
  prevention · increase competence set.

**Questionnaire cues**: How is each fault class detected, and how fast? What is the failover
mechanism and its measured time? Is there a spare, and is it hot/warm/cold? Is recovered state
consistent? Is there a runbook / automation for rollback?

## Deployability

Goal: get a new version into production with control, speed, and low blast radius.

- **Manage deployment pipeline**: scale rollouts (canary, rolling, blue/green) · roll back ·
  script deployment commands.
- **Manage deployed system**: manage service interactions (versioned interfaces, backward
  compatibility) · package dependencies (containers, images) · feature toggles.

**Questionnaire cues**: Can a deploy be partial (canary)? Is rollback automated and bounded?
Are interfaces versioned so a mixed-version fleet is safe? How is a bad deploy detected?

## Modifiability

Goal: make an expected change with low cost and low ripple.

- **Reduce the size of a module**: split module.
- **Increase cohesion**: increase semantic coherence.
- **Reduce coupling**: encapsulate · use an intermediary · restrict dependencies · refactor ·
  abstract common services.
- **Defer binding**: config-time, build-time, deploy-time, startup-time, runtime binding
  (parameters, feature flags, plug-ins, publish-subscribe, discovery).

**Questionnaire cues**: For each anticipated change, which modules are touched? Is the change
localised behind an interface? Where is binding fixed and could it be deferred?

## Performance

Goal: meet a latency / throughput / deadline target under a given load.

- **Control resource demand**: manage work requests (bound arrival rate, sampling) · prioritize
  events · reduce overhead · bound execution times · increase efficiency of resource use ·
  manage sampling rate.
- **Manage resources**: increase resources · introduce concurrency · maintain multiple copies
  of computations (caching) · maintain multiple copies of data (replication) · bound queue
  sizes · schedule resources (FIFO, fixed-priority, dynamic-priority).

**Questionnaire cues**: What is the arrival pattern and the contention point? Is there a cache,
and what is its hit ratio and staleness bound? Where is the concurrency, and what is the queue
policy and bound? What is the measured p95/p99, not the average?

## Security

Goal: resist, detect, and recover from attacks on confidentiality, integrity, availability.

- **Detect attacks**: detect intrusion · detect service denial · verify message integrity ·
  detect message delay.
- **Resist attacks**: identify actors · authenticate actors · authorize actors · limit access
  (firewalls, DMZ, least privilege) · limit exposure (minimise attack surface) · encrypt data ·
  separate entities (physical / virtual / air-gap) · change default settings · validate input.
- **React to attacks**: revoke access · lock computer · inform actors.
- **Recover from attacks**: maintain audit trail · restore (see Availability tactics).

**Questionnaire cues**: Is there one auditable choke point for authz? Is every channel
encrypted? Is the audit log append-only / tamper-evident? Is input validated at the trust
boundary? What is the blast radius of one compromised component?

## Integrability

Goal: make components work together with bounded effort, now and as they evolve.

- **Limit dependencies**: encapsulate · use an intermediary · restrict communication paths ·
  adhere to standards · abstract common services.
- **Adapt**: discover · tailor interface (add/hide/translate) · configure behaviour.
- **Coordinate**: orchestrate · manage resources.

**Questionnaire cues**: Are external contracts wrapped behind an adapter module? Is there a
timeout budget and a circuit breaker on every synchronous external call? What breaks if a
partner changes its contract?

## Testability

Goal: make it cheap to demonstrate a fault (or its absence) after a change.

- **Control and observe state**: specialized interfaces · record/playback · localize state
  storage · abstract data sources · sandbox · executable assertions.
- **Limit complexity**: limit structural complexity · limit non-determinism.

**Questionnaire cues**: Can a component be driven and observed in isolation? Is state
externalised so it can be set? How much of the behaviour is non-deterministic?

## Usability / interaction capability

Goal: let users learn, work efficiently, recover from error, and stay in control.

- **Support user initiative**: cancel · undo · pause/resume · aggregate.
- **Support system initiative**: maintain task model · maintain user model · maintain system
  model (progress feedback, predictions).

**Questionnaire cues**: Is every long action cancellable and every destructive action
reversible? Is progress shown for anything over ~1 s? Are errors preventable by design?

## Safety (where applicable)

- **Detect unsafe state**: sensor/actuator monitoring · timeout · timestamp · condition
  monitoring · comparison.
- **Contain / recover**: redundancy · degradation · masking · barrier · rollback · repair state ·
  recalculation · limit consequences (interlock, fault containment region) · fail safe /
  fail operational.
- **Prevent unsafe state**: substitution · predictive model · interlock.

## Energy efficiency, scalability, portability

These are covered by tactics drawn from the sets above (performance + deployability +
modifiability) plus:

- **Scalability**: statelessness · partitioning (sharding) · elastic resource pools ·
  load balancing · asynchronous processing.
- **Portability**: intermediary (adapter, HAL) · restrict dependencies to a portability layer ·
  defer binding to the platform · adhere to standards.
- **Energy**: monitor and meter consumption · scale to zero · schedule work to efficient
  times/nodes · reduce polling · right-size resources.
