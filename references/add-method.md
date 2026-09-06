# Reference — Attribute-Driven Design (ADD 3.0)

Primary source: Cervantes & Kazman, *Designing Software Architectures: A Practical Approach*
(2nd ed., 2024). Earlier: Wojcik et al., *ADD 2.0*, CMU/SEI-2006-TR-023.

## Core idea

Architecture design is a **systematic, iterative** activity. Each iteration takes a bounded goal
and a prioritised set of drivers, chooses and instantiates design concepts to satisfy them,
sketches views, and analyses the result. Design is decomposition guided by quality attributes,
not just functionality.

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

1. **Review inputs.** Confirm purpose, primary FRs, QAS, constraints, concerns.
2. **Establish the iteration goal by selecting drivers.** Pick the subset of drivers this
   iteration will address. Early iterations favour drivers that are both high-importance and
   high-difficulty. The goal is one sentence.
3. **Choose one or more elements of the system to refine.** Iteration 1 of a greenfield system =
   the whole system. Later = a specific module/service/component produced earlier.
4. **Choose one or more design concepts that satisfy the selected drivers.** Concept categories:
   - **Reference architectures** — domain-proven overall structures (e.g. web app 3-tier,
     microservices, event-driven, pipe-and-filter, service mesh, Lambda/serverless).
   - **Architectural / design patterns** — layers, ports & adapters, CQRS, saga, broker,
     publish-subscribe, MVC/MVVM, gateway, sidecar, strangler fig.
   - **Tactics** — fine-grained techniques per quality attribute: availability (redundancy,
     health check, failover, rollback, degradation), performance (caching, load balancing,
     bounded queues, concurrency, data locality), security (authenticate, authorize, encrypt,
     audit, limit exposure), modifiability (encapsulate, intermediary, restrict dependencies,
     defer binding), scalability (statelessness, partitioning, elastic pools).
   - **Externally developed components** — frameworks, middleware, cloud services, SaaS,
     libraries.
   Evaluate 2–4 alternatives per driver cluster with pros/cons; record why the chosen one wins
   and which were discarded, citing driver IDs.
5. **Instantiate architectural elements, allocate responsibilities, and define interfaces.**
   Turn the abstract concept into concrete named elements. For each: its responsibility, and its
   provided/required interfaces (operations, data, protocol, error semantics).
6. **Sketch views and record design decisions.** Produce/update the views that capture this
   iteration's decisions (context, container, component, sequence, deployment; module/C&C/
   allocation for fuller docs). Record decisions in an ADR-style log with rationale tied to
   drivers.
7. **Perform analysis of the current design and review the iteration goal.** For each selected
   driver: satisfied / partially / not addressed, with notes on risks and assumptions. Decide
   whether another iteration is needed and, if so, with which remaining drivers.

## Iteration planning (pragmatic extension)

ADD 3.0 does not prescribe an up-front plan, but drafting one — grouping drivers into a handful
of bounded iterations with a stated goal each — makes the end of design visible and keeps scope
honest. Iteration 1 is usually "establish the overall structure / choose the reference
architecture". Verify every driver ID is covered by at least one iteration before starting.

## Outputs

- The architecture: elements, responsibilities, relationships, interfaces.
- A set of views (C4 / UML), kept in the Architecture document.
- A design-decision (ADR) log with rationale traceable to drivers.
- Per-iteration analysis showing which drivers are satisfied.

## Common mistakes

- Designing structure from functionality alone, ignoring the QAS.
- Choosing a reference architecture before understanding the high-difficulty drivers.
- Skipping the analysis step, so "done" is never actually demonstrated against the drivers.
- Diagrams without concrete technology or measurable rationale.
- One giant iteration instead of several bounded ones.
