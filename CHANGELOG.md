# Changelog

All notable changes to the `sei-architecture-methodology` plugin. Versions follow
[SemVer](https://semver.org/); the version lives in `.claude-plugin/plugin.json` and is mirrored in
`.claude-plugin/marketplace.json` (both places) — `tests/validate.py --self` fails on drift.

## 1.15.0 — 2026-11-12

Diagrams become regression fixtures, and the layout check that used to be done by eye is counted.

### Added
- `skills/sei-diagrams/scripts/diagramlint.py` measures a rendered diagram (a `.svg`, or a
  `.mmd` / `.puml` it renders first): edge crossings, overlapping nodes, edges drawn through a
  node they do not connect to, colours outside the SEI palette, and an extreme ribbon shape. Each
  defect is named (`edge api_db × edge worker_cache`). The diagram skill runs it on every render
  before the visual check.
- `tests/diagramcheck.py` with `tests/diagram-baseline.json`: every example PNG is recorded with
  the source it was rendered from, its size, its element counts and its layout defects. Without a
  renderer the suite fails on a stale render (source changed, PNG did not), a PNG changed without
  the baseline, a low-resolution PNG, or an off-palette colour in a source or in any diagram a
  skill teaches. With a renderer it re-renders all 52 example diagrams and fails when one shows
  different elements or words, gains a crossing, an overlap or a run-through edge, loses the SEI
  theme, or changes shape — so a Mermaid, PlantUML or Graphviz upgrade cannot degrade a diagram
  unnoticed. `tests/test_diagrams.py` covers both scripts.
- `scripts/render-all.sh` also renders Mermaid blocks that live only in a Markdown file (12 of
  the Mermaid example's 26 diagrams), to the PNG the document shows; `--list` prints the plan.
- The examples' Markdown reports are compared with a fresh build, and the validator rejects an
  artifact heading with no blank line above it.
- Layout playbook: stack two stores that two services share with an invisible link.

### Fixed
- `scripts/driverstatus.py` deleted the blank line after the `- **Status**:` bullet whenever that
  bullet was the last one in the header, gluing the next heading to it. Both examples' CON-4 had
  been damaged this way. It also miscounted columns in a table row holding an escaped pipe.
- The PlantUML theme did not style use cases or sequence group frames, so use case ovals and the
  `alt` tab were drawn in PlantUML's default grey with a black border. They now use the palette;
  the seven affected example diagrams are re-rendered.
- The deployment diagrams could cross two edges: the Mermaid example's always did, and the
  PlantUML example's did under Graphviz 14 (not under 16). In both notations the two stores are
  now stacked with a hidden layout link, so nothing crosses whichever layout engine draws them.
- CI renders with PlantUML 1.2026.10, the version Homebrew installs.
- The Mermaid UC-4 diagram used a note colour one digit off the palette (`#FBF7EE`).
- `setup.sh` would write a `package.json` pinning older renderer versions than the shipped one.
- `render.sh` split a quoted glob on spaces, so a pattern under a directory with a space in its
  name rendered nothing; a pattern that matches no file is now reported as a failure.

### Verified
- The Mermaid CLI 12.0 → 12.2 and ELK layout 1.0.1 → 1.0.2 update merged after 1.14.0 renders
  every example diagram with the same layout as before.

## 1.14.0 — 2026-11-07

A review of the repository and both worked examples. It fixes the inconsistencies it found, adds
checks so the same kinds of drift fail the tests, and holds every generated artifact to its
template's structure.

### Fixed
- The examples' UC-3 named a "Bank Import API" supporting actor that no other artifact has; the
  user uploads the CSV file. The actor is gone from UC-3 and both use case diagrams, and UC-3's
  priority matches its index (medium).
- Driver statuses that disagreed between copies: SQA-1 and AQA-1 are `at risk` (ATAM) in every
  index and the utility tree, CON-4 is `in design` in its file, and the change log names CON-4.
- The Import Queue and Import Worker that the ATAM, ADR-2 and the Views-and-Beyond views rely on
  were missing from the ADD session, the ADD container and deployment diagrams, and the PlantUML
  container view. The Mermaid example also kept a stale `diagrams/container.mmd` that differed from
  the diagram in the document; it is removed.
- The deployment diagrams labelled the browser's call to the API "Serves SPA to browser"; Redis is
  no longer described as holding only derived data now that it carries the import stream.
- The ADD session's design-concepts table was split by a paragraph and rendered as text, and its
  iteration plan said SQA-1 was complete where the iteration's own analysis said partially.
- The ATAM reports pointed at diagrams that do not exist (`Architecture-05.png`, and a
  `../diagrams/` folder the PlantUML example does not have); they now link the real files.
- "Rendered + visually verified", "visually verified: yes" and "this is the Mermaid tree" are
  gone from the examples, and the four templates and the diagram skill that put them there now
  keep that instruction in HTML comments. Other writer guidance in the templates moved into
  comments too.
- The validator's "needs a numeric measure" rules counted the digit in an ID such as `PQA-1`,
  so they could never fire.
- A reference table in `architectural-drivers.md` had no header separator.
- Sections out of their template's order or level in the examples: BG-2's business-goal scenario
  came before its context, the ATAM's recommendations came after the register write-back, and the
  ADD architecture's interface specification sat beside *Interfaces* instead of under it. The
  docs directory listed an ID prefix the register does not use.
- The example ATAM was dated 2026-09-05, a day before the architecture it evaluates was designed;
  it is 2026-09-07, as the drivers change log already said. The docs rationale cited tradeoff
  point `T-1`, which the ATAM calls `TP-1`, and the architecture document called ATAM risk R-1
  closed by an ADD iteration that has not run yet.
- The ATAM template's Step 8 now says it is omitted in Lightweight mode, as Step 7 did, so a
  Lightweight report keeps the template's structure.
- Language in the examples: `p95` appeared in 15 files and was explained in none, and `(V, R)`
  was unexplained in two indexes; each now explains the notation at first use. Six passages
  written as arrow or dot chains (the ADD roadmap, the security view's denied-access sequence,
  the ATAM's approach list and register write-back, the ADRs' related links, the QAW's expected
  outputs) are sentences or lists. The directory, the scenario summary and the ADD session open
  with a sentence saying what they cover, and the PlantUML scenario files' diagram caption tells
  the reader how to read the diagram instead of how it was drawn. The three templates these
  came from carry the same changes.

### Changed
- Templates: the ADD session's plan heading is *Iteration Plan (design backlog)*, the drivers
  README title no longer embeds a file name, the ATAM template names Step 6 sections
  `<ATTR>QA-<n>` and adds optional Phase 2 scenario sections and a CBAM backlog, and the
  architecture document allows an interface specification under *Interfaces*.

### Added
- Generated artifacts keep their template's structure. `validate.py` compares each artifact's
  headings with its template: the same sections, at the same levels, in the same order. A
  section whose heading has a placeholder repeats; one the template marks optional may be left
  out. A failure names the section that is missing, added, repeated, out of order or at the
  wrong level. Every template must
  govern some artifact and match its own structure (`--self`). The rule is in
  `references/writing-style.md` and in every skill's writing rule.
- Templates for the Views-and-Beyond package files that had none — `docs-readme.md`,
  `system-overview.md`, `mapping-between-views.md`, `rationale.md`, `directory.md`,
  `change-log.md` — and `scenarios.md`, moved out of the quality-attributes skill.
- `scripts/driverstatus.py` sets a driver's status in the driver file, its kind's index, the
  README matrix and the utility tree at once, or changes nothing. ADD, ATAM and `/drivers` now
  write statuses through it.
- Validator rules: every copy of a driver's status and priority must agree; a table must have a
  header separator; a backticked relative path must exist; a Mermaid block must match the `.mmd`
  beside its PNG; artifacts and template text must not describe how they were made.
- PlantUML diagrams render at 240 dpi (`PLANTUML_DPI` to change) with the size limit raised, so
  they are as sharp as the Mermaid renders; every PlantUML example diagram was re-rendered (same
  layouts, 2.5 × the pixels). `tests/run.sh` fails if the default resolution drops.
- Tests: `tests/test_driverstatus.py` (45), and `tests/test_validate.py` grows to 230 with a case
  per rule of the architecture, session, ATAM, view-packet, mapping and drivers checkers, the
  template-structure check, the self-check and the CLI. Line coverage of `validate.py` rises from
  59 % to 88 %. The Claude app edition bundles every template with the validator so the structure
  check runs in chat too.

## 1.13.0 — 2026-11-06

The Quality Attribute Workshop becomes a guided, checked workshop, from a blank page or over
existing documentation, and the plugin gains a Claude app edition for claude.ai chat and Cowork.

### Added
- `references/qaw-question-guide.md` — the QAW facilitator's script: the questions to ask at
  every step, per ISO/IEC 25010 characteristic, per kind of system (AI and machine learning,
  multi-tenant SaaS, data platforms, mobile and offline, regulated data, IoT and edge, public
  APIs), per stakeholder role, for testing documentation that already exists, and for turning
  vague answers ("fast", "always up", "secure") into measurable scenarios.
- `references/qaw-facilitation-playbook.md` — how to run the room: four formats (two-day,
  one-day, half-day, remote) with a timebox table each, the roles, what to prepare and when,
  thirteen difficult moments with what to do and say, the scenario smells, and the follow-up
  after the workshop, including when to run it again.
- QAW entry modes. A workshop starts with Step 0, *Starting point*, which picks **greenfield**
  (nothing documented), **partial** (a brief, a codebase or loose scenarios to correct) or
  **refresh** (an existing drivers register to test and extend). In refresh mode the existing
  scenarios enter brainstorming tagged *existing* and are re-voted with the new ones; a previous
  report is kept as `qaw-report-<date>.md`. The report header records the format.
- The QAW skill relies on the documentation available: before each step Claude checks the
  documents found in Step 0, confirms what they already answer (citing the source) instead of
  asking again, asks open questions only about the gaps, and records where a stakeholder
  contradicts a document.
- *Parked questions* in the QAW report: a question nobody present can answer becomes a `PQ-<n>`
  row with who can answer it, an owner and a due date, instead of a guessed number.
- `scripts/qawkit.py` — the QAW kit, generated deterministically from the documentation and the
  report: `prep` (documented answers to confirm with their sources, characteristics with no
  scenario and their questions, characteristics set aside last time with their reasons, the
  questions for the kind of system via `--domain`, each participant's role questions, open
  parked questions), `agenda` (dated and timed from the playbook; later days fall on working
  days), `ballot` (the Step 7 vote sheet), `tally` (totals, budget check, unspent votes and the
  ranking, as the block for Step 7), `status` (which steps are done, the next step, the gaps,
  overdue parked questions), `lint` (scenario smells, each with the guide's question to ask;
  exits 1 while findings remain) and `summary` (one page for the sponsor).
- A *Running in the Claude app (chat)* section in the QAW skill: attachments as inputs, one step
  per reply, files in the sandbox, resuming from the last report with `status`, and diagrams
  left as source for rendering later.
- `scripts/appbundle.py` — builds the Claude app edition: every skill carries the references,
  templates and scripts it names, paths point at `${CLAUDE_SKILL_DIR}`, SKILL.md front matter
  keeps only the fields claude.ai accepts, and the zip is byte-identical for the same sources.
  Upload it in Customize > Plugins. CI uploads it with every run.
- Validator: the entry mode must be exactly one of the three; refresh mode must carry existing
  scenarios into Step 5; every parked question needs an owner and a status; the format must be
  one of the four; Step 7 must add up (row totals, the 30 % budget, nobody over budget, a
  ranking that follows the totals and lists every scenario). Reports written before this
  release still pass. `--self` checks that the question guide covers every step,
  characteristic, entry mode and system type, and that the playbook times all nine steps in
  every format.
- Tests: `tests/test_validate.py` 112 (was 55), `tests/test_qawkit.py` 236 and
  `tests/test_appbundle.py` 94, wired into `tests/run.sh` as steps 4b, 4d and 4e. The golden
  files tie each example's vote sheet, tally and Step 7 together.

### Fixed
- An archived QAW report (`qaw-report-<date>.md`) was validated as an ADD session because of
  its dated name; it is now validated as a QAW report.

### Changed
- Both worked examples' QAW reports: a *partial*-mode starting point (the founder's brief), a
  half-day format, a recorded reason for each ISO/IEC 25010 characteristic with no scenario,
  Step 7 taken from the tally, and three parked questions, among them the budget figure BG-4
  never stated. Each example carries the full kit, prepared for a remote refresh workshop.
- README: a section on the Claude app edition, a QAW example, and a corrected note on plugin
  discoverability (Anthropic's plugin directory exists; adding a marketplace is not a listing).

## 1.12.1 — 2026-11-01

### Changed
- Mermaid renderer bumped to `@mermaid-js/mermaid-cli` 12 (+ `@mermaid-js/layout-elk` 1).
  mermaid-cli 12 replaces `--width` with `--size` (a max-dimension budget): `render.sh` now
  passes `--size`, keeps `--width` as an alias, and `setup.sh` installs the Chromium build this
  puppeteer expects explicitly (npm's allow-scripts guard can block the postinstall download)
  and writes current versions in its package.json fallback. All 21 Mermaid example renders and
  the Mermaid example reports regenerated: diagrams now get up to 4800 px on their longest
  axis, so tall diagrams gained resolution.

## 1.12.0 — 2026-11-01

### Added
- `references/writing-style.md` — how artifacts are written for human readers (plain voice, no
  filler, an orientation paragraph up front, notation explained at first use); every
  artifact-producing skill now points at it from its Rules.
- Validator prose checks on every produced artifact: filler phrases are rejected, unfilled
  template placeholders fail, and a duplicated header bullet fails. `--self` also lints the
  plugin's own commands/skills/templates/references for filler and checks example diagram
  hygiene (every `.mmd`/`.puml` has its committed render; no orphan PNGs).
- `tests/test_validate.py` — unit tests for the new prose checks, wired into `tests/run.sh`,
  then extended to 55 fixture-based tests covering the diagram rules, every per-driver-file
  checker, report checks (scenario register, ATAM), traceability orphans (incl. the retired
  exclusion), link checking (incl. the `reports/` exemption) and the drivers-directory
  cross-file check.
- `render.sh` and `render-plantuml.sh` reject an output-looking `.png`/`.svg` argument with a
  message pointing at `--out DIR` — every positional argument is an input, and the old behaviour
  failed confusingly; `run.sh` step 4c asserts the guards without needing a renderer.
- `scripts/render-all.sh` — re-render every `*.mmd` / `*.puml` under a directory in place, in
  one deterministic pass; both example READMEs use it in their regenerate instructions.
- `.github/PULL_REQUEST_TEMPLATE.md` — the CLAUDE.md contributor checklist at review time —
  and `.github/dependabot.yml`, grouping weekly npm updates for the pinned Mermaid renderer and
  GitHub Actions updates (the vendored C4-PlantUML stays a manual, reviewed bump).
- Test dashboard on GitHub: `tests/run.sh` mirrors every check (pass / fail / skipped) into the
  Actions job summary when `GITHUB_STEP_SUMMARY` is set, and the README carries the workflow
  status badge. The suite also reports execution stats — per-step wall time, pass/fail/skip
  counts and the unit-test assertion totals — in the console and as a table in the job summary.

### Maintenance
- All 54 example diagrams re-rendered with the pinned toolchain and visually re-reviewed; the
  regenerated example reports pick up the reader-voice drivers README.

### Changed
- The drivers `README.md` template (and both worked examples) opens with a plain-language
  reader's paragraph instead of template meta-commentary, and its QA ID legend lists only the
  prefixes in use (the full table stays in the taxonomy reference). Template guidance now lives
  in HTML comments so it cannot leak into artifacts — applied across the drivers README,
  package-index, stakeholders, quality-attribute-scenario and architecture-document templates;
  both examples' stakeholder registers rewritten in reader voice to match.

### Fixed
- Duplicated `Design purpose` / `Stakeholders` header lines in the Mermaid example's drivers
  README and a duplicated `Mode` line in its `scenarios.md`.
- Removed the orphaned `examples/personal-finance-tracker-plantuml/diagrams/container.png`
  (nothing referenced it; the PlantUML example README's regenerate commands no longer produce it).

## 1.11.1 — 2026-09-24

### Fixed
- CI's PlantUML "render every example diagram" step asserted a hardcoded count of committed
  `.puml` files (29) that drifted stale after the 1.10.0 diagram dedup left 26. Now derived from
  `git ls-files` at run time so it can't drift again.
- `render.sh`'s Markdown extractor silently overwrote a mermaid block's output when two blocks
  shared the same `%% name:` slug, discarding the first diagram with no error. Now fails loudly
  and renders nothing for that file, naming the colliding blocks.
- `validate.py`'s QAW refined-scenario diagram check and its Mermaid title-comment extraction
  each had an anchoring bug (unanchored substring containment; a lookahead defeated by
  backtracking) that let a numeric-ID prefix collision or a `%% name:` comment mask a real
  problem. Both now match the delimiter-safe pattern already used elsewhere in the file.
- `skills/quality-attributes/SKILL.md`'s candidate-tactics table pointed at `tactics-catalog.md`
  sections ("Scalability", "Portability") that don't exist as standalone headings; corrected to
  the actual heading names.
- Both worked examples' root `README.md` now carry the package-index shape
  (`templates/architecture-readme.md`'s Activities-and-outputs table + change log) that
  `/drivers` creates and every other skill updates, closing a regression-fixture gap from 1.10.0.

## 1.11.0 — 2026-09-23

### Added
- **Brownfield intake** (`references/brownfield-intake.md`, `/sei brownfield`): a documented
  procedure for reverse-engineering a first draft of the drivers and the as-built views from an
  existing repository — what to read and in what order, what to produce, and an evidence table
  (claim · file path · confidence) behind every claim. Governed by one rule: code shows the
  architecture, never the requirement, so every derived driver is marked *derived — confirm* and
  an absent tactic is an evaluation finding rather than a driver. Wired into the router, `/drivers`
  Step 1 and `/atam`'s undocumented-architecture path.
- **Candidate tactics per quality attribute scenario**: each scenario names the tactic families it
  is normally met with (mapping table from ISO/IEC 25010 characteristic to tactics-catalog
  section), giving ADD Step 4 a shortlist to accept, reject or extend and telling ATAM Step 6
  which questionnaire to walk. A hint, never a design decision.
- **A package legend**: one legend diagram per package, rendered once and referenced from the
  documentation roadmap and the view packets instead of repeated in every diagram. Mermaid and
  PlantUML patterns, plus the inline-key variant for a diagram that must stand alone.
- Validator: every file in `references/` must be linked from the references index.

### Fixed
- `/atam` and `/architecture-docs` told you to update the package index but, unlike the three
  other skills that write to it, never said to create it when absent — a standalone run on a
  project with no drivers register pointed at a file that did not exist. ATAM also now says what
  to do when there is no register to write statuses back to.

## 1.10.0 — 2026-09-22

Method-level improvements from a careful read of every skill: hand-offs between activities,
things a skill promised but never produced, and workflow friction.

### Added
- **Package index** `architecture/README.md` (`templates/architecture-readme.md`): `/drivers`
  creates it, every skill registers its output. Sub-package footers link up to it and only to
  siblings that exist — a drivers-only project used to fail its own quality gate on eight broken
  navigation links.
- **Stakeholder register** `architecture/drivers/stakeholders.md` (`ST-<n>`), read by `/qaw`
  (participants), `/atam` (Phase 2) and `/architecture-docs` (view selection).
- **Design purpose and architectural concerns** in the drivers register (`README.md` header,
  `concerns/AC-<n>.md`), so `/add` Step 1 imports all five ADD 3.0 inputs.
- **`at risk` status**, set by ATAM Step 9 on every scenario with a Risk, with a change-log line
  in the drivers README and the package index.
- **ADRs from ADD**: Step 6 writes `architecture/add/adr/ADR-<n>.md` per significant decision;
  §9 links them; V&B `rationale.md` links instead of re-deriving.
- **Module decomposition view** in the ADD architecture document (§5 "Component and module views").
- **ADD Step 7 write-back** of driver statuses to the register.
- **QAW**: scenario type (use-case / growth / exploratory) at brainstorm time; a hand-off table
  mapping `CS-`/`AD-` IDs to register IDs; explicit diagram path.
- **ATAM**: `**Mode**` header; Steps 7–8 marked Full-only; sensitivity/tradeoff IDs renamed
  `SP-`/`TP-` (no clash with QAW raw scenarios `S-`).
- **V&B**: the primary C&C view's §2.4 carries one behaviour diagram per architecturally
  significant use case.
- **`render.sh`**: a `%% name: <slug>` comment names the PNG of a Mermaid block extracted from
  Markdown, so inserting a diagram no longer renumbers the rest.
- **Diagram house patterns** for sequence, state and deployment.
- Validator checks for all of the above; retired drivers excluded from the coverage check.
- `/quality-attributes` **register mode**: when `architecture/drivers/` exists it writes the
  per-scenario files there and `scenarios.md` becomes a linking summary — one source of truth.
- Worked examples updated throughout (stakeholders, concerns, ADRs, module view, behaviour
  diagram, QAW types + hand-off, ATAM mode + write-back, named diagram PNGs); reports regenerated.

## 1.9.0 — 2026-09-22

Gap-analysis release: consistency fixes across skills, templates and examples, tighter validation,
argument-aware commands.

### Fixed
- Every skill's quality gate now runs the validator as `${CLAUDE_PLUGIN_ROOT}/tests/validate.py`;
  the bare `tests/validate.py` did not exist from a user's project once the plugin was installed.
  The self-check rejects the unanchored form.
- Stale `architecture/drivers/drivers.md` references (ADD Step 1, architecture-document template)
  now point at the drivers **directory**.
- `scenarios.md` has one home: `architecture/quality-attributes/scenarios.md`. Templates, the
  drivers README navigation, the V&B system overview and both worked examples were aligned.
- Scenario diagram files are `diagrams/scenario-<ATTR>QA-<n>.*` everywhere (the quality-attributes
  skill used `<ATTR>QA-<n>.png`, so `/drivers` could not copy them by name).
- Rendering + visual verification is mandatory in `/quality-attributes` Step 5 (it said "on
  request" while its own quality gate required it).
- README: seven activities (not six); the layout tree shows the real `commands/` directory and
  marks `.claude/commands` as the in-place-development symlink.
- ATAM heading says four phases (0–3), matching the body and the glossary.
- Validator message and code agree on the scenario-count range (5–20).
- ADD session template use-case columns match the ADD skill.
- Removed a leftover `PLANTUML_SECURITY_PROFILE` diagnostic from the test runner.

### Changed
- Skills that are aliased by a differently-named command (`/add` → `attribute-driven-design`, …)
  carry `user-invocable: false`, so each activity appears once in the slash-command menu while
  Claude can still invoke the skill automatically. Enforced by the self-check.
- Removed the unrecognised `version:` field from every `SKILL.md` front-matter.
- The Mermaid renderer is pinned by a committed `skills/sei-diagrams/package-lock.json`;
  `setup.sh` uses `npm ci` when it is present and CI caches npm on it.
- Puppeteer config uses `"headless": true` (the pre-v22 `"new"` value is deprecated).

### Added
- Commands accept arguments (`argument-hint` + `$ARGUMENTS`): `/add new <slug>`, `/atam lightweight`,
  `/sei-diagram container plantuml …`, `/architecture-docs html`, paths for `/drivers`,
  `/quality-attributes`, `/qaw`, and an activity name for `/sei`.
- Validator: plugin.json ↔ marketplace.json version agreement; one picker entry per activity; every
  scenario in `scenarios.md` and every refined QAW scenario has an embedded, rendered diagram (bare
  backtick paths are rejected); `mapping-between-views.md` must contain real cross-view tables.
- Worked examples: `quality-attributes/scenarios.md` embeds all six scenario diagrams; the QAW
  reports embed the two refined-scenario diagrams (`qaw/diagrams/scenario-CS-1`, `-CS-5`).
- `CHANGELOG.md` (this file) and a contributor `CLAUDE.md`.

## 1.8.0 — 2026-09-14

- PlantUML `!include`s resolve through `PLANTUML_INCLUDE_PATH` (bare, assets-relative names — never
  `../`), so `.puml` files in a user's project render against the installed plugin.
- Licensed under Apache-2.0 with a `NOTICE`; vendored C4-PlantUML v2.10.0 (MIT) with its licence
  and provenance; self-check guards licence / attribution / version drift.
- CI split into three jobs (quick, Mermaid, PlantUML); PlantUML job renders every example `.puml`
  with a pinned upstream jar and Graphviz; render failures replay PlantUML's own diagnostics.

## 1.7.0 — 2026-09-14

- Fixed plugin loading when installed (commands at the plugin root, skills as directories).

## 1.5.0 — 2026-09-12

- Corrected UML use case diagram conventions: system actors as `«system»` rectangles, human
  actors as stick figures / `fa:fa-user`, one `UC-<n>` code per bubble across all diagrams.

## 1.4.0 — 2026-09-12

- `plugin.json` skill entries point at skill directories; self-validator updated accordingly.

## 1.3.0 — 2026-09-12

- First CI workflow and a placeholder licence (replaced in 1.8.0).

## Earlier (unversioned)

- Initial plugin: router + drivers, quality attributes, QAW, ADD 3.0, ATAM, Views-and-Beyond,
  diagrams; drivers register as a directory; utility tree as a table; two-notation worked example;
  `references/` body of knowledge; `mdreport.py` Markdown → Markdown/HTML report builder.
