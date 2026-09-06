---
name: quality-attribute-workshop
description: >-
  Facilitate the SEI Quality Attribute Workshop (QAW) — the eight-step, stakeholder-driven method
  that elicits, brainstorms, consolidates, prioritises and refines quality attribute scenarios
  before a software architecture exists. Use when the user invokes /qaw or asks to run a QAW,
  facilitate a quality attribute workshop, or elicit scenarios with stakeholders.
version: 1.0.0
allowed-tools: [Read, Write, Bash, Glob]
---

# Quality Attribute Workshop (QAW)

Facilitate the SEI QAW. The QAW is **system-centric** and **stakeholder-focused**, and is run
*before* the architecture is created (or early, to inform it). You act as **facilitator**; the user
represents (or relays for) the stakeholders.

Output file: `architecture/qaw/qaw-report.md` (create the folder). Update it after every step.
Deep reference: `references/qaw-method.md`. Report template: `templates/qaw-report.md`.

**Keep prompts short.** Numbered lists for choices. One step at a time; announce each step in one line.

## Roles and inputs

- **Facilitators** (you): run the steps, own the scenario list, stay neutral on content.
- **Stakeholders** (user + named others): architects, developers, testers, integrators, operators,
  maintainers, product owner, sponsor, end-user reps, security, downstream-system owners.
- **Inputs**: business/mission drivers, any architectural plan or context that exists, a system
  description. Ask for these up front; read files the user points at.

## The eight steps

### Step 1 — QAW presentation and introductions
State the QAW purpose, the eight steps, and the expected outputs (raw scenarios, prioritised
scenarios, refined scenarios). Capture the **participant list** with each person's role and the
concerns they bring. Write it to the report.

### Step 2 — Business / mission drivers
The sponsor's representative presents: system context, business goals, key functional
requirements, constraints, and the quality attributes that matter most to the business. Record
business drivers as `BG-1…` and the named quality attributes. Confirm the summary.

### Step 3 — Architectural plan presentation
Whatever architectural information exists is presented: system boundary, key technical
constraints, existing context/plans, interfaces to external systems. If nothing exists yet, record
that and capture the constraints and context that *are* known.

### Step 4 — Identification of architectural drivers
You (facilitators) present a first-draft list of **architectural drivers** distilled from steps 2–3
— the quality attributes, high-impact functional requirements, and constraints most likely to
shape the architecture. Stakeholders add, remove, merge. Record the agreed list as `AD-1…`
mapped to business goals.

### Step 5 — Scenario brainstorming (round-robin)
Go around the participants; each contributes **one scenario per turn**. A scenario names a
stimulus, an environment, and a response. Aim for coverage across the step-4 drivers. Keep going
for multiple passes until ideas are exhausted (typically 2–3× the number of participants).
Number them `S-1, S-2, …` verbatim — do **not** polish yet.

To automate: when the user is relaying for a group, generate candidate scenarios per driver and
per stakeholder concern, present them as the round-robin output, and let the user cull/add.

### Step 6 — Scenario consolidation
Merge scenarios that are near-duplicates or clearly the same concern. Ask the group to agree on
each merge; never merge unilaterally over an objection. Record which `S-` IDs folded into which.
The consolidated list keeps its original IDs (with a note), or is renumbered `CS-1…` — pick one
and be consistent.

### Step 7 — Scenario prioritisation (voting)
Each stakeholder gets a vote budget = **30 % of the consolidated scenario count, rounded up**
(e.g. 12 scenarios → 4 votes each). Two passes:
1. Allocate all votes (a stakeholder may put multiple votes on one scenario).
2. Tally. Sort by total votes.

When relaying for a group, ask the user for per-stakeholder vote allocations, or for a single
merged prioritisation if that is all that is available. Record the vote table and the ranked list.

### Step 8 — Scenario refinement
Take the **top scenarios** (as many as time allows, usually 4–6). For each, produce:
- the **six-part form**: source of stimulus, stimulus, artifact, environment, response, response
  measure (numeric);
- **business goals** it supports;
- the **relevant quality attributes**, classified against **ISO/IEC 25010:2023**
  (characteristic + sub-characteristic — see `references/quality-attribute-taxonomy.md`);
- a **six-part UML scenario diagram** (use the `sei-diagrams` skill's *Quality attribute scenario
  diagram* pattern), rendered in the report and optionally to PNG;
- **questions** raised about how the architecture would achieve it;
- **issues** / concerns / assumptions surfaced during discussion.

## Outputs (all in the report)

1. Participant list with roles.
2. Business/mission drivers.
3. Architectural plan summary + constraints.
4. Agreed architectural drivers.
5. **Raw brainstormed scenarios** (`S-n`).
6. **Consolidated scenarios** with merge map.
7. **Prioritised scenarios** — vote table + ranked list.
8. **Refined scenarios** — six-part form + questions + issues for the top set.
9. Next steps (feed refined scenarios into ADD as drivers; schedule ATAM later).

## Rules

- Facilitator stays neutral on scenario *content*; drives *process* only.
- Never discard or merge a scenario without stakeholder agreement — record dissent.
- Raw scenario wording from step 5 is preserved verbatim; refinement happens only in step 8.
- Every refined scenario has a numeric response measure and cites ≥ 1 business goal.
- Vote budget is 30 % of consolidated count, rounded up — state the number explicitly.
- Write the report incrementally; each step appends its section.
- Hand off: the refined scenarios become the `<ATTR>QA-n` drivers for `/attribute-driven-design` and
  the `architectural-drivers` register.
- **Report format**: `qaw-report.md` is the working file. For the deliverable, ask the user
  **Markdown, HTML, or both** and build it with
  `scripts/build-report.sh architecture/qaw/qaw-report.md --format <fmt> --embed-diagrams
  --title "Quality Attribute Workshop — <system>"`.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until the generated artifact passes both:

1. **Automated**: `python tests/validate.py architecture/qaw/qaw-report.md` — exits 0 (from the plugin root, or point at
   the plugin's `tests/validate.py`). It checks IDs, structure, six-part scenarios with numeric
   measures, traceability with no orphans, diagram rules, and the deprecated-`QAS-` guard.
2. **Best-practice checklist**: walk the relevant section of
   `references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix,
   re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
