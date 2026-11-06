---
name: quality-attribute-workshop
description: >-
  Facilitate the SEI Quality Attribute Workshop (QAW) — the eight-step, stakeholder-driven method
  that elicits, brainstorms, consolidates, prioritises and refines quality attribute scenarios,
  guided by a question script per step, per quality attribute and per stakeholder role. Runs from
  a blank page or over existing drivers and documentation (refresh mode), in a two-day, one-day,
  half-day or remote format, with generated agenda, vote tally, progress and scenario checks. Use
  when the user invokes /qaw or asks to run a QAW, facilitate a quality attribute workshop,
  elicit or revisit quality requirements with stakeholders, or asks which questions to ask in one.
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

**Question guide:** `${CLAUDE_PLUGIN_ROOT}/references/qaw-question-guide.md` is the facilitator's
script — the questions for every step, per ISO/IEC 25010 characteristic, per kind of system
(AI, multi-tenant SaaS, data, mobile, regulated data, IoT, public APIs), per stakeholder role, and
for testing documentation that already exists. Read it before Step 0 and ask from it at every
step: never open a step with "what are your quality requirements?".

**Facilitation playbook:** `${CLAUDE_PLUGIN_ROOT}/references/qaw-facilitation-playbook.md` is how
to run the room — the four formats and their timeboxes, who does what, what to prepare, what to
do and say in difficult moments, the scenario smells, and what happens after the workshop. Turn
to its *Difficult moments* table whenever the session stalls or one voice takes over.

**Keep prompts short.** Numbered lists for choices. One step at a time; announce each step in one line.

## Roles and inputs

- **Facilitators** (you): run the steps, own the scenario list, stay neutral on content.
- **Stakeholders** (user + named others): architects, developers, testers, integrators, operators,
  maintainers, product owner, sponsor, end-user reps, security, downstream-system owners.
- **Inputs**: business/mission drivers, any architectural plan or context that exists, a system
  description. Ask for these up front; read files the user points at.

## Rely on the documentation available

The workshop is guided by whatever documentation exists — never run it as if the page were blank
when it is not. Before every step:

1. **Look first.** Check the inputs found in Step 0 (drivers register, stakeholder register,
   earlier QAW report, architecture docs and ADRs, brownfield intake, briefs and requirements the
   user named) for what the step's questions would ask.
2. **Do not ask what the documents answer.** Present the documented answer with its source
   (file and section, or driver ID) and ask only whether it still holds — "The brief says 10 000
   users within 12 months (BG-1). Is that still the target?" — instead of the open question.
3. **Ask openly only about the gaps** — what no document covers, or what the group says is out
   of date.
4. **Cite the source in the report.** Every answer taken from a document names where it came
   from; an answer from the room is attributed to the participant.
5. **Record contradictions, do not resolve them silently.** When a stakeholder contradicts a
   document, write down both and the decision the group made; a document the group calls out of
   date is listed as such in the Starting point.

## Generate the workshop artifacts

`${CLAUDE_PLUGIN_ROOT}/scripts/qawkit.py` builds the workshop's working files and checks from
what is already documented and from the report, deterministically (same inputs, same output).
Use it instead of writing these files or adding up votes by hand; review each file before
handing it out.

Every command below is `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/qawkit.py <command> …`.

| When | Command | Writes |
|------|---------|--------|
| Before Step 1 (after Step 0) | `prep --drivers architecture/drivers --system "<SystemName>" --date <YYYY-MM-DD> --out architecture/qaw/qaw-prep.md` — add `--previous-report architecture/qaw/qaw-report-<date>.md` in refresh mode and `--domain <key>[,<key>]` for the kind of system (`ai`, `saas`, `data`, `mobile`, `regulated`, `iot`, `api`) | `qaw-prep.md` — documented answers to confirm with their sources, the ISO/IEC 25010 characteristics with no scenario and their questions, those the last workshop set aside with its reasons, the system-type questions, each participant's role questions, open parked questions from the last workshop |
| Before Step 1 | `agenda --format <two-day\|one-day\|half-day\|remote> --date <YYYY-MM-DD> --start 09:00 --system "<SystemName>" --out architecture/qaw/qaw-agenda.md` | `qaw-agenda.md` — dated, timed blocks from the playbook's timeboxes; later days fall on working days |
| At any time | `status architecture/qaw/qaw-report.md --date <today>` | to stdout: which steps are done, the next step, drivers and scenario types with no scenario, characteristics with no leaf, open and overdue parked questions |
| At Step 7, after consolidation | `ballot architecture/qaw/qaw-report.md --out architecture/qaw/qaw-vote-sheet.md` | `qaw-vote-sheet.md` — one row per `CS-<n>`, one column per participant, the vote budget computed |
| At Step 7, after the vote | `tally architecture/qaw/qaw-vote-sheet.md --out architecture/qaw/qaw-tally.md` | `qaw-tally.md` — totals, unspent votes and the ranking, as the block that replaces Step 7's budget line, table and ranking; exits 2 when someone voted over budget |
| After Step 8, and in the quality gate | `lint architecture/qaw/qaw-report.md` | to stdout: scenario smells (empty part, generic source, no number, vague word, no business goal, characteristic neither covered nor recorded as not significant), each with the guide's question to ask; exits 1 while findings remain |
| After the hand-off table | `summary architecture/qaw/qaw-report.md --out architecture/qaw/qaw-summary.md` | `qaw-summary.md` — one page for the sponsor: counts, ranking, `(H, H)` leaves, refined scenarios, open questions |

`prep` suggests an entry mode from the register; the Step 0 decision is still yours. With no
drivers register yet (greenfield), skip `prep` and use the question guide directly. The script
exits 2 with a one-line reason when an input is missing; fix the input, never hand-edit around it.
When the user asks where the workshop stands, run `status` and answer from its output.

## Asking the questions

Each step below names its section of the question guide. Ask one question at a time, play the
answer back in one line, and record it in the report. A question nobody present can answer goes
to the report's **Parked questions** table as `PQ-<n>` with the role that can answer it, an owner
and a due date — never fill the gap with an invented number. When the user is relaying for a
group, offer the step's questions as a numbered list and let them answer the ones they can.

## Step 0 — Choose the entry mode

Before Step 1, look for what already exists — `architecture/drivers/` (register, stakeholders,
utility tree), a previous `architecture/qaw/qaw-report.md`, `architecture/docs/`,
`architecture/brownfield-intake.md`, and any brief or requirements document the user named — and
ask the mode questions from the guide's *Choose the entry mode* section. Then pick one:

- **greenfield** — nothing documented. Every step starts from open questions.
- **partial** — some inputs exist (a brief, a codebase, loose scenarios). Read them first, present
  what they say as a draft in Steps 2–4, and ask the group to correct it. Anything derived from
  code is marked *derived — confirm* (`${CLAUDE_PLUGIN_ROOT}/references/brownfield-intake.md`).
- **refresh** — a drivers register with quality attribute scenarios exists. Steps 2–4 test the
  existing drivers with the guide's *Testing what already exists* questions instead of eliciting
  them from scratch; Step 5 starts from the existing scenarios and spends the round on gaps
  (ISO/IEC 25010 characteristics with no scenario, drivers with no scenario, what changed); Step 7
  votes on old and new scenarios together.

If a previous `qaw-report.md` exists, rename it `qaw-report-<its date>.md` in the same folder
(its diagram links keep working) and start a new report. Record the mode and every input used in
the report's **Starting point** section, linking the previous report if there is one.

Then agree the **format** with the user from the playbook's *Choose a format* table, record it in
the report header (`- **Format**: one-day`), and generate the agenda with `qawkit.py agenda`. Ask
which kind of system this is; each matching system type in the question guide becomes a
`--domain` key for `prep`.

## The eight steps

### Step 1 — QAW presentation and introductions
State the QAW purpose, the eight steps, and the expected outputs (raw scenarios, prioritised
scenarios, refined scenarios). Take the **participant list** from `architecture/drivers/stakeholders.md`
(`ST-<n>`, role, concerns) if it exists; otherwise capture it here **and** create that file from
`${CLAUDE_PLUGIN_ROOT}/templates/stakeholders.md` so the later activities reuse it. Write it to the report.
Ask the guide's *Step 1* questions of each participant, and record roles that are absent — their
concerns become parked questions or the role-specific questions in the guide.

### Step 2 — Business / mission drivers
The sponsor's representative presents: system context, business goals, key functional
requirements, constraints, and the quality attributes that matter most to the business. Record
business drivers as `BG-1…` and the named quality attributes. Confirm the summary.
Ask the guide's *Step 2* questions. In **refresh** mode, test each existing `BG-<n>` instead:
still current, target still right, anything new; a goal that no longer applies is marked
`retired`, never deleted.

### Step 3 — Architectural plan presentation
Whatever architectural information exists is presented: system boundary, key technical
constraints, existing context/plans, interfaces to external systems. If nothing exists yet, record
that and capture the constraints and context that *are* known.
Ask the guide's *Step 3* questions; with no plan at all, ask only the constraint, operations and
team-skills questions.

### Step 4 — Identification of architectural drivers
You (facilitators) present a first-draft list of **architectural drivers** distilled from steps 2–3
— the quality attributes, high-impact functional requirements, and constraints most likely to
shape the architecture. Stakeholders add, remove, merge. Record the agreed list as `AD-1…`
mapped to business goals.
Ask the guide's *Step 4* questions. Then check coverage against all nine ISO/IEC 25010
characteristics: for each one with no driver, ask its opening questions from the guide's
*Questions by quality attribute* and record the answer — a driver, or a line naming the
characteristic as "not significant here" with the reason (that exact phrase is what `status`
and `lint` look for). Add the questions of each system type that applies.

### Step 5 — Scenario brainstorming (round-robin)
Go around the participants; each contributes **one scenario per turn**. A scenario names a
stimulus, an environment, and a response, and is tagged with its **type**: *use-case* (an
anticipated use), *growth* (an anticipated change — load, features, platforms) or *exploratory*
(an extreme, stress or failure situation that exposes limits). Aim for coverage across the
step-4 drivers **and** across the three types. Keep going
for multiple passes until ideas are exhausted (typically 2–3× the number of participants).
Number them `S-1, S-2, …` verbatim — do **not** polish yet.
Offer the guide's *Step 5* prompts (one per scenario type) to each participant, and its restart
prompts when a round stalls. In **refresh** mode, existing scenarios enter the list first,
tagged *existing* in the Contributor column, and the round aims at the gaps.

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

Generate the ballot with `qawkit.py ballot` (see *Generate the workshop artifacts*) so the
budget and the scenario rows come from the report, not from memory. Once the votes are in the
sheet, run `qawkit.py tally` and copy its *Step 7 of the report* block into the report — never
add votes up by hand. `validate.py` re-checks the totals, the budget and the ranking order.

When relaying for a group, ask the user for per-stakeholder vote allocations, or for a single
merged prioritisation if that is all that is available. Record the vote table and the ranked list.
Ask the guide's *Step 7* sanity question after the tally; in **refresh** mode, a scenario that
dropped sharply since the last workshop is a finding — ask what changed.

### Step 8 — Scenario refinement
Take the **top scenarios** (as many as time allows, usually 4–6). Fill the six parts with the
guide's one-question-per-part table, and turn vague answers ("fast", "always up", "secure") into
measures with its *Turning vague answers into scenarios* table. For each, produce:
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

After each refined scenario, run `qawkit.py lint` and ask the question it gives for every
finding before moving on; the playbook's *Scenarios that hold up* lists the smells it cannot
see (a solution in the scenario, two events in one stimulus).

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
  (`V ≈ Importance`, `R ≈ Difficulty`.) Mark a `(H, H)` leaf `★`. The guide's *Step 9* gives
  the one question per letter that sets each pair.
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

0. Starting point — entry mode (greenfield / partial / refresh) and the inputs it used.
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
11. **Parked questions** — every `PQ-<n>` with who can answer it, an owner and a due date.
12. Next steps (run `/drivers` from the hand-off table, then ADD; schedule ATAM).

Generated beside the report by `qawkit.py` (section above): `qaw-prep.md` (before the session,
when a drivers register exists), `qaw-agenda.md` (before the session), `qaw-vote-sheet.md` and
`qaw-tally.md` (Step 7) and `qaw-summary.md` (at the end).

## Rules

- **Write for the human reader** — follow `${CLAUDE_PLUGIN_ROOT}/references/writing-style.md`:
  open every artifact with one to three plain sentences saying what it covers and where to start,
  explain notation like `(V, R)` at its first use, keep bold for labels and defined terms, and
  use no filler words (`validate.py` rejects the worst offenders). Template guidance belongs in
  HTML comments, never in the artifact's visible text.

- Facilitator stays neutral on scenario *content*; drives *process* only.
- **Rely on the documentation available** (section above): read it before each step, confirm
  what it already answers instead of asking again, cite the source of every documented answer,
  and record contradictions between documents and stakeholders.
- Elicit with questions from the guide, never with "what are the non-functional requirements?";
  no question names a technology or invites a yes/no answer about a quality.
- An unanswered question is parked as `PQ-<n>` with an owner — never answered with an invented
  number.
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

## Running in the Claude app (chat)

The same workshop runs in a claude.ai conversation, where there is no project folder and
usually nobody else in the room: the user relays for the stakeholders.

- **Inputs.** Ask the user to attach the documents Step 0 needs (brief, requirements, a zipped
  `architecture/drivers/` folder, the last `qaw-report.md`). The *Rely on the documentation
  available* rules apply to attachments exactly as to files.
- **Pace.** One step per reply: announce the step, ask its questions as a numbered list the user
  can answer in one message, play the answers back, then show the step's section of the report.
- **Files.** With code execution, keep the report and the kit under `architecture/qaw/` in the
  sandbox's working folder, run `qawkit.py` and `validate.py` there exactly as above, and offer
  the files for download at the end of each step. Without code execution, show each section in
  the reply and say that the kit files and the checks were not run.
- **Resuming.** In a new conversation, ask for the last `qaw-report.md`, run `status` on it, and
  continue from its *Next step*.
- **Diagrams.** The renderers need Node.js, Chromium, Java and Graphviz, which chat does not
  have. Keep each scenario's Mermaid block in the report, leave its image line in place, and
  tell the user to render the PNGs later with the `sei-diagrams` skill in Claude Code. The
  missing PNGs are the only `validate.py` findings that may stay open in chat; list them for
  the user.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until the generated artifact passes all three:

1. **Automated**: `python ${CLAUDE_PLUGIN_ROOT}/tests/validate.py architecture/qaw/qaw-report.md` — exits 0. It checks IDs, structure, six-part scenarios with numeric
   measures, traceability with no orphans, vote arithmetic, diagram rules, and the
   deprecated-`QAS-` guard.
2. **Scenario lint**: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/qawkit.py lint architecture/qaw/qaw-report.md`
   — exits 0. Every finding is a question still to ask, or a characteristic to record as not
   significant here.
3. **Best-practice checklist**: walk the relevant section of
   `${CLAUDE_PLUGIN_ROOT}/references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix,
   re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
