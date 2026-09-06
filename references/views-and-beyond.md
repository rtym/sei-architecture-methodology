# Reference — Documenting Software Architectures: Views and Beyond (V&B)

Source: Clements, Bachmann, Bass, Garlan, Ivers, Little, Merson, Nord, Stafford —
*Documenting Software Architectures: Views and Beyond*, 2nd ed. Aligns with ISO/IEC/IEEE 42010.

## Central principle

> Documenting an architecture is a matter of documenting the relevant **views**, then adding
> documentation that applies to more than one view or to the whole package.

A **view** is a representation of a set of system elements and the relations among them, chosen to
serve particular stakeholder concerns. You don't document "the architecture" in one picture; you
document a curated set of views plus connective tissue.

## The three viewtypes (categories of views)

### Module views
Elements are **implementation units** (modules). Relations: *is-part-of*, *depends-on*, *is-a*.
Styles:
- **Decomposition** — modules and submodules; supports understanding, work division, change impact.
- **Uses** — which modules use which; supports incremental development and subsetting.
- **Layered** — a constrained uses view; allowed-to-use relation between layers.
- **Generalization** — is-a relations; supports OO design, extension, reuse.
- **Data model** — data entities and their relationships.
- **Aspects** — cross-cutting concerns realised by aspects.

Answers: primary units of implementation? responsibilities? allowed dependencies? impact of a
change? how to subset the system?

### Component-and-Connector (C&C) views
Elements are **runtime components** (principal units of computation with runtime presence) and
**connectors** (interaction mechanisms). Relations: *attachment* (component ports to connector
roles). Styles:
- client-server, service-oriented (SOA / microservices), publish-subscribe, peer-to-peer,
  pipe-and-filter, shared-data (repository / blackboard), communicating-processes.

Answers: what are the major executing components and how do they interact? data stores? parallel
behaviour? how does the system achieve its runtime quality attributes (performance, availability,
security data-flow)? how can it be scaled or evolved at runtime?

### Allocation views
Map software elements to **non-software structures** in their environment. Relation: *allocated-to*.
Styles:
- **Deployment** — software (usually C&C) elements to hardware / execution environments; network.
- **Install** — components to the file/directory structure of the production environment.
- **Implementation** — modules to the development file/build structure.
- **Work assignment** — modules to the teams/people responsible.

Answers: where does each element execute? what hardware/network does it need? how is the build
laid out? who is responsible for what?

## The view template (a "view packet")

Document every view with the same structure:

1. **Primary presentation** — the main diagram (or table). Shows the elements and relations of
   the view. Use a consistent, legended notation. Show what's important; usually graphical.
2. **Element catalog** — details the elements shown:
   - 2.1 Elements and their properties (responsibilities, significant properties).
   - 2.2 Relations and their properties.
   - 2.3 Element interfaces (syntax, semantics, error handling; can reference an interface doc).
   - 2.4 Element behavior (sequence/state diagrams where structure isn't enough).
3. **Context diagram** — how this view's portion of the system relates to its environment.
4. **Variability guide** — the points of built-in variation (options, parameters, plug-in
   points, product-line variation) and how to exercise each.
5. **Rationale** — why the design reflected in this view is as it is; alternatives and why they
   were rejected; how the view supports the drivers.

## Documentation beyond views

Documentation that spans views or the whole package:

1. **Documentation roadmap** — what information is in the package and where; how it's organised;
   how a reader with a given concern should navigate it (scenario-based "where do I look").
2. **How the documentation is organised** / views chosen and why (view selection, mapped to
   stakeholder concerns).
3. **System overview** — what the system does; its context; primary requirements. Prose + a
   top-level picture. Orients a new reader.
4. **Mapping between views** — tables showing how elements in one view correspond to elements in
   another (e.g. a module realises which runtime components; a component deploys to which node).
   Demonstrates consistency; helps readers correlate.
5. **Rationale** — architecture-wide rationale not tied to a single view (major decisions,
   patterns, constraints satisfied). Often an ADR log.
6. **Directory** — index of elements/relations/design concepts (where each is defined and used),
   glossary, and acronym list.

## Notation — how formal to be

Pick the least formal notation that removes ambiguity for the intended reader:

- **Informal** — boxes and lines with a legend. Fast; fine for a sketch or a rarely-changing
  view. The risk is that "what a box means" drifts.
- **Semi-formal** — a defined vocabulary of element and relation types with consistent visual
  rules: **C4** for structural views, **UML** for behaviour (sequence, state, activity) and for
  use cases. This is the plugin's default; the `sei-diagrams` skill enforces the visual rules.
- **Formal** — an architecture description language with defined semantics. Use only when the
  cost of a misreading is high (safety, contracts) — rare in practice.

State the notation and include or reference a **key/legend** in every view (V&B rule 3).

## Combining views

Two views can be merged into one when they serve overlapping stakeholders and the combined
picture stays legible — e.g. a **deployment + install** view, or a small system's **module +
uses** view. A combined view is an *overlay*: it shows the elements of one view annotated with
information from another (a module box tagged with its runtime component and its node). Combine
to reduce reader effort; split again the moment the diagram passes ~10 elements or mixes
abstraction levels.

## Documenting behaviour

Structure diagrams show what the parts are; **behaviour** documentation shows what they do over
time, and belongs in §2.4 of a view packet (and §6 of the ADD architecture document):

- **Sequence diagram** — the ordered interactions among a fixed set of elements for one
  scenario (the dashboard read, the failover). Best for showing a path and its branches
  (`alt` / `opt`).
- **State machine** — the modes of one element and the events that move it between them
  (a circuit breaker: closed → open → half-open).
- **Activity diagram** — a workflow with decisions and parallelism, when control flow (not
  message passing) is the point.

Every behaviour diagram is followed by a plain-English paragraph that names the scenario, the
trigger, and the outcome — the diagram supports the prose, it does not replace it.

## Seven rules for sound documentation

1. Write documentation from the reader's point of view.
2. Avoid unnecessary repetition — say each thing once, in the most appropriate place, and
   cross-reference.
3. Avoid ambiguity — define your notation; provide a key/legend; define terms.
4. Use a standard, planned organisation, and tell readers what it is.
5. Record rationale — explain why, not only what.
6. Keep documentation current but not too detailed; review it periodically and on change.
7. Review documentation for fitness of purpose with the stakeholders who will use it.

## How much to document

Document a view if it carries architectural decisions that some stakeholder needs and that aren't
already evident elsewhere. Skip a view if it adds no information a stakeholder needs. But the
description as a whole must cover **all three viewtypes** — module, C&C, allocation — because each
answers questions the others cannot.

## Choosing views (the method)

1. Produce a candidate list: standard views for module (decomposition, uses/layered), C&C (the
   ones matching the system's runtime structures), and allocation (deployment, plus install /
   implementation / work-assignment if relevant).
2. Combine views that serve small stakeholder groups (e.g. a combined deployment + install view).
3. Prioritise the remaining views by stakeholder need and cost; document the high-value ones now,
   the rest as needed.
