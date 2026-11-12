# Contributor notes for Claude Code

This repository **is** a Claude Code plugin (and a one-plugin marketplace). Everything a user's
Claude reads at runtime — `commands/`, `skills/*/SKILL.md`, `templates/`, `references/` — runs with
the **user's project** as the working directory, never this repo. Keep that in mind for every path.

## Run the tests before and after any change

```bash
bash tests/run.sh --quick    # seconds: structure, validator self-check, examples, mdreport, diagram baseline
bash tests/run.sh            # + render smoke tests and a re-render of every example diagram (needs the toolchain below)
claude plugin validate .     # the official manifest check
```

Toolchain for the full suite: `bash skills/sei-diagrams/scripts/setup.sh` (Node 18+, installs the
lockfile-pinned Mermaid CLI + Chromium) and `brew install openjdk plantuml graphviz`.

## Conventions the self-check enforces

- Every cross-file path in a command, skill, template or reference is `${CLAUDE_PLUGIN_ROOT}`-anchored
  (including `${CLAUDE_PLUGIN_ROOT}/tests/validate.py`). A bare `references/x.md` is a bug.
- PlantUML `!include`s are bare, assets-relative names (`plantuml-theme.puml`, `c4/C4_Container.puml`);
  never `../`, never `<C4/…>`.
- Quality attribute scenario IDs are attribute-prefixed (`AQA-1`, `SQA-2`); the flat `QAS-<n>` is banned.
- A skill aliased by a differently-named `commands/*.md` carries `user-invocable: false`; `version:`
  is not a SKILL.md field.
- `plugin.json` and both version fields in `marketplace.json` must agree.
- Every embedded Mermaid block obeys the ten diagram rules in `skills/sei-diagrams/SKILL.md`.
- Every generated artifact keeps its template's headings — same sections, levels, order
  (`validate.py` checks; a placeholder heading repeats, a heading saying *optional* may be left
  out). A new template must be added to `STRUCTURE_TEMPLATES` in `tests/validate.py`.
- A diagram sets no colour outside the SEI palette (`assets/palette.md`); `tests/diagramcheck.py`
  checks the examples' sources and every fenced diagram in a skill, template or reference.
- Diagrams are embedded as `![title](diagrams/x.png)` image lines (plus the fenced block for
  Mermaid, plus a `.puml` link for PlantUML) — never a bare backtick path.

## When you change behaviour

1. Update the skill **and** its template **and** both worked examples under `examples/` — they are
   the regression fixtures; `tests/run.sh` validates every file in them.
2. Re-render any diagram whose source changed (`skills/sei-diagrams/scripts/render.sh` /
   `render-plantuml.sh`, or `scripts/render-all.sh <dir>` for every source under a directory),
   then run `skills/sei-diagrams/scripts/diagramlint.py` on the source, open the PNG and check
   it before committing it. Then record the new approved state with
   `python3 tests/diagramcheck.py --update` (needs both renderers) and read its diff: the
   baseline holds each example diagram's source hash, size, element counts and layout defects,
   and the suite fails when a source and its PNG disagree or a fresh render is worse than the
   baseline. Re-render only the diagrams you changed — a Mermaid PNG is not byte-identical from
   run to run. Both render scripts write the PNG
   **next to its source** — extra arguments are more inputs, not an output path (an
   output-looking `.png`/`.svg` argument is rejected; use `--out DIR` to redirect).
3. If an example's `drivers/`, `add/` or `docs/` changed, rebuild its reports (commands in the
   example README) — `tests/test_mdreport.py` compares the committed Markdown reports with a
   fresh build. If an example's `drivers/` or `qaw/qaw-report.md` changed, regenerate its QAW kit with
   `scripts/qawkit.py` (commands in the example README) — `tests/test_qawkit.py` compares the
   committed `qaw-prep.md`, `qaw-agenda.md`, `qaw-tally.md` and `qaw-summary.md` with a fresh
   run, checks that `qaw-vote-sheet.md` is the ballot with votes filled in, and that the
   report's Step 7 is the tally's block. If a skill names a new plugin file, check the Claude
   app edition still builds: `python3 scripts/appbundle.py` (`tests/test_appbundle.py` runs it).
4. Change a driver's status in an example only with `scripts/driverstatus.py` — the register
   keeps up to four copies, and `validate.py` fails when they disagree.
5. Add a line to `CHANGELOG.md` under an *Unreleased* heading (create it if needed).

## Release checklist

1. Bump the version in `.claude-plugin/plugin.json` and in **both** places in
   `.claude-plugin/marketplace.json`; rename *Unreleased* in `CHANGELOG.md` to the version + date.
2. `bash tests/run.sh && claude plugin validate .`
3. Commit, then tag `v<x.y.z>` and `sei-architecture-methodology--v<x.y.z>` (both tag styles are in use).
4. Push only when asked — pushing publishes to everyone who installed from `rtym/sei-architecture-methodology`.
5. Build the Claude app edition (`python3 scripts/appbundle.py`) and attach
   `dist/claude-app/sei-architecture-methodology-app-<x.y.z>.zip` to the GitHub release.

To bump the vendored C4-PlantUML, follow `skills/sei-diagrams/assets/c4/README.md`.

## Style

- Commit messages: English, imperative mood, one change per commit.
- Markdown artifacts are the source of truth; rendered PNGs next to their sources are committed,
  ad-hoc renders are not.
