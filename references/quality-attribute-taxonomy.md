# Reference — Quality attribute taxonomy (ISO/IEC 25010:2023) + SEI scenario mechanics

Use **ISO/IEC 25010** as the classification vocabulary and the **SEI six-part scenario** as the
form. Every quality attribute scenario names an ISO characteristic and sub-characteristic.

## Why quality attributes drive the architecture

A **quality attribute (QA)** is a *measurable or testable* property that indicates how well the
system satisfies stakeholder needs *beyond* basic function — the "utility" of the product along
a dimension of interest.

- **Functionality does not determine architecture.** Given a set of required functions there is
  no end to the architectures that satisfy them (if function were all that mattered, a single
  monolithic blob would do). We structure systems into cooperating elements *for the other
  qualities.* Functionality is achieved by **assigning responsibilities** to elements — which
  produces the module decomposition; the architect's interest in functionality is how it
  interacts with and constrains the other qualities.
- **Three problems** with most QA discussions, and their fixes:
  1. definitions aren't testable ("the system shall be modifiable" — every system is modifiable
     w.r.t. *some* changes and not others) → fix: **QA scenarios**;
  2. endless debate over which attribute an issue "belongs to" (a denial-of-service attack —
     availability? performance? security? usability? all claim it) → fix: **QA scenarios**;
  3. each attribute community has its own vocabulary (events / attacks / faults / user input
     may name the same occurrence) → fix: a **common form** per attribute (the general
     scenarios below).
- **Two categories**: *runtime* qualities (availability, performance, usability) and
  *development-time* qualities (modifiability, testability, deployability).
- **QAs are never achieved in isolation** — achieving one affects others, often negatively
  (almost every QA costs performance; portability isolates dependencies behind process /
  procedure boundaries → overhead). Design is partly the art of the appropriate **tradeoff**.
- **"Not my problem."** The software architect may not be responsible for *every* QA requirement
  — a system may meet its security need with barbed wire and guards, not software. Confirm
  which QAs are actually in the architecture's scope.

## The six-part scenario (SEI / Bass–Clements–Kazman)

| Part | Definition | Watch for |
|------|-----------|-----------|
| Source of stimulus | The entity (human, system, timer, sensor) that generated the stimulus | "the user" is too vague — name the role or system |
| Stimulus | A condition arriving at the system that needs a response | must be a discrete, describable event |
| Artifact | The part of the system the stimulus arrives at | whole system, a service, a data store, the build pipeline |
| Environment | The system's mode/state when the stimulus occurs | normal, peak/overload, degraded, startup, deployment, maintenance |
| Response | The activity that results from the stimulus | observable behaviour, not an implementation |
| Response measure | The response quantified so the requirement is testable | a number with a unit and, for time, a percentile |

The four core parts (stimulus, source, response, response measure) are the heart; **environment
and artifact are the two most often overlooked** — knowing all six are there forces the
architect to consider whether each is relevant. "Environment" can be a runtime *mode* (normal,
overload, degraded) **or** a non-running state (development, testing, data refresh, battery
recharge).

**General scenario** = attribute-level, system-independent template (the "portions" menu).
**Concrete scenario** = filled in for this system. It is far easier for a stakeholder to
*tailor a general scenario* than to invent one from thin air — so brainstorm concrete scenarios
by walking the general-scenario portions (`${CLAUDE_PLUGIN_ROOT}/references/quality-attribute-scenarios.md`).

## Achieving quality attributes: tactics and patterns

- A **tactic** is a design decision that influences **one** quality-attribute response — it
  directly affects the system's response to a stimulus. Per-attribute lists:
  `${CLAUDE_PLUGIN_ROOT}/references/tactics-catalog.md`.
- An **architectural pattern** is a proven solution to a recurring design problem, specified by
  the roles, responsibilities, relationships, and collaboration of its elements. A pattern
  usually affects **more than one** QA and **bundles several tactics** — so patterns frequently
  *make* QA tradeoffs. Catalog: `${CLAUDE_PLUGIN_ROOT}/references/architecture-patterns.md`.
- **Refine tactics to be concrete**: *schedule resources* → SJF / round-robin / fixed-priority;
  *use an intermediary* → layer / broker / proxy / tier. Application is context-dependent
  (*manage sampling rate* fits some real-time systems, is wrong for stock trading).
- **Super-tactics** appear almost everywhere: modifiability's *encapsulate*, *restrict
  dependencies*, *use an intermediary*, *abstract common services* (in the realisation of
  nearly every pattern); *schedule resources*; and **monitor** (used for energy efficiency,
  performance, availability, and safety). A load balancer is an intermediary that does
  scheduling. A tactic is a design primitive found over and over, across attributes — which is
  precisely why tactics are worth mastering.
- **Design and process both matter.** A great security architecture is worthless if staff fall
  for phishing. QAs also deteriorate over time through well-intentioned local decisions
  ("death by a thousand cuts" → **architecture debt**); reverse it by **refactoring
  architectural elements**, not just code (`${CLAUDE_PLUGIN_ROOT}/references/architecture-in-the-lifecycle.md`).

### The tactics-based questionnaire — the four-step procedure

Per tactic question (`${CLAUDE_PLUGIN_ROOT}/references/tactics-catalog.md` supplies the questions per QA):

1. **Supported?** — mark the column `Y` / `N`.
2. **Design decisions and location** — if `Y`, the specific decisions made to realise the
   tactic and *where in the architecture / code base* they manifest (for auditing and
   architecture reconstruction). Note how it's realised — custom code, framework, or externally
   produced component.
3. **Risk** — `H` / `M` / `L` for implementing (or *not* implementing) the tactic.
4. **Rationale** — why the decisions were made (including a decision *not* to use the tactic)
   and the implications (cost, schedule, evolution).

~30–90 minutes per quality attribute; forces the architect to step back and see the bigger
picture; reveals decisions taken *and not taken*, and the risks buried in them.

## ISO/IEC 25010:2023 — product quality model (9 characteristics)

| # | Characteristic | Sub-characteristics | Typical stimulus → response → measure |
|---|----------------|---------------------|--------------------------------------|
| 1 | **Functional suitability** | completeness, correctness, appropriateness | usually functional requirements / use cases, not QAS |
| 2 | **Performance efficiency** | time behaviour, resource utilization, capacity | *N concurrent requests, normal ops* → *served* → *p95 latency < X ms; CPU < Y %; sustains Z req/s* |
| 3 | **Compatibility** | co-existence, interoperability | *a partner system sends msg format V, production* → *accepted & processed* → *100 % of conformant messages, 0 data loss* |
| 4 | **Interaction capability** (2011: *usability*) | appropriateness recognizability, learnability, operability, user error protection, user engagement, inclusivity, user assistance, self-descriptiveness | *first-time user performs task T* → *completes without help* → *≥ 85 % task completion; ≤ 2 errors; WCAG 2.2 AA* |
| 5 | **Reliability** | faultlessness, availability, fault tolerance, recoverability | *a node fails, production* → *system stays available / recovers* → *uptime ≥ 99.95 %/mo; failover < 30 s; RPO 5 min, RTO 1 h* |
| 6 | **Security** | confidentiality, integrity, non-repudiation, accountability, authenticity, resistance | *attacker attempts cross-tenant read* → *rejected & logged* → *0 successful reads; 100 % logged; alert < 1 min* |
| 7 | **Maintainability** | modularity, reusability, analysability, modifiability, testability | *developer adds report type, during a sprint* → *change localised* → *≤ 1 person-day; ≤ 3 modules touched; 0 regressions* |
| 8 | **Flexibility** (2023; absorbs *portability* & much of *scalability*) | adaptability, scalability, installability, replaceability | *load grows 10×, normal ops* → *scales horizontally* → *linear cost to 10×; no code change; provisioning < 10 min* |
| 9 | **Safety** (2023, new) | operational constraint, risk identification, fail safe, hazard warning, safe integration | *sensor returns out-of-range value, operation* → *system enters safe state & warns* → *safe state < 500 ms; operator alerted; hazard logged* |

### 2011 vs 2023
The **2011** model has 8 characteristics: *functional suitability, performance efficiency,
compatibility, **usability**, reliability, security, maintainability, **portability***. The
**2023** revision renames usability → **interaction capability**, adds **flexibility** and
**safety**, and folds portability's sub-characteristics into flexibility. State which edition the
project uses in the artifact header.

### Related ISO standards
- **ISO/IEC 25012** — data quality model (accuracy, completeness, consistency, currentness,
  confidentiality, traceability, …). Use when data is a first-class concern.
- **ISO/IEC 25019** (Quality-in-use) / **25002**, **25023** (measures). Use 25023 for concrete
  metric definitions behind a response measure.
- **ISO/IEC/IEEE 42010** — architecture description (viewpoints, views, correspondence rules);
  the basis the `architecture-documentation` skill's Views-and-Beyond output aligns with.

## Attribute-by-attribute scenario checklists

**Performance efficiency** — arrival pattern (periodic/stochastic/sporadic), load level, mix of
operations, contention for shared resources; response = latency / throughput / deadline;
measure = percentile latency, req/s, jitter, queue depth.

**Reliability / availability** — fault type (crash, omission, timing, response, Byzantine),
detection, and recovery (active/passive redundancy, spare, rollback, degradation); measure =
availability %, MTBF, MTTR, failover time, RPO/RTO, proportion of faults handled.

**Security** — actor (insider/outsider, authenticated/not), asset, action (disclose, modify,
deny, fabricate); response = authenticate, authorize, encrypt, audit, limit exposure, recover;
measure = time/effort to breach, % of attacks detected/logged, time to detect & respond.

**Maintainability / modifiability** — what changes (function, platform, capacity, vendor), who
changes it, when (design/build/runtime); response = locate, make, test, deploy the change;
measure = effort (person-days), number of elements/LOC touched, regressions, deployment time.

**Interaction capability / usability** — learn a feature, use efficiently, minimise error impact,
adapt, feel comfortable; measure = task time, task completion rate, error rate, satisfaction
score, accessibility conformance level.

**Compatibility / interoperability** — an external system of known/unknown identity exchanges
data/services in a defined/discovered manner; measure = % of exchanges correctly processed,
data loss, contract-conformance rate.

**Flexibility / scalability** — dimension of growth (users, data, transactions, geography,
features); response = horizontal/vertical scaling, feature toggles, plug-ins; measure = cost
curve vs load, provisioning time, code change required.

**Safety** — unsafe state trigger, hazard; response = detect, prevent, fail safe/operational,
warn, contain; measure = time to safe state, proportion of hazards mitigated, false-alarm rate.

**Testability** — a fault exists after a change; response = control inputs, observe outputs,
isolate the unit; measure = branch/statement coverage achievable, probability a fault surfaces
per test, time to set up a test.

**Deployability** (BCK 4th ed; maps to *flexibility/installability*) — a new version is ready;
response = deploy with control, safety, rollback; measure = time to deploy, blast radius,
rollback time, deployment frequency.

## General scenario "portions" — the menu for each part

A **general scenario** is the attribute-level template: for each of the six parts it lists the
*range of values* a concrete scenario can pick from. Building a concrete scenario is choosing
one value (or a few) from each portion and making them specific and measurable.

| Part | Typical portions to choose from |
|------|--------------------------------|
| Source | end user · administrator/operator · another system (internal / external, known / unknown) · a timer · a sensor · a developer / a code commit · an attacker · the infrastructure |
| Stimulus | a request at a given rate/mix · a fault (crash / omission / timing / wrong response) · a change request (to function, platform, capacity, vendor) · an attack (disclose / modify / deny / fabricate) · a deployment · a spike in load |
| Artifact | the whole system · a specific service / component / connector · a data store · the build pipeline · the deployment infrastructure · a specific interface |
| Environment | normal operation · peak / overload · degraded mode · startup / shutdown · during deployment · maintenance window · post-incident recovery |
| Response | serve / process · detect + log + alert · fail over / degrade gracefully / recover · reject + audit · make the change with bounded ripple · scale out |
| Response measure | latency percentile · throughput (req/s) · availability % / MTBF / MTTR / RPO / RTO · effort (person-days) and elements touched · % of attacks detected / time to breach · task-completion rate / error rate · cost curve vs. load |

Use the per-attribute checklists above to pick sensible portions; then make every chosen value
concrete and put a **number with a unit** (and, for time, a percentile) on the response measure.

## Tactics and the tactics-based questionnaire

Once an attribute matters, the design levers for it are **tactics** — the per-attribute lists
are in `${CLAUDE_PLUGIN_ROOT}/references/tactics-catalog.md`, and the patterns that bundle them in
`${CLAUDE_PLUGIN_ROOT}/references/architecture-patterns.md`. When *analysing* an existing architecture (ATAM Step 6,
ADD Step 7, or a design review), walk the attribute's **tactics-based questionnaire**: for each
tactic, ask "is it used? where? how well is it implemented? what is the risk if it is missing or
weak?" The gaps become risks; the deliberate omissions become non-risks with a stated
assumption.

## Sources
- ISO/IEC 25010:2023 *Systems and software Quality Requirements and Evaluation (SQuaRE) —
  Product quality model*.
- Bass, Clements, Kazman — *Software Architecture in Practice*, 3rd/4th ed., ch. 4–13 (per-attribute
  general scenarios and tactics).
