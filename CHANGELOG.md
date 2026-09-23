# Changelog

All notable changes to the `sei-architecture-methodology` plugin. Versions follow
[SemVer](https://semver.org/); the version lives in `.claude-plugin/plugin.json` and is mirrored in
`.claude-plugin/marketplace.json` (both places) — `tests/validate.py --self` fails on drift.

## Unreleased

### Fixed
- CI's PlantUML "render every example diagram" step asserted a hardcoded count of committed
  `.puml` files (29) that drifted stale after the 1.10.0 diagram dedup left 26. Now derived from
  `git ls-files` at run time so it can't drift again.

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
