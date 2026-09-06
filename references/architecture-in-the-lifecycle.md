# Reference — Architecture in the project lifecycle

Architecture is a means to an end, practised inside a real project. This note covers architecture
debt, how much design to do up front (Agile), distributed development, and the architect's role
and competence.

## Architecture debt and hotspots

Architecture debt is a form of technical debt whose root causes are **distributed across several
files and their relationships**, so it is harder to see than code-level debt.

**Do you have a debt problem?** Build a **design structure matrix (DSM)** — files on both rows
and columns, cells annotated with the dependency type:
- **structural** dependencies (calls / implements / inherits), from a static-analysis tool;
- **evolutionary** dependencies (two files change together in a commit), from the VCS history.

A healthy system has a **sparse, roughly lower-triangular** DSM (each file depends only on
lower-level files; no cycles). Debt shows up as a **dense** matrix, entries **above the
diagonal**, and strong **evolutionary coupling between structurally unrelated files**.

**Hotspots** — sets of elements that make an outsized contribution to maintenance cost. Find
them by looking for six recurring **architecture anti-patterns**:

| Anti-pattern | Signature in the DSM |
|--------------|----------------------|
| **Unstable interface** | an influential file (many dependents) that changes frequently *with* its dependents |
| **Modularity violation** | structurally independent files that keep changing together |
| **Unhealthy inheritance** | a parent depends on a child; or a client depends on both a parent and its children |
| **Cyclic dependency / clique** | a set of files forming a strongly connected graph |
| **Package cycle** | two or more packages depend on each other instead of forming a hierarchy |
| **Crossing** | a file with high fan-in *and* high fan-out that co-changes heavily with both |

Not every file is in a hotspot — a hotspot is a *cluster* tightly coupled to itself and
decoupled from the rest. Each cluster is a refactoring candidate.

**Quantify the debt.** Weight each anti-pattern by the bug fixes and churn its files carry.
Estimate the refactoring cost (person-months) and the expected saving (future churn avoided,
assuming a refactored file reverts to the project-average bug rate). Compare → ROI. In practice
these refactorings pay back several times over in feature velocity and bug-fix time.

**Automate it** — issue-tracker export + VCS log + reverse-engineered dependencies → build DSM →
detect anti-patterns → compute per-hotspot debt → run in CI so debt is monitored continuously.
The quantitative output is the business case to give the PM for a refactoring.

`/atam` findings and this DSM analysis are complementary: ATAM reasons about the design against
quality-attribute scenarios; the DSM reasons about the code's actual coupling and change history.

## How much architecture up front? (Agile)

The question is not *whether* to do architecture but *how much before coding starts*. The
"right" amount rises with project size, functional complexity, demanding quality attributes,
requirement volatility / domain novelty, and degree of distributed development.

Three stances:
- **Big Design Up Front (BDUF)** — all design effort first. Wrong for volatile requirements.
- **Emergent** — no up-front design; the architecture "emerges" from coding. Works only for
  small, simple systems that can turn on a dime and refactor freely. For medium/large systems it
  produces *an* architecture — the wrong one — because security, performance, safety, etc.
  cannot be bolted on late.
- **Iteration 0 (recommended)** — a few **ADD** iterations before increments start, focused on
  the major patterns (a reference architecture if apt), frameworks, and components; enough to
  structure the project, set work assignments and team formation, and cover the hardest quality
  attributes. When a driving quality-attribute requirement then changes, use a **spike** — a
  time-boxed, throwaway task in a separate branch — to answer the question before committing.

Of the 12 Agile principles, an architecture-centric reading agrees strongly with six, partly
with four, and disagrees with two: *"the best architectures emerge from self-organizing teams"*
(no — they are consciously designed by skilled architects) and *"face-to-face conversation is
the most efficient way to convey information"* (no — interfaces, protocols, and structures must
be written down, and the maintenance team will not be the original team). SAFe's **intentional
architecture** (planned strategies + inter-team design guidance) balanced against emergent
design is the same idea at enterprise scale.

## Distributed development

When teams are spread across sites / time zones / organizations:
- **Allocation of responsibilities to teams** matters more than in co-located work — it is a
  first-class architectural decision (a work-assignment view).
- **Minimise cross-team module dependencies** — a dependency between modules owned by distant
  teams needs coordination that used to be a hallway conversation and is now a scheduled call at
  someone's midnight.
- **Documentation matters more** — remote teams lack the informal coordination channels, so they
  must rely on well-written, well-disseminated documentation, and people must take the initiative
  to talk when in doubt.
- Coordination methods, richest to leanest: informal contact (co-located only) · meetings · async
  electronic (email, wiki, chat) · documentation. Pick per infrastructure, culture, language,
  time zones, and how many teams depend on a module.

## The architect's role and competence

- **Architect vs. project manager** — complementary: the PM owns the **external-facing**
  administrative view (budget, schedule, staffing, reporting risk up); the architect owns the
  **internal technical** view (and reflects external stakeholder concerns down to developers).
  The PM turns to the architect for input across the PMBOK knowledge areas.
- **Architecture competence rests on a triad**: **duties** (what the architect does — design,
  document, evaluate, mentor, negotiate, keep drivers current), supported by **skills** (think
  abstractly, communicate clearly, negotiate, lead) and **knowledge** (patterns, tactics,
  technologies, standards, quality attributes, ISO/IEC/IEEE 42010, the cloud, …). Improve
  competence by: gaining experience carrying out the duties (apprenticeship, not just
  education); developing the non-technical skills; and continuously mastering and refreshing the
  body of knowledge.
- **Never make a work breakdown structure the first project artifact** — the architecture (its
  structures and the work-assignment view derived from them) should inform the WBS, not the
  reverse.
