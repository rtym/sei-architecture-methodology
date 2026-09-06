# Reference — Quality Attribute Workshop (QAW)

Source: Barbacci et al., *Quality Attribute Workshops (QAW), Third Edition*, CMU/SEI-2003-TR-016.

## What it is

A facilitated, **stakeholder-driven** method to discover, refine and prioritise quality-attribute
requirements as **scenarios**, applied **before** the software architecture is complete (typically
after requirements are somewhat firm but early enough to influence design). It is **system-centric**
— not tied to any one subsystem — and involves stakeholders beyond the architect.

## Roles

- **Facilitators** (2 recommended): run the steps, own the scenario list, remain neutral on
  content. One drives discussion, one records.
- **Stakeholders**: anyone with a vested interest — sponsor/customer, program manager, architects,
  developers, integrators, testers, maintainers, operators, end-user representatives, security,
  owners of interfacing systems.

## Inputs

Business/mission drivers, the system's requirements/context, any architectural plans that exist,
architectural constraints.

## The eight steps

1. **QAW presentation and introductions.** Facilitators explain QAW motivation, the process, and
   the outputs. Everyone introduces themselves and their role/concerns.
2. **Business/mission presentation.** A stakeholder (usually the sponsor's representative)
   presents the business context: high-level functional requirements, constraints, and quality
   attributes of concern (~ one hour).
3. **Architectural plan presentation.** Someone presents the system's architectural plans as they
   stand — context, key technical constraints, existing designs, interfaces. May be brief or
   "nothing yet".
4. **Identification of architectural drivers.** Facilitators share the list of key architectural
   drivers they distilled from steps 2–3 (quality attributes, high-impact functional
   requirements, constraints). Stakeholders clarify, add, remove, correct. Consensus list.
5. **Scenario brainstorming.** Round-robin: each stakeholder, in turn, contributes one scenario.
   Facilitators ensure each scenario has (at minimum) a stimulus and a response, and that the
   architectural drivers from step 4 are each represented. Multiple round-robin passes; continue
   until ideas thin out (target ≈ 2× the number of stakeholders, often more). Wording is captured
   verbatim; no refinement yet.
6. **Scenario consolidation.** Similar scenarios are merged with stakeholder consent — reduces
   redundancy before voting. Record what merged into what. Never merge over an objection.
7. **Scenario prioritisation.** Each stakeholder is allocated votes equal to **30 % of the number
   of consolidated scenarios, rounded up**. Voting is done in two passes (allocate, then tally).
   A stakeholder may spend multiple votes on one scenario. Scenarios are ranked by total votes.
8. **Scenario refinement.** Starting from the highest-voted, refine as many as time permits
   (often top 4–6). For each, document:
   - the **six-part scenario**: stimulus, stimulus source, environment, artifact, response,
     response measure;
   - the **business goals** behind it;
   - the relevant **quality attributes**;
   - a set of **questions** about how the architecture will (or will not) satisfy it;
   - **issues** — concerns, assumptions, risks raised during discussion.

## Outputs

- The list of architectural drivers (step 4).
- The raw brainstormed scenarios (step 5).
- The consolidated scenarios and the merge map (step 6).
- The prioritised (voted) scenario list (step 7).
- The refined top scenarios with questions and issues (step 8).

## What the results are used for

A stakeholder-interview / QAW output (a list of architectural drivers + a group-prioritised set
of QA scenarios) serves five purposes:

1. refine the system and software requirements;
2. understand and clarify the architectural drivers;
3. provide the **rationale** for design decisions the architect later makes;
4. guide the development of prototypes and simulations;
5. influence the **order** in which the architecture is developed.

## After the QAW

Refined scenarios feed:
- the **architectural drivers** register (`<ATTR>QA-n`),
- **ADD** as iteration drivers,
- later, **ATAM** — the QAW scenarios seed the utility tree and Phase-2 brainstorming.

The QAW is one structured form of "gathering ASRs by interviewing stakeholders" — see
`references/architectural-drivers.md` for the other three ways (requirements-doc sniffing, PALM
business-goal workshop, the architect's own utility tree) and the "play dumb" technique for a
stakeholder who says *"I don't know what that requirement should be."*

## Facilitation tips

- Keep the architectural-driver list visible throughout so brainstorming stays on target.
- Push every scenario toward a **measurable** response before step 8 ends.
- Time-box refinement per scenario (~15 min); park deep design debates as "issues".
- If stakeholders can't attend, a single proxy can relay per-stakeholder input, but note the
  reduced confidence in the vote.
