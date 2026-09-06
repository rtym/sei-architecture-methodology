# Reference — General scenarios per quality attribute

The **general scenario** for an attribute is a reusable template: for each of the six parts it
lists the *range of values* a concrete scenario can draw from. Build a concrete
`<ATTR>QA-<n>` by picking one (or a few) value(s) per part, making them specific to your
system, and putting a **number with a unit** (and a percentile for time) on the response
measure. Tactic lists for each attribute are in `references/tactics-catalog.md`; the
tactics-based questionnaire framing is in `references/quality-attribute-taxonomy.md`.

ISO/IEC 25010 homes: availability → Reliability; deployability / energy efficiency / scalability
/ portability → Flexibility; integrability → Compatibility; modifiability / testability →
Maintainability; performance → Performance efficiency; safety → Safety; security → Security;
usability → Interaction capability.

---

## Availability

| Part | Possible values |
|------|-----------------|
| Source | internal / external: people, hardware, software, physical infrastructure, physical environment |
| Stimulus | a **fault**: omission, crash, incorrect timing, incorrect response |
| Artifact | processors, communication channels, storage, processes, affected artifacts in the environment |
| Environment | normal operation, startup, shutdown, repair mode, degraded operation, overloaded operation |
| Response | prevent the fault from becoming a failure; **detect** (log; notify people/systems); **recover** (disable the fault source; be temporarily unavailable during repair; fix/mask the fault or contain the damage; operate in degraded mode during repair) |
| Response measure | time/interval the system must be available; availability % (e.g. 99.999); time to detect the fault; time to repair; time/interval allowed in degraded mode; proportion or rate of a fault class handled without failing |

*Sample:* a server in a server farm fails during normal operation; the system informs the
operator and continues to operate with no downtime.
High-availability reference points: 99.9 % ≈ 8 h 46 m/yr down; 99.99 % ≈ 52 m/yr; 99.999 %
("five nines") ≈ 5 m/yr; 99.9999 % ≈ 32 s/yr. Only unscheduled outages count.

## Deployability

| Part | Possible values |
|------|-----------------|
| Source | end user, developer, system administrator, operations personnel, component marketplace, product owner |
| Stimulus | a new element is available to deploy (replace an element with a new version — defect fix, security patch, framework/component upgrade, upgrade of an internally produced element); a new element is approved for incorporation; an existing element/set needs to be **rolled back** |
| Artifact | a single software element, multiple elements, or the entire system; its platform, UI, environment, or an interoperating system |
| Environment | staging, production (or a specified subset of either): full deployment, or subset deployment to a portion of users / VMs / containers / servers / platforms |
| Response | incorporate the new components; deploy them; monitor them; roll back a previous deployment |
| Response measure | cost — number/size/complexity of affected artifacts, average/worst-case effort, elapsed clock/calendar time, money, new defects; extent of ripple to other functions/QAs; number of failed deployments; repeatability, traceability, cycle time of the process |

*Sample:* a new release of an auth service in the component marketplace is chosen by the
product owner; it is tested and deployed to production within 40 h and ≤ 120 person-hours, with
no defects introduced and no SLA violated.

## Energy efficiency

| Part | Possible values |
|------|-----------------|
| Source | end user, manager, system administrator, automated agent |
| Stimulus | a request to conserve energy — total usage, maximum instantaneous usage, average usage |
| Artifact | specific devices, servers, VMs, clusters |
| Environment | runtime, connected, battery-powered, low-battery mode, power-conservation mode |
| Response | disable services; deallocate runtime services; change allocation of services to servers; run services at a lower consumption mode; allocate/deallocate servers; change level of service; change scheduling |
| Response measure | max/avg kilowatt load; avg/total energy saved; total kWh used; time the system must stay powered on — while maintaining a required functionality level and acceptable levels of other QAs |

*Sample:* a manager wants to save energy at runtime by deallocating unused resources at
non-peak periods; the system deallocates resources while keeping worst-case DB-query latency
< 2 s, saving on average 50 % of the total energy required.

## Integrability

| Part | Possible values |
|------|-----------------|
| Source | mission/system stakeholder, component marketplace, component vendor |
| Stimulus | add a new component; integrate a new version of an existing component; integrate existing components together in a new way |
| Artifact | the entire system; a specific set of components; component metadata; component configuration |
| Environment | development, integration, deployment, runtime |
| Response | changes are {completed, integrated, tested, deployed}; components in the new configuration exchange information correctly (syntactically and semantically); they collaborate successfully; they do not violate any resource limits |
| Response measure | cost — number of components changed, % of code changed, LOC changed, effort, money, calendar time; effects on other QA response measures (to capture allowable tradeoffs) |

*Sample:* a new data-filtering component becomes available in the marketplace; it is integrated
and deployed in 1 month with ≤ 1 person-month of effort.

## Modifiability

| Part | Possible values |
|------|-----------------|
| Source | end user, developer, system administrator, product-line owner, the system itself (learns / self-modifies) |
| Stimulus | a directive to add/delete/modify functionality, or change a quality attribute, capacity, platform, or technology; add a product to a product line; change the location of a service |
| Artifact | code, data, interfaces, components, resources, test cases, configurations, documentation |
| Environment | runtime, compile time, build time, initiation time, design time |
| Response | make the modification; test it; deploy it; self-modify |
| Response measure | cost — number/size/complexity of affected artifacts; effort; elapsed time; money (outlay or opportunity cost); extent of ripple to other functions/QAs; new defects introduced; time for the system to adapt |

*Sample:* a developer wants to change the UI; the change is made to the code at design time,
takes < 3 h to make and test, and no side effects occur.

## Performance

| Part | Possible values |
|------|-----------------|
| Source | external: a user request, a request from an external system, data from a sensor; internal: one component requesting another, a timer notification |
| Stimulus | arrival of a **periodic** event (predictable interval), a **stochastic** event (probability distribution), or a **sporadic** event (neither) |
| Artifact | the whole system, or a component within it |
| Environment | runtime — normal mode, emergency mode, error-correction mode, peak load, overload mode, degraded-operation mode, some other defined mode |
| Response | system returns a response / an error / no response; ignores the request if overloaded; changes the mode or level of service; services a higher-priority event; consumes resources |
| Response measure | latency (max/min/mean/median); throughput (satisfied requests over an interval); number/percentage of requests unsatisfied; jitter; utilisation of a computing resource (CPU, memory, thread pool, buffer) |

*Sample:* 500 users initiate 2 000 requests in a 30-second interval under normal operations; the
system processes all requests with an average latency of 2 seconds.
Two contributors to response time: **processing time** (working, consuming resources — CPU
degrades gradually, memory can crash suddenly) and **blocked time** (resource contention,
resource unavailable, or dependency on another not-yet-complete computation).

## Safety

| Part | Possible values |
|------|-----------------|
| Source | a data source (sensor, software component computing a value, communication channel), a time source (clock), or a user action |
| Stimulus | an **omission** (a value never arrives; a function is never performed); a **commission** (a function performed incorrectly; a device produces a spurious event or incorrect data; a sensor reports incorrect data; a component produces incorrect results); a **timing failure** (data too late/early; an event too late/early or at the wrong rate; events in the wrong order) |
| Artifact | safety-critical portions of the system |
| Environment | normal operation, degraded operation, manual operation, recovery mode |
| Response | recognise the unsafe state and: avoid it; recover; continue in degraded or safe mode; shut down; switch to manual operation; switch to a backup system; notify appropriate entities; log the unsafe state and the response |
| Response measure | % of entries into unsafe states avoided; % of unsafe states from which the system can (automatically) recover; change in risk exposure = size(loss) × prob(loss); % of time the system can recover; time in degraded/safe mode; % of time shut down; elapsed time to enter and recover (from manual operation, from a safe/degraded mode) |

*Sample:* a sensor in a patient-monitoring system fails to report a life-critical value after
100 ms; the failure is logged, a warning light is illuminated, and the system enters a safe
mode. (Architect for safety by first identifying safety-critical functions via **FMEA / hazard
analysis** and **fault tree analysis (FTA)**, then designing detect + mitigate mechanisms.)

## Security

| Part | Possible values |
|------|-----------------|
| Source | human, or another system; inside or outside the organization; previously identified (correctly or not) or currently unknown |
| Stimulus | an **attack** — an unauthorized attempt to: display data, capture data, change or delete data, access system services, change the system's behaviour, reduce availability |
| Artifact | system services; data within the system; a component or resources of the system; data produced or consumed by the system |
| Environment | the system is online/offline; connected to / disconnected from a network; behind a firewall or open; fully / partially / not operational |
| Response | maintain **confidentiality, integrity, availability**: protect data/services from unauthorized access; prevent unauthorized manipulation; identify parties with assurance; non-repudiation; keep data/services available for legitimate use. Track activity: record access/modification; record access attempts; notify appropriate entities when an attack appears to be occurring |
| Response measure | how much of a resource is compromised / ensured; accuracy of attack detection; time before an attack was detected; how many attacks were resisted; time to recover from a successful attack; how much data is vulnerable to a particular attack |

*Sample:* a disgruntled employee at a remote location attempts to improperly modify the pay-rate
table; the system maintains an audit trail, and the correct data is restored within a day.
(**PII** — personally identifiable information — is a distinct confidentiality concern:
who inside and outside the collecting organization may see it; obscure it for testing.)

## Testability

| Part | Possible values |
|------|-----------------|
| Source | a human or an automated test tool — unit / integration / system / acceptance testers, end users; run manually or with automated tools |
| Stimulus | a test or set of tests is initiated to: validate system functions; validate qualities; discover emerging threats to quality |
| Environment | at a life-cycle milestone: completion of a coding increment (class, layer, service); completed integration of a subsystem; full implementation; deployment to production; delivery to a customer; a testing schedule |
| Artifact | the portion being tested (a unit of code / component / service / subsystem / the whole system) and the test infrastructure |
| Response | control the system and test infrastructure to perform the desired tests; observe the results; capture the activity that caused a fault; control and monitor system state |
| Response measure | effort to find a fault or class of faults; effort to achieve a given % of state-space coverage; probability a fault is revealed by the next test; time to perform tests; effort to detect faults; time to prepare the test infrastructure; effort to bring the system into a specific state; reduction in risk exposure = size(loss) × prob(loss) |

*Sample:* a developer completes a code unit and runs a test sequence whose results are
captured, giving 85 % path coverage within 30 minutes.

## Usability

| Part | Possible values |
|------|-----------------|
| Source | the end user (possibly in a specialized role such as a system/network administrator); an external event arriving at the system to which the user may react |
| Stimulus | the end user wants to: use the system efficiently; learn to use the system; minimise the impact of errors; adapt the system; configure the system |
| Environment | the user actions occur at runtime or at system-configuration time |
| Artifact | a GUI, a command-line interface, a voice interface, a touch screen |
| Response | provide the features needed; anticipate the user's needs; provide appropriate feedback |
| Response measure | task time; number of errors; learning time; ratio of learning time to task time; number of tasks accomplished; user satisfaction; gain of user knowledge; ratio of successful to total operations; time or data lost when an error occurs |

*Sample:* a user downloads a new application and is using it productively after 2 minutes of
experimentation. (Usability is tightly coupled to **modifiability** — you will iterate the UI,
so architect to make that iteration cheap.)
