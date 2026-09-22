# Changelog

All notable changes to the `sei-architecture-methodology` plugin. Versions follow
[SemVer](https://semver.org/); the version lives in `.claude-plugin/plugin.json` and is mirrored in
`.claude-plugin/marketplace.json` (both places) — `tests/validate.py --self` fails on drift.

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
