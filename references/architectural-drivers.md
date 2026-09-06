# Reference — Architectural drivers

The **architectural drivers** are the small set of requirements and context that most strongly
shape the architecture. Getting them right is the point of leverage in the whole SEI method:
ADD iterations are scoped by them, ATAM analysis targets them, and Views-and-Beyond rationale
cites them.

## Register layout

Because a real system has many drivers, the `architectural-drivers` skill stores them as a
**directory**, not one file:

```
architecture/drivers/
├── README.md           # ID legend · traceability matrix · coverage check · prioritised list · change log
├── business-goals/README.md + BG-<n>.md
├── use-cases/README.md + UC-<n>.md   (+ use-cases/diagrams/UC-<n>.puml|.mmd|.png — one UML use case diagram each)
├── constraints/README.md + CON-<n>.md
└── quality-attributes/
    ├── README.md               # index: links every <ATTR>QA-<n>.md + the utility tree
    ├── <ATTR>QA-<n>.md         (six-part scenario + horizontal scenario diagram)
    └── utility-tree.md         # the summary of the quality attributes — a TABLE (from the QAW)
```

Add a driver = add a file + one row in the top `README.md` + one row in the subdirectory
`README.md`. Every cross-reference is a relative Markdown link. Never renumber; retire
(`Status: retired`), don't delete.

## What makes a requirement an ASR

An **architecturally significant requirement** is one worth capturing here because it meets
**both** tests:

1. **Profound impact on the architecture** — including it leads to a materially different
   structure than leaving it out.
2. **High business or mission value** — it matters enough to important stakeholders that the
   architecture should satisfy it, possibly at the expense of others.

ASRs come from four places, and are recorded in one place (this register) so they can be
reviewed, cited in decisions, and revisited on change:

- **requirements documents** — read them, colour-code architecturally significant material,
  chase the rest to a stakeholder;
- **stakeholder interviews / a QAW** — elicit and prioritise scenarios directly;
- **the architect's utility tree** — when stakeholders are not available, the architect drafts
  the QA-related ASRs top-down (Utility → QA → refinement → scenario) and rates each leaf;
- **derivation from business goals** — each goal implies requirements the architecture must meet.

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

For an important or contested goal, expand it into a **seven-part business-goal scenario** (the
structure PALM elicits):

| Part | What it captures |
|------|------------------|
| 1. Goal-source | the person / role who wants the goal met |
| 2. Goal-subject | the stakeholder(s) whose satisfaction the goal is about |
| 3. Goal-object | the entity the goal is about — the system, the organisation, a portfolio |
| 4. Environment | the context in which the goal applies (market conditions, regulatory regime, timeframe) |
| 5. Goal | the goal itself, stated concretely |
| 6. Goal-measure | how and by when success is judged |
| 7. Pedigree & value | who set the goal, how confident they are, how volatile it is, and its value/priority |

A goal expressed this way makes the derived ASRs and their priorities defensible.

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
six-part UML scenario diagram. Prioritised with a `(V, R)` pair — **business value** and
**technical risk**, each `H`/`M`/`L` (`V ≈ Importance`, `R ≈ Difficulty`).

## The utility tree — a table

The utility tree is the summary of all quality-attribute ASRs, kept in
`quality-attributes/utility-tree.md` **as a table**, not a diagram. Three grouping levels are
columns:

| Quality attribute (ISO/IEC 25010) | Refinement (concern) | Leaf scenario (ID + response measure) | Priority (V, R) | Status |

- The **root** is "Utility" (overall fitness for purpose).
- Each leaf is a concrete scenario with an explicit response and a numeric response measure.
- `(V, R)`: **V** = must-have (`H`) / important-not-fatal (`M`) / nice-to-have (`L`);
  **R** = keeps-you-up-at-night (`H`) / concerning (`M`) / confident (`L`). Mark `(H, H)` `★`.
- **Checks after filling it in**: a QA or refinement with no leaf is a prompt to look for an
  unrecorded ASR (not automatically an error); the `★` leaves get the most design attention,
  and a large number of them is a signal to question feasibility.

The QAW produces this table at its Step 9; otherwise the architect drafts it. ATAM Step 5 reuses
it and analyses the `★` / `(H, M)` leaves.

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
