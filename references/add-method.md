# Reference — Attribute-Driven Design (ADD 3.0)

Primary source: Cervantes & Kazman, *Designing Software Architectures: A Practical Approach*
(2nd ed., 2024). Earlier: Wojcik et al., *ADD 2.0*, CMU/SEI-2006-TR-023.

## Core idea

Architecture design is a **systematic, iterative** activity: turn decisions about architectural
drivers into structures. Each iteration takes a bounded goal and a prioritised set of drivers,
chooses and instantiates design concepts to satisfy them, sketches views, and analyses the
result. Design is decomposition guided by quality attributes, not just functionality. "A good
engineer makes a design that works with as few original ideas as possible" — the creativity is
in identifying, combining, and adapting existing solutions.

## Rounds and iterations

- A **design round** = the architecture-design activities performed within one development cycle
  (a sprint, or the whole design phase in a waterfall model). It produces an architecture that
  suits that round's **design purpose**.
- A round is one or more **design iterations**. Steps 1–7 make up a round; steps 2–7 are
  repeated per iteration.
- Before design starts, establish the **system context** (what is inside/outside, which external
  entities it talks to) — a context diagram.

## Determining scope — the design purpose

Why are we designing *now*? e.g. produce a design for early estimation · refine an existing
design for a new increment · design and build a prototype to retire a technical risk. In
brownfield work, the existing architecture is also an input. Getting the drivers and their
**priority** right is crucial — design is garbage-in-garbage-out.

## Inputs (ADD step 1)

- **Design purpose** — why are we designing now? One of:
  greenfield system · greenfield feature in an existing system · brownfield replacement ·
  brownfield extension · brownfield migration/modernisation.
- **Primary functional requirements** — the architecturally significant use cases.
- **Quality attribute scenarios** — prioritised (Importance to the business × Difficulty to achieve).
- **Constraints** — business, technical, regulatory.
- **Architectural concerns** — general (e.g. establish an overall structure), plus specific
  internal concerns the architect knows about (team skills, mandated tech, need for a
  deployment pipeline, etc.).

## The seven activities (per iteration)

1. **Review inputs.** Confirm purpose, primary FRs, QAS, constraints, concerns. The architect
   now *owns* the drivers — check no important stakeholder was missed and no business condition
   changed since prioritisation. The drivers become the initial **architectural backlog**.
2. **Establish the iteration goal by selecting drivers.** Pick the subset of drivers this
   iteration will address (a performance scenario to satisfy, a use case to enable, …). Early
   iterations favour drivers that are both high-importance and high-difficulty. The goal is one
   sentence.
3. **Choose one or more elements of the system to refine.** Greenfield iteration 1 = establish
   the context, then select the only element available — the whole system — for refinement by
   **decomposition**. Later / brownfield = refine elements from prior iterations by
   **decomposition** (top-down, into finer elements), **combination** (bottom-up, into
   coarser elements), or **improvement** of an existing element. For brownfield you need a good
   grasp of the as-built architecture (reverse engineering / developer discussions).
   **Steps 2 and 3 may be reversed** for greenfield or when fleshing out a reference
   architecture — pick an element first, then decide which drivers to address on it.
4. **Choose one or more design concepts that satisfy the selected drivers.** The **design
   concept catalog** — the menu you choose from, coarse to fine:
   - **Reference architectures** — domain-proven whole-system structures (web app 3-tier,
     microservices, event-driven / streaming, pipe-and-filter / batch, serverless, modular
     monolith). See `${CLAUDE_PLUGIN_ROOT}/references/architecture-patterns.md` (last section).
   - **Deployment patterns** — blue/green, canary, sidecar, service mesh, feature toggle.
   - **Architectural & design patterns** — layers, ports & adapters, CQRS, saga, broker,
     publish–subscribe, gateway, strangler fig, anti-corruption layer, circuit breaker,
     bulkhead, cache-aside, load balancer. Catalog: `${CLAUDE_PLUGIN_ROOT}/references/architecture-patterns.md`.
   - **Tactics** — the fine-grained decisions below patterns, one per quality-attribute
     response. Full per-attribute lists: `${CLAUDE_PLUGIN_ROOT}/references/tactics-catalog.md`.
   - **Externally developed components** — frameworks, middleware, cloud services, SaaS,
     libraries; a "buy/adopt vs build" decision with its own tradeoffs (fit, lock-in, control).

   Procedure: for each driver cluster, list 2–4 candidate concepts; put them in a pros/cons
   table; every row's rationale cites ≥ 1 driver ID; record the choice **and** the discarded
   alternatives with why. Where a concept is a tactic, name it from the catalog so ATAM can
   later question it with the matching tactics-based questionnaire.
5. **Instantiate architectural elements, allocate responsibilities, and define interfaces.**
   Turn each chosen concept into concrete named elements — the structures the iteration
   produces (module, C&C, allocation). For each element: a single clear responsibility, and its
   **provided / required interfaces** — operations, data and their types, protocol, error and
   exception semantics, and any quality-of-service the interface guarantees. Record instantiation
   decisions (what was created / split / merged and why) alongside the interface table.
6. **Sketch views and record design decisions.** Produce/update the views that capture this
   iteration's decisions (context, container, component, sequence, deployment; module / C&C /
   allocation for fuller docs). "Sketch" is deliberate — enough detail to analyse, not a
   finished description. Record decisions in an ADR-style log with rationale tied to driver IDs
   and the alternatives rejected.
7. **Perform analysis of the current design and review the iteration goal.** For each selected
   driver: satisfied / partially / not addressed, with notes on risks and assumptions. Use the
   **tactics-based questionnaire** for each attribute (`${CLAUDE_PLUGIN_ROOT}/references/tactics-catalog.md`) as the
   checklist — for every relevant tactic ask "is it used, where, and what is the risk if not?".
   Prefer a **peer** to do (or help with) the analysis — a second person won't share your
   assumptions and will have a different experience base. Then review whether enough design was
   done for the round's **design purpose**, not just the iteration goal.

**Iterate if necessary** — repeat steps 2–7 for every remaining driver, resources permitting.
**Let risk be your guide**: at minimum, address the highest-priority drivers, with certainty (or
"good enough" confidence) that the critical ones are satisfied.

## Identifying and selecting design concepts (Step 4, expanded)

**Identify** candidates three ways, usually in combination:
- **best-practice catalogs** — patterns, reference architectures, tactic taxonomies, framework
  docs (`${CLAUDE_PLUGIN_ROOT}/references/architecture-patterns.md`, `${CLAUDE_PLUGIN_ROOT}/references/tactics-catalog.md`); many
  alternatives, but vetting them costs time;
- **your own experience** — fast and confident for a familiar system type; risks reusing the
  same hammer;
- **peers** — a short brainstorm brings in experience you don't have.

**Select** by putting the candidates in a **pros/cons table** keyed to the iteration's drivers
and picking one. When the choice is high-stakes or contested, do a deeper analysis:
- **SWOT** — strengths / weaknesses / opportunities / threats of each candidate;
- **CBAM** (cost/benefit analysis method) — for each candidate strategy, estimate the utility
  it adds (via levels of quality-attribute response), its cost, and its time to implement, then
  rank by ROI. CBAM was designed to run after ATAM but can inform design directly.

Record the choice **and** the discarded alternatives with the reason (ADR-style, citing driver
IDs). Watch two things: **constraints** rule out some candidates (e.g. "libraries must carry an
approved licence"); and **earlier decisions** restrict what is now compatible (e.g. a web
reference architecture chosen in iteration 1 rules out a local-app UI framework later).

### Prototyping to select a design concept

When the analysis techniques above don't settle the choice — especially for **externally
developed components** — build an early **throwaway prototype** (no concern for maintainability
or reuse; not a basis for further development). Strongly consider a prototype if most answers
are "yes":

- Does the project use emerging technologies?
- Is the technology new to the company?
- Do any drivers (esp. QAs) carry risk that the technology can satisfy them?
- Is there a lack of trusted internal/external information about the technology?
- Are there configuration options that need testing/understanding?
- Is it unclear whether it integrates with the project's other technologies?

To decide *how much* to spend on experiments, use **Value of Information (VoI)**: assess the
cost of a wrong choice, the cost of the experiments, and your confidence in each option and in
the experiment's results; Bayes gives **EVPI** (max worth paying for a definitive experiment)
and **EVSI** (worth paying for an imperfect one). Evaluate against the team's risk appetite.

## Design roadmap — order the early iterations by system type

ADD does not fix an iteration order, but a **roadmap** keeps the start of design from being ad
hoc:

**Greenfield in a mature domain** (web app, mobile app, enterprise system, …):
1. **Establish the overall structure** — choose reference architecture(s) + deployment
   pattern(s) (+ any full-stack framework). Weigh the constraints and the QAs that favour one
   reference architecture over another.
2. **Identify structures for the primary functionality** — allocate the architecturally
   significant use cases to elements (by decomposing the reference-architecture elements); also
   think about allocating modules to teams.
3. **Refine the structures for the remaining drivers** — tactics + patterns + frameworks + the
   basics (modularity, low coupling, high cohesion).

**Greenfield in a novel domain** — no reference architecture to lean on: work from first
principles, use general-purpose tactics and patterns, and lead with **prototyping** to retire
the hardest quality-attribute risks.

**Brownfield (existing system)** — maintenance, or refactoring to cut architecture/technical
debt: Step 1's input is the existing architecture; iterations mostly refine existing structures
to meet new or violated drivers.

## Step 5 — instantiation by concept category, and interfaces

Instantiating one design concept may touch **more than one structure** (instantiating the
passive-redundancy pattern produces C&C *and* allocation structure; the decisions about spare
count, state-sync mechanism, and failure detection become module responsibilities).

| Concept | What "instantiate" means |
|---------|--------------------------|
| Reference architecture | customise — add/remove elements (e.g. add a payment-integration component to the 3-tier structure) |
| Pattern | fill in the blanks the pattern leaves — how many of each element, their functionality, who talks to whom, which protocol |
| Tactic | adapt another concept you're using to realise it, or adopt one that already realises it (custom auth vs. a security pattern with auth vs. an auth framework) |
| Externally developed component | may create elements (framework subclassing) or not (setting a thread-pool size) |

Then **allocate responsibilities** (high internal cohesion, a narrow responsibility set, low
external coupling) and identify element **properties** (config options, statefulness, resource
management, priority, hardware characteristics) — properties feed analysis and the rationale.

**Interfaces** are a contractual spec letting elements collaborate:
- **External interfaces** — of other systems you must interact with; usually a constraint you
  can't change; ≥ 1 per external system (identified via the context diagram).
- **Internal interfaces** — between the instantiated elements. "Interacts" = *anything one
  element does that impacts another*. Use behavioural representations (sequence / state /
  activity) to find relationships and interface contents. Early iterations produce abstract
  elements (layers) whose interfaces are deliberately **underspecified** ("the UI tier sends
  *commands*, the business tier sends *results*"); refine them as later iterations add
  structures for specific use cases / QA scenarios. Not every internal interface must be
  identified in a given iteration — some are delegated to later activities.

## Step 6 — preliminary documentation (choose a purpose)

Capture the sketches (a photo of the whiteboard is fine) plus a **responsibilities table** per
diagram, written **as you identify each element**. Be consistent with symbols; add a legend.
Then pick a **documentation purpose** for this iteration based on your risk-mitigation concern —
*analysis* (a critical QA scenario you must prove is met → document exactly what the analysis
needs), *construction*, or *education* (new team members → a C&C sketch + a module sketch of the
major layers) — and document to fulfil that purpose, not everything.

## Iteration planning, the design backlog, and the Kanban board

Draft an up-front plan — a handful of bounded iterations, each with a one-sentence goal —
grouped by the roadmap above. Verify **every driver ID** appears in at least one iteration /
backlog item before starting.

The plan *is* an **architectural (design) backlog** — the pending design actions. Seed it with
the drivers; add supporting items as you go: a prototype to retire a QA risk, reverse-
engineering of existing assets, issues found in a review, and QA scenarios / concerns
*discovered* while adopting a design concept (e.g. "the chosen web reference architecture has no
session management" → new concern on the backlog).

Track it on a **Kanban board** with columns **Not Yet Addressed · Partially Addressed ·
Completely Addressed · Discarded**. A driver card starts in *Not Yet Addressed*; Step 2 moves it
to *Partially Addressed* when the iteration goal selects it; Step 7 moves it to *Completely
Addressed* once the analysis confirms it. Define explicit criteria for "Completely Addressed"
(e.g. analysed, or implemented in a prototype and verified). Colour cards by priority. **End the
round** when a majority — or at least the highest-priority drivers — are *Completely Addressed*.

## Outputs

- The architecture: elements, responsibilities, relationships, interfaces.
- A set of views (C4 / UML), kept in the Architecture document.
- A design-decision (ADR) log with rationale traceable to drivers.
- Per-iteration analysis showing which drivers are satisfied.

## Analysis during design

Design and analysis interleave — don't wait for a formal ATAM. Cheap in-iteration checks
(see `${CLAUDE_PLUGIN_ROOT}/references/design-reviews.md`):
- **Tactics-based analysis** — walk the attribute's tactic list as a questionnaire.
- **Reflective questions** — the architect asks themselves the "have I…?" questions for the
  iteration's drivers before declaring the goal met.
- **Scenario-based design review** — a short peer review that walks the top scenarios against
  the current structures.

## Common mistakes

- Designing structure from functionality alone, ignoring the QAS.
- Choosing a reference architecture before understanding the high-difficulty drivers.
- Skipping the analysis step, so "done" is never actually demonstrated against the drivers.
- Diagrams without concrete technology or measurable rationale.
- One giant iteration instead of several bounded ones.
