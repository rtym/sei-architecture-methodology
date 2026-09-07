# Reference — Glossary

Terms used across the skills and references, with the file that treats each in depth.

| Term | Meaning |
|------|---------|
| **Architecture** | the set of structures needed to reason about a system — elements, relations, and the properties of both (`architecture-fundamentals.md`) |
| **Structure / view / viewtype** | a *structure* is a set of elements + relations of one kind; a *view* is a representation of one or more structures; the three *viewtypes* are Module, Component-and-Connector (C&C), Allocation (`views-and-beyond.md`) |
| **ASR** (architecturally significant requirement) | a requirement the architecture would be *dramatically different* without; usually a QA requirement (`architectural-drivers.md`) |
| **Architectural driver** | an ASR, a primary functional requirement (use case), a constraint, an architectural concern, or the design purpose — the inputs to ADD (`architectural-drivers.md`) |
| **Business-goal scenario** | a structured seven-part expression of a business goal, elicited by PALM (`architectural-drivers.md`) |
| **Quality attribute (QA)** | a measurable / testable property of how well a system meets stakeholder needs beyond basic function (`quality-attribute-taxonomy.md`) |
| **Six-part scenario** | the SEI form for a QA requirement: source · stimulus · artifact · environment · response · response measure (`quality-attribute-taxonomy.md`) |
| **General vs concrete scenario** | *general* = system-independent template (the "portions" menu); *concrete* = filled in for this system (`quality-attribute-scenarios.md`) |
| **Utility tree** | the summary of QA ASRs **as a table**: quality attribute → refinement → leaf scenario, each leaf rated `(V, R)` (`architectural-drivers.md`) |
| **`(V, R)`** | priority pair on a utility-tree leaf: **business value** V and **technical risk** R, each H/M/L (`V ≈ Importance`, `R ≈ Difficulty`). `★` = `(H, H)` = architecturally significant |
| **Tactic** | a design decision that influences **one** QA response (`tactics-catalog.md`) |
| **Super-tactic** | a tactic so pervasive it appears in almost every pattern (encapsulate, restrict dependencies, use an intermediary, abstract common services, schedule resources, monitor) |
| **Architectural / design pattern** | a proven solution to a recurring design problem; usually affects several QAs and **bundles tactics** (`architecture-patterns.md`) |
| **Reference architecture** | a domain-proven blueprint for the whole system (`design-concepts.md`) |
| **Design concept** | anything chosen in ADD Step 4: reference architecture, deployment pattern, pattern, tactic, or externally developed component (`design-concepts.md`) |
| **Design roadmap** | the recommended iteration order by system type — greenfield-mature / greenfield-novel / brownfield (`add-method.md`) |
| **Design (architectural) backlog** | the living list of pending design actions, tracked on a Kanban board (Not Yet / Partially / Completely Addressed / Discarded) (`add-method.md`) |
| **Round vs iteration** | a *round* = the design activities in one development cycle; a round is one or more *iterations* (steps 2–7) (`add-method.md`) |
| **Value of Information (VoI)** | technique to size a prototyping effort: EVPI (value of a definitive experiment) and EVSI (value of an imperfect one) via Bayes (`add-method.md`) |
| **View packet** | the five-section documentation unit for one view: primary presentation · element catalog · context diagram · variability guide · rationale (`views-and-beyond.md`) |
| **Quality view** | a view formed by extracting the parts of the structural views relevant to one pervasive concern — security / communications / error-handling / reliability / performance (`views-and-beyond.md`) |
| **Overlay** | a combined view holding elements + relations from two or more views, each keeping its original type (`views-and-beyond.md`) |
| **Risk / non-risk** | a *risk* is a decision that may lead to undesirable consequences given the drivers; a *non-risk* is a decision deemed safe *under a stated assumption* (`atam-method.md`) |
| **Sensitivity point** | a decision with a marked effect on one QA response (`atam-method.md`) |
| **Tradeoff point** | a decision to which ≥ 2 QA responses are sensitive, one improving as the other degrades (`atam-method.md`) |
| **Risk theme** | a group of related risks revealing a systemic weakness; each mapped to the business goal(s) it threatens (`atam-method.md`) |
| **ATAM** | Architecture Tradeoff Analysis Method — a 9-step, 4-phase evaluation by external evaluators (`atam-method.md`) |
| **LAE** | Lightweight Architecture Evaluation — the same method run project-internally in ≤ a day (`atam-method.md`) |
| **CBAM** | Cost/Benefit Analysis Method — ranks candidate architectural strategies by ROI; the follow-on to ATAM (`atam-method.md`) |
| **Tactics-based questionnaire** | a per-QA analysis: for each tactic, Supported? / Design decisions + location / Risk / Rationale (`quality-attribute-taxonomy.md`) |
| **QAW** | Quality Attribute Workshop — an 8-step, stakeholder-driven method to elicit and prioritise scenarios before the architecture exists (`qaw-method.md`) |
| **PALM** | a workshop with the architect + business stakeholders to elicit business goals and derive the QAs they imply (`architectural-drivers.md`) |
| **Architecture debt** | technical debt whose root cause is spread across files and their relations; found via a design structure matrix + anti-patterns (`architecture-in-the-lifecycle.md`) |
| **DSM** (design structure matrix) | a files × files matrix of structural + evolutionary dependencies, used to find hotspots (`architecture-in-the-lifecycle.md`) |
| **Iteration 0** | a few ADD iterations before increments start, to set the major patterns / frameworks / structure (`architecture-in-the-lifecycle.md`) |
| **MTBF / MTTR** | mean time between failures / mean time to repair; steady-state availability ≈ MTBF / (MTBF + MTTR) (`quality-attribute-scenarios.md`) |
| **RPO / RTO** | recovery point objective (max data loss) / recovery time objective (max downtime) |
