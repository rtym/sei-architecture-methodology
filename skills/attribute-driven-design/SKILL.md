---
name: attribute-driven-design
description: >-
  Facilitate a SEI Attribute-Driven Design (ADD 3.0) architectural design session — iterative,
  driver-focused decomposition producing an architecture plus C4/UML views and an ADR log. Use
  when the user invokes /add, asks to run an ADD session, design or evolve an architecture from
  quality attribute drivers, or produce an architecture document from scenarios.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
user-invocable: false
---

# Attribute-Driven Design (ADD 3.0)

Facilitate a short SEI ADD 3.0 design session. **Two living Markdown files per session are the
single source of truth** — update them after every step.

Working directory: `architecture/add/` (create it).
- `architecture/add/<slug>-session.md` — the session log
- `architecture/add/<slug>-Architecture.md` — the architecture document

Deep references: `${CLAUDE_PLUGIN_ROOT}/references/add-method.md`, `${CLAUDE_PLUGIN_ROOT}/references/design-concepts.md` (the concept
catalog + how to identify/select), `${CLAUDE_PLUGIN_ROOT}/references/interfaces.md` (Step 5),
`${CLAUDE_PLUGIN_ROOT}/references/architecture-in-the-lifecycle.md` (Iteration 0, architecture debt). Diagram rules:
the `sei-diagrams` skill
(`${CLAUDE_PLUGIN_ROOT}/skills/sei-diagrams/SKILL.md`) — **all** diagrams in both files follow it.

**Keep prompts and findings short** — a sentence or two. Offer choices as numbered lists.
**Draft first**: at each step propose a complete draft, then refine with the user.

## Start

On invocation — unless `/add` was given arguments that already answer it — ask in one line whether to:
1. **New** — start a fresh session.
2. **Continue** — list `architecture/add/*-session.md`, let the user pick, read it, resume.
3. **Report** — the session file already *is* the report; give its path.

For a new session get a short **name** (slug) and a one-line **system purpose**, then create both
files from the templates below. If `architecture/drivers/`, `architecture/quality-attributes/scenarios.md`
or a QAW report exists, offer to import its drivers instead of re-entering them. Create the
package index `architecture/README.md` (`${CLAUDE_PLUGIN_ROOT}/templates/architecture-readme.md`) if absent and
update its `/add` row when the session ends.

## Templates

Create the two files from their templates and keep their sections exactly — the same headings,
levels and order (`validate.py` checks them). The templates carry the tables, the starter
diagrams and the guidance comments; read them, do not write the files from memory.

- `${CLAUDE_PLUGIN_ROOT}/templates/add-session.md` → `<slug>-session.md`. Header bullets
  (Date, Purpose, Status, Architecture, Drivers imported from), the **Drivers** tables (quality
  attribute scenarios, use cases, constraints, architectural concerns), the **Iteration Plan
  (design backlog)**, then one `## Iteration N — <goal>` block per iteration with a section for
  each of Steps 2–7. Append a new block for every iteration.
- `${CLAUDE_PLUGIN_ROOT}/templates/architecture-document.md` → `<slug>-Architecture.md`. Nine
  numbered sections: 1 Introduction · 2 Context diagram · 3 Architectural drivers · 4 Container
  diagram · 5 Component and module views (one `### <Container name>` per container, then
  `### Module decomposition`) · 6 Sequence diagrams · 7 Deployment diagram · 8 Interfaces and
  events · 9 Design decisions. Every diagram sits under a `Diagram` heading with a `Description`
  heading after it, embedded per the `sei-diagrams` *Embedding in Markdown* rule.

Quality attribute scenario IDs in both files are attribute-prefixed (`AQA-`, `SQA-`, `PQA-`,
`MQA-`, … — see the `architectural-drivers` skill).

## Process

Announce each step in one line, then write its result to the session file.

### Step 1 — Review inputs (once, before iterations)

- **Design purpose** (choose one): greenfield system · greenfield feature · brownfield replacement
  · brownfield extension · brownfield migration — take it from the drivers `README.md` header if
  the register exists.
- **Business goals** (`BG-`) and **stakeholders** (`ST-`, `architecture/drivers/stakeholders.md`)
  — import from the `architectural-drivers` register if it exists.
- **Primary functional requirements** — the architecturally significant **use cases** (`UC-`),
  each with primary actor, trigger, and main success scenario.
- **Quality attribute scenarios** — six-part form, ISO/IEC 25010 classification, attribute-prefixed
  IDs (`AQA-`, `SQA-`, `PQA-`, …), priority `(Importance, Difficulty)`. Import from
  the `architecture/drivers/` register (its `README.md` matrix and one file per driver), or from
  `architecture/quality-attributes/scenarios.md` / the QAW report if present.
- **Constraints** (`CON-`) — business, technical, regulatory.
- **Architectural concerns** (`AC-`) — extensibility, team skills, tech-stack mandates, etc.
  Import `architecture/drivers/concerns/AC-*.md` if present; concerns raised during design are
  written back there as new `AC-<n>` files.

End with a one-line summary of the most architecturally significant drivers.

### Iteration Plan / design backlog (pragmatic addition)

Group drivers into N iterations, each with a bounded goal, ordered by the **design roadmap** for
the system type (`${CLAUDE_PLUGIN_ROOT}/references/add-method.md` → *Design roadmap*):
- **greenfield, mature domain**: iter 1 = establish overall structure (reference architecture +
  deployment pattern); iter 2 = structures for the primary use cases; later iters = refine for
  the remaining quality-attribute drivers;
- **greenfield, novel domain**: lead with prototypes to retire the hardest QA risks;
- **brownfield**: start from the existing architecture; iterations refine it to meet the new or
  violated drivers.

Keep the plan as a living **design backlog** on a Kanban board with columns **Not Yet Addressed
· Partially Addressed · Completely Addressed · Discarded**: seed with one item per driver, add
supporting items (a prototype to retire a QA risk, reverse-engineering, review findings,
concerns discovered while adopting a concept). Step 2 moves a card to *Partially Addressed*;
Step 7 moves it to *Completely Addressed* against an explicit criterion (analysed, or prototyped
and verified). End the round when the highest-priority drivers are *Completely Addressed*.
Note: **Steps 2 and 3 may be reversed** for greenfield / reference-architecture work (pick an
element first). Deep reference: `${CLAUDE_PLUGIN_ROOT}/references/add-method.md`.

**Coverage check (mandatory):** list every driver ID from Step 1 and confirm each appears in ≥ 1
iteration / backlog item before presenting. Present, wait for review, write the agreed plan into
`## Iteration Plan`.

### Step 2 — Establish the iteration goal by selecting drivers

Review unaddressed / partially-satisfied drivers. Select the subset for this iteration —
prioritise drivers that are **both** high-importance and high-difficulty. State the goal in one
sentence. **Present and wait for confirmation.**

### Step 3 — Choose element(s) to refine

Iteration 1 on greenfield = the whole system. Later = a subsystem/service/component from a prior
iteration. **State the choice and why. Wait for confirmation.**

### Step 4 — Choose design concept(s)

**Identify** candidates from the **design concept catalog** (coarse → fine): reference
architectures · deployment patterns · architectural & design patterns · **tactics** ·
externally developed components. Start from the **candidate tactics** already recorded on each
selected driver's `<ATTR>QA-<n>.md` (they are a shortlist, not a decision — accept, reject or
extend them, and say which in the rationale), then widen with the best-practice catalogs
(`${CLAUDE_PLUGIN_ROOT}/references/tactics-catalog.md`, `${CLAUDE_PLUGIN_ROOT}/references/architecture-patterns.md`), your own experience,
and a peer brainstorm. **Select** with a pros/cons table keyed to the iteration's drivers; for a
high-stakes choice, add a SWOT or CBAM (ROI) analysis. Every rationale cites ≥ 1 driver ID;
record the discarded alternatives and why. Name tactics from the catalog so Step 7 and ATAM can
question them with the matching questionnaire. **Present the table and wait for review.**

### Step 5 — Instantiate elements, allocate responsibilities, define interfaces

Two tables: **instantiation decisions** (elements created/modified + responsibility) and
**interfaces** (provided / required / protocol per element). For each significant interface
capture the four agreement points from `${CLAUDE_PLUGIN_ROOT}/references/interfaces.md` — scope, interaction style,
data representation & structure, error model — and apply the design principles (least surprise,
small interfaces, uniform access, DRY, consistency). **Present both and wait for review.**

### Step 6 — Sketch views and record design decisions

Update the relevant `Architecture.md` sections (§2 §3 §4 §5 §6 §7 §8). Follow the **interactive
diagram review** protocol from the `sei-diagrams` skill:
1. Open with **"Diagrams modified this step: §N Title [, §M Title]"**.
2. Render each modified diagram as a fenced mermaid block, applying every diagram rule.
3. After each diagram, one sentence on what changed and why.
4. Every sequence diagram gets a plain-English description paragraph immediately below it.
5. Render each diagram to `architecture/add/diagrams/<name>.png`, `Read` it and visually
   cross-verify (correctness + minimal crossings), then embed it in `Architecture.md` as the
   diagram per the `sei-diagrams` *Embedding in Markdown* rule (Mermaid → fenced block + image
   line; PlantUML → image line + a link to the `.puml` source), relative paths.

Record significant decisions in §9 **and as ADRs**: each significant decision gets
`architecture/add/adr/ADR-<n>.md` from `${CLAUDE_PLUGIN_ROOT}/templates/adr.md` (context, decision, rationale
citing driver IDs, alternatives, consequences), and its §9 row links it in the `ADR` column.
When the iteration introduces or changes **modules** (layers, packages, allowed-to-use rules),
add or update the *Module decomposition* diagram in §5 — it seeds the Views-and-Beyond Module
view. **Present diagrams + decisions table; wait for review before writing to `Architecture.md`.**

### Step 7 — Analyse and review the iteration goal

Analysis table: each selected driver → **yes / partially / no** + notes. Drive the analysis with
the **tactics-based questionnaire** for each attribute in play (`${CLAUDE_PLUGIN_ROOT}/references/tactics-catalog.md`):
for every relevant tactic, is it used, where, and what is the risk if it is not? State whether
the goal was achieved and which drivers/concerns remain. **Write back to the register**: for every
driver analysed, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/driverstatus.py architecture/drivers <ID>
<partially|addressed>` (when the session entered its drivers here and there is no register, say
so in the analysis notes and skip this) — it sets the status in the driver file, its kind's index, the `README.md`
matrix and (for a scenario) the utility tree together, and refuses to change any of them if one
does not list the driver. Then set `Addressed in` to this iteration in the matrix and append a
change-log line there and in the package index `architecture/README.md`. Ask whether to run
another iteration.
Yes → Step 2 with remaining drivers. No → set **Status: completed**, print both file paths, and
offer to run `/architecture-docs` (Views & Beyond) and `/atam` (evaluation).

## Rules

- **Write for the human reader** — follow `${CLAUDE_PLUGIN_ROOT}/references/writing-style.md`:
  open every artifact with one to three plain sentences saying what it covers and where to start,
  explain notation like `(V, R)` at its first use, keep bold for labels and defined terms, and
  use no filler words (`validate.py` rejects the worst offenders). Template guidance belongs in
  HTML comments, never in the artifact's visible text. Keep the template's sections
  exactly — the same headings, levels and order; `validate.py` checks them.

- IDs are sequential per session: `BG-1`, `UC-1`, `CON-1`, `AC-1`, and attribute-prefixed QA scenarios (`PQA-1`, `SQA-1`, …).
- Every Step-4 and Step-6 rationale cites ≥ 1 driver ID.
- The session Markdown stays current — write as you go, never only at the end.
- Design decisions → `Architecture.md` §9 **and** one `adr/ADR-<n>.md` each; interfaces → §8;
  diagrams → their dedicated sections; module structure → §5 *Module decomposition*.
- Step 7 writes driver statuses back to `architecture/drivers/` and the package index.
- Every diagram satisfies the `sei-diagrams` rules: `title` line, aliases without spaces, concrete
  technology on every element, specific relationship labels, ≤ 10 nodes, explicit `Boundary`,
  minimised crossings. Always render in the conversation before writing to the file.
- Every sequence diagram in `Architecture.md` is followed immediately by a plain-English description.
- Wait for user review at the Iteration Plan step and at Steps 2, 3, 4, 5, 6, 7.
- After the session, `python3 ${CLAUDE_PLUGIN_ROOT}/tests/validate.py architecture/add/*.md` must pass.

## Quality gate — cross-check the output before you're done

Do not declare the activity complete until the generated artifact passes both:

1. **Automated**: `python3 ${CLAUDE_PLUGIN_ROOT}/tests/validate.py architecture/add/*.md` — exits 0. It checks IDs, structure, six-part scenarios with numeric
   measures, traceability with no orphans, diagram rules, and the deprecated-`QAS-` guard.
2. **Best-practice checklist**: walk the relevant section of
   `${CLAUDE_PLUGIN_ROOT}/references/best-practices-checklist.md` and report each item `ok` / `fix: …`. Fix,
   re-run, repeat.

Every embedded diagram must additionally have been rendered to PNG and **visually cross-verified**
(`Read` the image — correctness + minimal crossings) per the `sei-diagrams` skill.
