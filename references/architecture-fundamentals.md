# Reference — Architecture fundamentals

Grounding for the whole method: what an architecture *is*, why it is worth the effort, and the
rules of thumb that separate a fit-for-purpose architecture from a fragile one.

## What a software architecture is

The software architecture of a system is **the set of structures needed to reason about the
system** — software elements, the relations among them, and the properties of both. Three
categories of structure, each a different engineering lever:

| Structure category | Elements / relations | You reason about… |
|--------------------|----------------------|-------------------|
| **Module** | implementation units (modules); *is-part-of*, *depends-on*, *is-a* | change impact, work assignment, subsetting, buildability |
| **Component-and-connector (C&C)** | things with runtime presence (components) + interaction mechanisms (connectors); *attachment*, data/control flow | performance, availability, security data-flow, scalability, concurrency |
| **Allocation** | software elements ↔ environment elements (hardware, file systems, teams); *allocated-to* | deployment, install, build layout, who-owns-what |

A **view** is a representation of one or more structures. Every system *has* an architecture;
it may or may not be documented. There is no inherently good or bad architecture — only more or
less **fit for a stated purpose**, which is why evaluation only makes sense against explicit
goals (the drivers).

## Why architecture matters (use these to justify the effort)

An architecture is the point of leverage on a project because it:

1. inhibits or **enables the driving quality attributes** — the single most important reason;
2. lets you **reason about and manage change** as the system evolves;
3. supports **early prediction** of system qualities (before code is committed);
4. improves **communication among stakeholders**;
5. carries the **earliest, hardest-to-change decisions**;
6. defines **constraints on implementation**;
7. shapes (and is shaped by) **organizational structure** (Conway's law);
8. is a basis for **incremental development** (a skeletal system grown by increments);
9. is the artifact the architect and PM use to reason about **cost and schedule**;
10. can be a **reusable, transferable model** — the core of a product line;
11. focuses attention on **assembling** components, not just building them;
12. **restricts the design vocabulary**, channelling developer creativity and cutting complexity;
13. is a foundation for **training** new team members.

## Rules of thumb for a "good" architecture

Failing one is not automatically fatal, but it is a warning sign to investigate. Apply them
proactively on greenfield work and as analysis heuristics on an existing system.

**Process**
- P1. Produced by **one architect or a small team with an identified technical lead** — for
  conceptual integrity — with a strong connection to the development team.
- P2. Built on a **prioritised list of well-specified quality attribute scenarios**; functionality
  matters less to structure than the QAs.
- P3. **Documented with views** chosen for the most important stakeholders' concerns; minimal at
  first, elaborated as needed.
- P4. **Evaluated early** for its ability to deliver the important quality attributes, and
  re-evaluated when the architecture or its environment changes.
- P5. Lends itself to **incremental implementation** — build a skeletal system that exercises the
  communication paths, then grow it.

**Structure / product**
- S1. **Well-defined modules** using information hiding and separation of concerns; each with an
  interface that hides the changeable parts, so teams can work independently.
- S2. Quality attributes achieved with **known patterns and tactics** for each attribute, unless
  requirements are genuinely unprecedented.
- S3. **Never depend on a particular version** of a commercial product or tool; if you must,
  isolate the dependency so a version change is cheap.
- S4. **Separate data producers from data consumers** — changes usually stay on one side.
- S5. Don't expect a **1:1 module ↔ component** mapping; concurrency multiplies components.
- S6. Every process **relocatable to another processor**, ideally at runtime (virtualization,
  cloud).
- S7. A **small number of simple, uniform component-interaction patterns** — do the same thing the
  same way throughout.
- S8. A **small, explicit set of resource-contention areas**, each with a stated resolution and,
  where a resource is a concern, an enforced budget (time budget, network-traffic budget).
