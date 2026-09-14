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

1. **Profound impact on the architecture** — the architecture would be *dramatically different*
   without it. (Not all requirements are equal — features shape structure the least; QA
   requirements shape it the most.)
2. **High business or mission value** — it matters enough to important stakeholders that the
   architecture should satisfy it, possibly at the expense of others.

You cannot design a successful architecture if you don't know the ASRs. Identifying them takes
real work — and the first thing experienced architects do is **talk to the important
stakeholders.**

## Four ways to gather ASRs

Record what you find in one place (this register) so it can be reviewed, cited in decisions,
and revisited on change.

### 1. From requirements documents — "don't get your hopes up"

Requirements specs fail an architect two ways: most of their content (features) barely shapes
the architecture; and much of what *does* shape it (developmental qualities, teaming, business
goals) isn't in even a good spec. Statements like "the system shall be modular / usable / fast"
aren't testable — treat them as an **invitation to a conversation** about what the requirement
really is. **Sniff out** candidate ASRs by looking for these categories (and remember: the
*anticipated change/evolution* of each is usually ASR too):

| Category | Look for |
|----------|----------|
| Usage | user roles vs. system modes; internationalization; language distinctions |
| Time | timeliness; coordination between elements |
| External elements | external systems, protocols, sensors/actuators, middleware |
| Networking | network properties and configurations (incl. their security) |
| Orchestration | processing steps; information flows |
| Security properties | user roles, permissions, authentication |
| Data | persistence; currency (freshness) |
| Resources | time, concurrency, memory footprint, scheduling, multi-user/-activity, devices, energy, soft resources (buffers, queues), scalability |
| Project management | teaming, skill sets, training, team coordination |
| Hardware choices | processors, processor families, processor evolution |
| Flexibility | portability, calibrations, configurations |
| Named technologies | mandated commercial packages / stacks |

### 2. By interviewing stakeholders (a QAW is one structured form)

Stakeholders often **don't know** their QA requirements — so the architect helps *set* them
(collaboration; relish it). Insisting on precise numbers up front yields arbitrary numbers that
hurt success. Experienced architects know what similar systems exhibited and what's cheap vs.
prohibitive — and are the only people who can say "I can deliver better than you had in mind —
useful?".

**When a stakeholder says "I don't know what that requirement should be" — play dumb.**
"So… 24 hours would be OK?" → *"No!"* → "1 hour?" → *"No!"* → "5 minutes?" → *"No!"* → "10
seconds?" → *"…I could live with that."* A **range** of acceptable values is enough to choose
architectural mechanisms — 24 h vs. 10 min vs. 10 s vs. 100 ms means very different approaches.

The QAW is a facilitated, stakeholder-focused method to generate, consolidate, prioritise, and
refine QA scenarios *before* the architecture is complete (full 8-step method:
`${CLAUDE_PLUGIN_ROOT}/references/qaw-method.md`). Its results feed five uses: refine requirements · understand /
clarify the architectural drivers · provide rationale for later design decisions · guide
prototypes and simulations · influence the order the architecture is developed.

### 3. By understanding the business goals (PALM)

Business goals are the *raison d'être* for the system. Three relationships between a business
goal and the architecture:

1. **A goal leads to a QA requirement** — every QA requirement traces up to a higher purpose
   ("differentiate from competitors → unusually fast response time"). Knowing the goal behind a
   stringent requirement lets you **question it meaningfully** or marshal the resources to meet
   it.
2. **A goal affects the architecture *without* inducing a QA requirement** — e.g. an
   architecture that cleverly avoids needing a database is still "deficient" if the org has an
   idle, highly-paid database team that needs work; no spec would capture that, yet it shapes
   the design.
3. **No influence** — a "reduce cost" goal met by lowering the office thermostat.

Architects usually learn business goals by **osmosis**; systematic capture is better because
goals imply ASRs that would otherwise surface too late. **PALM** is a workshop with the
architect + key business stakeholders:
- **Elicit business goals** — guided by the 11 categories below; express each as a **seven-part
  business-goal scenario** (see "Business goals" section); consolidate near-alikes; prioritise.
- **Derive potential QAs** — for each important goal scenario, name a QA and a response-measure
  value that, if architected in, would help achieve the goal.

The **11 business-goal categories** (use as elicitation prompts): 1 growth & continuity of the
organisation · 2 meeting financial objectives · 3 meeting personal objectives · 4 responsibility
to employees · 5 responsibility to society · 6 responsibility to the state · 7 responsibility to
shareholders · 8 managing market position · 9 improving business processes · 10 managing the
quality & reputation of products · 11 managing change in the environment over time.

### 4. From the architect's utility tree

When the primary sources aren't available, the architect drafts the QA-related ASRs **top-down**
(Utility → QA → refinement → scenario) and rates each leaf `(V, R)` — see "The utility tree" below.

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
