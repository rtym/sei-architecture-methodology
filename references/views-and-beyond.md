# Reference — Documenting Software Architectures: Views and Beyond (V&B)

Source: Clements, Bachmann, Bass, Garlan, Ivers, Little, Merson, Nord, Stafford —
*Documenting Software Architectures: Views and Beyond*, 2nd ed. Aligns with ISO/IEC/IEEE 42010.

## Central principle

> Documenting an architecture is a matter of documenting the relevant **views**, then adding
> documentation that applies to more than one view or to the whole package.

A **view** is a representation of a set of system elements and the relations among them, chosen to
serve particular stakeholder concerns. You don't document "the architecture" in one picture; you
document a curated set of views plus connective tissue.

**The golden rule: know your reader.** Documentation is a love letter you write to your future
self and to every stakeholder who will build, test, analyse, operate, or evolve the system.
Design and documentation are ideally the same piece of work — the language you use to explain
the architecture is the language you use to design it. "Documentation" does not mean a printed
book: an online, searchable, comment-enabled form (a wiki) is usually ideal.

## Four uses of architecture documentation

The uses determine what information to capture:

1. **Education** — introduce the system to new team members, external analysts, a new architect,
   or the customer you are pitching for funding.
2. **Communication among stakeholders** — the primary vehicle; its precise use depends on which
   stakeholders are talking. The most avid future reader is the **future architect** (possibly
   you), who needs the design decisions and *why* they were made.
3. **Basis for analysis and construction** — tells implementers what to build and how it wires
   together; gives analysts the information (resource consumption, scheduling, dependencies,
   failure rates) to evaluate security, performance, availability, modifiability.
4. **Forensics** — after an incident, the flow of control and the interface/component specs give
   the "as executed" picture needed to find the immediate and underlying cause.

Documentation is both **prescriptive** (for audiences whose decisions are still open — it
constrains) and **descriptive** (for audiences recounting decisions already made).

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
laid out? who is responsible for what? An allocation view is **static** (a fixed allocation) or
**dynamic** (shows the conditions and triggers under which the allocation changes — e.g. a
load-balancer creating processes on another machine as load rises).

### Summary of the three structural viewtypes

| | Elements | Relations | Constraints | Typical usage |
|---|----------|-----------|-------------|---------------|
| **Module** | implementation units with a coherent set of responsibilities | *is-part-of*, *depends-on*, *is-a* | may restrict visibility between modules | construction blueprint; change-impact analysis; incremental-dev planning; requirements-traceability; communicating the code base; work assignments / schedule / budget; data model |
| **C&C** | components (principal processing units + data stores); connectors (pathways of interaction — links, protocols, info flows, shared-storage access) | *attachment* (components ↔ connectors, forming a graph); attachments only between **compatible** component/connector types; a connector cannot stand alone | show how the system works at runtime; guide development of runtime elements; reason about runtime QAs (performance, availability) |
| **Allocation** | a software element (with properties *required* of the environment) ↔ an environmental element (with properties *provided* to the software) | *allocated-to* (a software element mapped to an environmental element; may be many-to-many) | varies by view | reason about performance / availability / security / safety; distributed development & work allocation; concurrent access to versions; install form and mechanism |

**Module properties** worth recording alongside a module view: name (may encode its position in
the decomposition, `A.B.C`), responsibilities (traced to requirements), implementation
information (mapping to source-code units/files, test information, management/schedule info,
implementation constraints), and revision history.

**C&C element properties** worth defining (to support the view's intended analysis): reliability
(failure likelihood), performance (response time / bandwidth / latency / jitter), resource
requirements (processing, storage, energy), functionality, security features, concurrency
(separate process/thread — for deadlock/bottleneck analysis), runtime extensibility.

### Quality views — a fourth kind

The three structural viewtypes guide developers, but when a quality attribute or stakeholder
concern is **pervasive**, its solution is spread across several structures that are awkward to
combine. A **quality view** is formed by *extracting the relevant pieces of the structural
views and packaging them together* for a specific concern. Common ones:

- **Security view** — every element with a security role, how they communicate, security data
  stores, security-relevant repositories, security protocols, where humans interact with
  security, and how the system responds to specific threats.
- **Communications view** — for globally dispersed / heterogeneous systems: all
  component-to-component channels, network channels, QoS parameters, areas of concurrency;
  supports deadlock / race-condition and bandwidth-allocation analysis.
- **Exception / error-handling view** — how components detect, report, and resolve faults;
  supports root-cause analysis.
- **Reliability view** — replication and switch-over mechanisms, timing, transaction integrity.
- **Performance view** — network-traffic models, max latencies per operation, buffering.

Quality views embody the ISO/IEC/IEEE 42010 philosophy: **views are driven by stakeholder
concerns.**

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

Comprehensive architecture documentation includes, in addition to views and behaviour:

1. **Documentation roadmap** — what information is in the package and where; how it's organised;
   how a reader with a given concern should navigate it (scenario-based "where do I look").
2. **How the documentation is organised** / views chosen and why (view selection, mapped to
   stakeholder concerns).
3. **System overview** — what the system does; its context; primary requirements. Prose + a
   top-level picture. Orients a new reader.
4. **Mapping between views** — the associations across views are generally **many-to-many**
   (a module maps to several runtime elements; a runtime element maps to several modules).
   Capture them as **tables**: list the elements of the first view in a convenient lookup order,
   and **name the correspondence** the table depicts — "is implemented by" (C&C → module),
   "implements" (module → C&C), "included in" (decomposition → layered), "allocated to"
   (C&C → deployment node), "realises" (element → driver). This is where internal consistency
   is demonstrated.
5. **Documenting patterns** — for every pattern used: record that it is used, *why* it fits the
   problem, and how the successive design decisions instantiate it (those decisions manifest as
   named elements + relations in the structural views).
6. **Context diagram(s)** — one per view (or a top-level one): the scope of the view and the
   environment entities (humans, other systems, sensors/devices) it interacts with. Best for the
   initial picture of how the system or subsystem meets its environment.
7. **Variability guide** — how to exercise every built-in variation point in a view.
8. **Rationale** — why the design in a view is as it is (see below).
9. **Glossary and acronym list** — decode the specialized terms so all stakeholders speak the
   same language.
10. **Document control information** — issuing organization, current version, date/status, change
    history, and the procedure for submitting change requests. Usually in the front matter.
11. **Directory** — index of where each element/relation/design concept is defined and used.

## Documenting the rationale

When designing you make decisions to hit each iteration's goal: **selecting a design concept
from alternatives · creating structures by instantiating it · establishing relationships and
defining interfaces · allocating resources**. A diagram shows the *end product* of a thought
process, not the thought. Record the reasoning *as you make it* — if you leave it, you will not
remember why.

Take the **greatest care** with the decisions that drive a `(H,H)`/`(H,M)` quality-attribute
scenario's response measure. For each decision also record its **risks** so they can be
reviewed and possibly revisited, and **justify** it (most decisions are "good enough", not
optimal).

Minimum: a two-column table.

| Design decision and location | Rationale and assumptions (**include discarded alternatives**) |
|------------------------------|---------------------------------------------------------------|
| Introduce concurrency (tactic) in `TimeServerConnector` and `FaultDetectionService` | Concurrency is needed to receive and process several trap events simultaneously. |
| Use of the messaging pattern (a message queue) in the communications layer | The queue imposes a performance penalty, but some implementations are high-performance and it supports `<ATTR>QA-3`. Discarded: direct synchronous calls. |

Fuller (for critical systems): also record *what evidence justified the decision · who did what ·
why shortcuts were taken · why tradeoffs were made · what assumptions were made.*

## Stakeholders and the views they need

Identifying the real stakeholders is an architect's obligation; the list below is a starting
point.

| Stakeholder | Cares about | Views they typically want |
|-------------|-------------|---------------------------|
| **Project manager** | schedule, resource/work assignment, contingency to release a subset | module (decomposition, uses/layered); allocation (deployment, work-assignment); top-level context + system overview |
| **Developer** | which elements to build, their data model, their interfaces and neighbours, reusable code assets, constraints | module (decomposition, uses/layered, generalization); C&C (the components assigned + neighbours); allocation (deployment, implementation, install); context + interface docs + variability guide + rationale/constraints |
| **Tester / integrator** | correct black-box behaviour of the pieces that fit together; incremental subsets | module (decomposition, uses, data model); **all** C&C; allocation (deployment, install, implementation); context + interface + behaviour specs |
| **Designer of an interoperating system** | the provided/required operations and protocols | interface docs (from module and/or C&C views); the data model; top-level context diagrams |
| **Maintainer** | same as a developer, plus where a change lands and its ripple, plus the discarded alternatives | developer views + decomposition + uses + **rationale** |
| **End user** (or rep) | insight into what the system does and how to use it; can surface design discrepancies pre-deployment | C&C (flow of control / data transformation); allocation (deployment); context diagrams |
| **Analyst** | whether the design meets its quality objectives; inputs for evaluation methods and analytic tools | potentially any part — resource consumption, scheduling policies, dependencies, failure rates |
| **Infrastructure support** | what runs where; how to set up config management | module (decomposition, uses); C&C (various); allocation (deployment, install, implementation); variability guides |
| **Future architect** | *everything* — especially candid rationale and design decisions | all of it |

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

Documenting as separate views is divide-and-conquer, but many structures have strong
associations. The easiest way to merge is an **overlay**: one combined view holding elements and
relations from two or more views, each keeping the **type** it had in its constituent view. Do
it only when the association is tight and the result stays legible (≤ ~10 elements, one
abstraction level); don't overload it with mappings. Combinations that occur naturally:

- **C&C view + C&C view** — different C&C views tend to show different parts, or decomposition
  refinements of a component, and combine easily.
- **Deployment view + any C&C view that shows processes** — processes *are* the things deployed
  onto processors / VMs / containers.
- **Decomposition view + work-assignment / implementation / uses / layered view** — decomposed
  modules form the units of work, of development, and of the uses relation, and populate layers.

## Documenting behaviour

Structure diagrams show what the parts are; **behaviour** documentation shows how they interact
over time, and is required for reasoning about deadlock potential, deadline satisfaction, and
resource consumption. It belongs in §2.4 of a view packet (and §6 of the ADD architecture
document). Two families of notation:

**Trace-oriented** — a sequence of activities/interactions that is the system's response to one
stimulus in one state. Does not attempt to show *all* behaviour.
- **Use cases** — how actors use the system to reach a goal. UML gives the *diagram* (an
  overview of actors + behaviour); the *text* should carry: name + brief description, primary
  actor(s), secondary actors, flow of events, alternative flows, non-success cases.
- **Sequence diagram** — interactions among instances pulled from the structural docs; vertical
  = time, horizontal = instances (left→right in call order); solid filled arrowhead =
  synchronous, open arrowhead = asynchronous, dashed = return; activation bars show
  processing/blocked. Useful for finding where interfaces are needed. Not explicit about
  concurrency.
- **Communication diagram** — a graph of interacting elements with each interaction numbered by
  order; good for verifying the architecture can meet the functional requirements. Poor for
  concurrency.
- **Activity diagram** — a workflow of actions with conditional branching (diamond) and
  **concurrency** (fork/join bars); optionally annotate which element/actor performs each
  action. Use when control flow (not message passing on specific objects) is the point, and
  when concurrency matters (e.g. a performance analysis).

**Comprehensive** — shows the *complete* behaviour so all paths from initial to final state can
be inferred.
- **State machine** — states (boxes) and transitions (arrows). Each transition is labelled with
  the triggering **event**, optionally a **guard** `[condition]` (transition enabled only if
  true), and optionally an **action/effect** `/ effect` performed on transition. States may have
  entry/exit actions. Models one element's runtime modes and its timed reactions to internal and
  environmental stimuli.

Every behaviour diagram is followed by a plain-English paragraph naming the scenario, the
trigger, and the outcome — the diagram supports the prose, it does not replace it.

## Practical considerations (form, distribution, evolution)

- **Modeling tools** — commercial tools (SysML is common) offer multi-user access, version
  control, syntactic/semantic model checking, trace links to requirements/tests, and sometimes
  code generation. Weigh the licence cost against what building those capabilities would cost.
- **Online / hypertext / wiki** — structure as short pages (one screen) over a deeper structure:
  an overview page linking to detail. A wiki lets many stakeholders **comment and clarify** while
  only selected people can **change** — set the permissions accordingly.
- **Release strategy** — put documentation under version control like any artifact; the architect
  issues releases to support major milestones, far enough ahead that developers can act on them
  (e.g. revised docs at the end of each sprint / with each incremental release).
- **Documenting architectures that change dynamically** (runtime plug-ins, dynamic
  discovery/binding, high-frequency deploy) — the architecture changes faster than any doc
  cycle, so:
  - **document what is true of every version** — the invariants (a plug-in must have *this*
    interface and go in *this* slot). The doc becomes a description of the constraints any
    compliant version must meet.
  - **document the ways the architecture is allowed to change** — usually "add new components,
    replace components with new implementations": put this in the **variability guide**.
  - **generate interface documentation automatically** — with explicit interface mechanisms
    (e.g. protocol buffers) the definitions are always current; load them into a searchable
    store so revision histories and cross-references are available.
- **Traceability** — link each significant design decision to the ASR or business goal that led
  to it, and keep the links in the documentation (a table, or tool-supported). When **every ASR
  is covered** by the trace links, you have assurance the architecture part is right.

## "Preliminary documentation during design" (from ADD)

Don't treat documentation as a phase after design. During ADD Step 6, produce *just enough*:
record responsibilities as you identify elements, record decisions as you make them (the
two-column rationale table), sketch the views that carry this iteration's decisions. Elaborate
into full view packets when the view set stabilises.

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
