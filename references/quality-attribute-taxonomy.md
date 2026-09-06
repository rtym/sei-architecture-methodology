# Reference — Quality attribute taxonomy (ISO/IEC 25010:2023) + SEI scenario mechanics

Use **ISO/IEC 25010** as the classification vocabulary and the **SEI six-part scenario** as the
form. Every quality attribute scenario names an ISO characteristic and sub-characteristic.

## The six-part scenario (SEI / Bass–Clements–Kazman)

| Part | Definition | Watch for |
|------|-----------|-----------|
| Source of stimulus | The entity (human, system, timer, sensor) that generated the stimulus | "the user" is too vague — name the role or system |
| Stimulus | A condition arriving at the system that needs a response | must be a discrete, describable event |
| Artifact | The part of the system the stimulus arrives at | whole system, a service, a data store, the build pipeline |
| Environment | The system's mode/state when the stimulus occurs | normal, peak/overload, degraded, startup, deployment, maintenance |
| Response | The activity that results from the stimulus | observable behaviour, not an implementation |
| Response measure | The response quantified so the requirement is testable | a number with a unit and, for time, a percentile |

**General scenario** = attribute-level template (reusable). **Concrete scenario** = filled in for
this system. Utility trees and QAWs produce concrete scenarios.

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
are in `references/tactics-catalog.md`, and the patterns that bundle them in
`references/architecture-patterns.md`. When *analysing* an existing architecture (ATAM Step 6,
ADD Step 7, or a design review), walk the attribute's **tactics-based questionnaire**: for each
tactic, ask "is it used? where? how well is it implemented? what is the risk if it is missing or
weak?" The gaps become risks; the deliberate omissions become non-risks with a stated
assumption.

## Sources
- ISO/IEC 25010:2023 *Systems and software Quality Requirements and Evaluation (SQuaRE) —
  Product quality model*.
- Bass, Clements, Kazman — *Software Architecture in Practice*, 3rd/4th ed., ch. 4–13 (per-attribute
  general scenarios and tactics).
