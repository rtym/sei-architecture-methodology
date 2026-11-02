# Changelog

All notable changes to the `sei-architecture-methodology` plugin. Versions follow
[SemVer](https://semver.org/); the version lives in `.claude-plugin/plugin.json` and is mirrored in
`.claude-plugin/marketplace.json` (both places) — `tests/validate.py --self` fails on drift.

## Unreleased

### Added
- `references/qaw-question-guide.md` — the QAW facilitator's script: the questions to ask at
  every step, per ISO/IEC 25010 characteristic, per stakeholder role, for testing documentation
  that already exists, and for turning vague answers ("fast", "always up", "secure") into
  measurable scenarios.
- QAW entry modes. A workshop now starts with Step 0, *Starting point*, which picks
  **greenfield** (nothing documented), **partial** (a brief, a codebase or loose scenarios to
  correct) or **refresh** (an existing drivers register to test and extend). In refresh mode the
  existing scenarios enter brainstorming tagged *existing* and are re-voted with the new ones; a
  previous report is kept as `qaw-report-<date>.md`.
- The QAW skill now requires relying on the documentation available: before each step Claude
  checks the documents found in Step 0, confirms what they already answer (citing the source)
  instead of asking again, asks open questions only about the gaps, and records where a
  stakeholder contradicts a document. The validator rejects a partial- or refresh-mode report
  whose Starting point names no input document.
- *Parked questions* in the QAW report: a question nobody present can answer becomes a `PQ-<n>`
  row with who can answer it, an owner and a due date, instead of a guessed number.
- Validator: the entry mode must be exactly one of the three; refresh mode must carry existing
  scenarios into Step 5; every parked question needs an owner and a status. Reports written
  before this release have neither section and still pass. `--self` checks that the question
  guide keeps a question section for every step, every ISO/IEC 25010 characteristic and every
  entry mode. 25 new unit tests (80 in total).

- `scripts/qawkit.py` — generates the QAW's working artifacts from the documentation that
  already exists, deterministically: `prep` (documented answers to confirm with their sources,
  the ISO/IEC 25010 characteristics with no scenario and their questions, each participant's
  role questions, open parked questions from the last workshop), `ballot` (the Step 7 vote
  sheet with the budget computed) and `summary` (a one-page result for the sponsor). The QAW
  skill runs it at the matching steps; both worked examples carry a generated kit.
- `tests/test_qawkit.py` — 103 unit tests for the kit: every reader and builder, CLI exit
  codes, and golden files (the kit committed in each example must equal a fresh run). Wired
  into `tests/run.sh` as step 4d.

### Fixed
- An archived QAW report (`qaw-report-<date>.md`) was validated as an ADD session because
  of its dated name; it is now validated as a QAW report.

### Changed
- Both worked examples' QAW reports gain the new sections: a *partial*-mode starting point (the
  founder's brief) and three parked questions, among them the budget figure BG-4 never stated.

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
