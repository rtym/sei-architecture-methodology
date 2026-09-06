# Reference — Architectural drivers

The **architectural drivers** are the small set of requirements and context that most strongly
shape the architecture. Getting them right is the point of leverage in the whole SEI method:
ADD iterations are scoped by them, ATAM analysis targets them, and Views-and-Beyond rationale
cites them.

## The four kinds

### 1. Business goals (`BG-`)
Why the system exists and what "success" means to the organisation paying for it. The SEI
business-goal categories (from *Software Architecture in Practice*, and the PALM method):

1. Contributing to **growth and continuity** of the organisation (market share, new markets).
2. Meeting **financial objectives** (revenue, cost, ROI, margins).
3. Meeting **personal objectives** of individuals (reputation, career, curiosity).
4. Meeting **responsibility to employees** (skills, safety, satisfaction).
5. Meeting **responsibility to society and the law** (regulation, standards, ethics, environment).
6. Meeting **responsibility to state and nation**.
7. Managing the **quality and reputation of the organisation's products**.
8. Improving **business processes**.
9. Managing **market position** — technical leadership, first-mover, brand.
10. Managing **change in the environment** (technology shifts, competitors).
11. Managing **relationships with stakeholders, suppliers, partners**.

Write each goal as: *`<stakeholder>` needs `<outcome>` so that `<business value>`.*

### 2. Primary functional requirements — as use cases (`UC-`)
The behaviour the system must provide **that has architectural impact**. Not every feature — only
those that:
- exercise a quality attribute scenario (e.g. the high-volume path, the sensitive-data path),
- cross a trust boundary or a process/network boundary,
- drive a key external integration,
- dominate load, or
- are central to the system's value proposition.

Capture them as **use cases** (Cockburn style): primary actor, supporting actors, trigger,
preconditions, main success scenario, architecturally significant alternate/exception flows,
postconditions. Draw a **UML use case diagram** per actor group or subsystem: actors outside the
system boundary, use cases inside, `<<include>>` for always-invoked sub-behaviour, `<<extend>>`
for conditional sub-behaviour.

### 3. Constraints (`CON-`)
Non-negotiable decisions already made — inputs, not choices. Three types:
- **Business** — budget, schedule, team size and skills, buy-vs-build mandates, partner deals.
- **Technical** — mandated platform/language/cloud, must-integrate-with systems, protocols.
- **Regulatory** — GDPR, HIPAA, PCI-DSS, SOC 2, sector rules, data-residency, accessibility law.

Record each with its source and whether it is *hard* (cannot change) or *negotiable*. Flag any
constraint that conflicts with a business goal or quality attribute — that tension is itself a
driver.

### 4. Quality attributes — as scenarios (`<ATTR>QA-`)
The measurable qualities. Classified against **ISO/IEC 25010** (see
`quality-attribute-taxonomy.md`), each expressed as a **six-part scenario** and drawn as a
six-part UML scenario diagram. Prioritised with an `(Importance, Difficulty)` pair.

## Traceability

Maintain a matrix so coverage is checkable:

- Every **BG** is supported by ≥ 1 **UC** or **QAS** (a goal with no requirement realising it is
  either not a real goal or a missing requirement).
- Every **UC**, **QAS**, **CON** traces up to ≥ 1 **BG** (a requirement that serves no business
  goal is scope creep — challenge it).
- Track a `Status` per driver — `open / in design / partially / addressed / retired` — updated as
  ADD iterations complete and ATAM findings land.

## Prioritisation

Rank drivers for design attention by:
1. Quality scenarios that are **high importance AND high difficulty** — these constrain structure most.
2. Then high-importance / medium-difficulty scenarios.
3. Architecturally significant use cases.
4. Hard constraints (they bound the solution space rather than pull it).

The top ~5–10 form the input to ADD iteration 1.

## Sources
- Bass, Clements, Kazman — *Software Architecture in Practice*, 4th ed., ch. 3 (Understanding
  Quality Attributes), ch. 19 (Architecturally Significant Requirements), and the business-goal
  categories / PALM.
- Cervantes, Kazman — *Designing Software Architectures*, ch. 2 (Architectural Design) and the
  ADD inputs.
- Cockburn — *Writing Effective Use Cases*.
