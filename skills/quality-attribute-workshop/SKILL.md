---
name: quality-attribute-workshop
description: >-
  Facilitate the SEI Quality Attribute Workshop (QAW) — the eight-step, stakeholder-driven method
  that elicits, brainstorms, consolidates, prioritises and refines quality attribute scenarios
  before a software architecture exists. Use when the user invokes /qaw or asks to run a QAW,
  facilitate a quality attribute workshop, or elicit scenarios with stakeholders.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
user-invocable: false
---

# Quality Attribute Workshop (QAW)

Facilitate the SEI QAW. The QAW is **system-centric** and **stakeholder-focused**, and is run
*before* the architecture is created (or early, to inform it). You act as **facilitator**; the user
represents (or relays for) the stakeholders.

Output file: `architecture/qaw/qaw-report.md` (create the folder). Update it after every step.
Deep reference: `${CLAUDE_PLUGIN_ROOT}/references/qaw-method.md` (the QAW is one structured form of "gathering ASRs by
interviewing stakeholders" — `${CLAUDE_PLUGIN_ROOT}/references/architectural-drivers.md` covers the other three ways
and the "play dumb" technique for a stakeholder who says *"I don't know what that requirement
should be"*). Report template: `${CLAUDE_PLUGIN_ROOT}/templates/qaw-report.md`.

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
scenarios, refined scenarios). Take the **participant list** from `architecture/drivers/stakeholders.md`
(`ST-<n>`, role, concerns) if it exists; otherwise capture it here **and** create that file from
`${CLAUDE_PLUGIN_ROOT}/templates/stakeholders.md` so the later activities reuse it. Write it to the report.

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
stimulus, an environment, and a response, and is tagged with its **type**: *use-case* (an
anticipated use), *growth* (an anticipated change — load, features, platforms) or *exploratory*
(an extreme, stress or failure situation that exposes limits). Aim for coverage across the
step-4 drivers **and** across the three types. Keep going
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
  (characteristic + sub-characteristic — see `${CLAUDE_PLUGIN_ROOT}/references/quality-attribute-taxonomy.md`);
- a **six-part UML scenario diagram** — **horizontal `flowchart LR`** (use the `sei-diagrams`
  skill's *Quality attribute scenario diagram* pattern), source and PNG in
  `architecture/qaw/diagrams/scenario-CS-<id>.*`, rendered, visually verified and embedded as an
  image line;
- **questions** raised about how the architecture would achieve it;
- **issues** / concerns / assumptions surfaced during discussion.

### Step 9 — Build the quality attribute utility tree
After refinement, assemble the **utility tree as a table** — it is the summary of the workshop's
quality attributes and becomes the QA summary in the architectural drivers. **It is a table, not
a diagram.**

One row per leaf scenario, columns *Quality attribute (ISO/IEC 25010 characteristic) ·
Refinement (concern / sub-characteristic) · Leaf scenario (ID + response measure) · Priority
(V, R) · Status*.

- Every refined scenario (and every consolidated scenario that survived voting) is a leaf row.
- `(V, R)` = **business value** and **technical risk**, each `H`/`M`/`L`. Business value comes
  from the vote ranking + business-goal weight; technical risk is the architect's estimate.
  (`V ≈ Importance`, `R ≈ Difficulty`.) Mark a `(H, H)` leaf `★`.
- Follow the table with a **"Reading the tree"** note: a QA/refinement with no leaf → look for
  an unrecorded ASR; the `★` leaves get the most attention.
- Template: `${CLAUDE_PLUGIN_ROOT}/templates/utility-tree.md`.

Hand this tree to `/drivers` — it populates `architecture/drivers/quality-attributes/utility-tree.md`
and is referenced from the drivers `README.md`. ATAM step 5 reuses the same structure.

### Step 10 — Hand-off table and package index
Close the report with a **hand-off table**: every `CS-<id>` (refined or merely consolidated) →
the `<ATTR>QA-<n>` it becomes, and every `AD-<n>` → the register ID (`BG-` / `UC-` / `CON-` /
`<ATTR>QA-`) it maps to. Workshop IDs never leave the report otherwise, and the register would
carry no trace of where a scenario came from. Then update the `/qaw` row and change log of the
package index `architecture/README.md` (create it from
`${CLAUDE_PLUGIN_ROOT}/templates/architecture-readme.md` if absent).

## Outputs (all in the report)

1. Participant list with roles.
2. Business/mission drivers.
3. Architectural plan summary + constraints.
4. Agreed architectural drivers.
5. **Raw brainstormed scenarios** (`S-n`).
6. **Consolidated scenarios** with merge map.
7. **Prioritised scenarios** — vote table + ranked list.
8. **Refined scenarios** — six-part form + horizontal scenario diagram + questions + issues.
9. **Quality attribute utility tree** — a table, one leaf per row, every leaf `(V, R)` + status.
10. **Hand-off table** — `CS-<id>` → `<ATTR>QA-<n>`, `AD-<n>` → register IDs.
11. Next steps (run `/drivers` from the hand-off table, then ADD; schedule ATAM).

## Rules

- Facilitator stays neutral on scenario *content*; drives *process* only.
- Never discard or merge a scenario without stakeholder agreement — record dissent.
- Raw scenario wording from step 5 is preserved verbatim, each tagged use-case / growth /
  exploratory; refinement happens only in step 8.
- Every `CS-` and `AD-` ID appears in the hand-off table mapped to a register ID.
- Every refined scenario has a numeric response measure and cites ≥ 1 business goal.
- Vote budget is 30 % of consolidated count, rounded up — state the number explicitly.
- Write the report incrementally; each step appends its section.
- Hand off: the refined scenarios become the `<ATTR>QA-n` drivers for `/attribute-driven-design` and
  the `architectural-drivers` register.
- **Report format**: `qaw-report.md` is the working file. For the deliverable, ask the user
  **Markdown, HTML, or both** and build it with
  `${CLAUDE_PLUGIN_ROOT}/scripts/build-report.sh architecture/qaw/qaw-report.md --format <fmt> --embed-diagrams
  --title "Quality Attribute Workshop — <SystemName>"`.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until the generated artifact passes both:

1. **Automated**: `python ${CLAUDE_PLUGIN_ROOT}/tests/validate.py architecture/qaw/qaw-report.md` — exits 0. It checks IDs, structure, six-part scenarios with numeric
   measures, traceability with no orphans, diagram rules, and the deprecated-`QAS-` guard.
2. **Best-practice checklist**: walk the relevant section of
   `${CLAUDE_PLUGIN_ROOT}/references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix,
   re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
