# Contributor notes for Claude Code

This repository **is** a Claude Code plugin (and a one-plugin marketplace). Everything a user's
Claude reads at runtime — `commands/`, `skills/*/SKILL.md`, `templates/`, `references/` — runs with
the **user's project** as the working directory, never this repo. Keep that in mind for every path.

## Run the tests before and after any change

```bash
bash tests/run.sh --quick    # seconds: structure, validator self-check, examples, mdreport
bash tests/run.sh            # + Mermaid and PlantUML render smoke tests (needs the toolchain below)
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
- Diagrams are embedded as `![title](diagrams/x.png)` image lines (plus the fenced block for
  Mermaid, plus a `.puml` link for PlantUML) — never a bare backtick path.

## When you change behaviour

1. Update the skill **and** its template **and** both worked examples under `examples/` — they are
   the regression fixtures; `tests/run.sh` validates every file in them.
2. Re-render any diagram whose source changed (`skills/sei-diagrams/scripts/render.sh` /
   `render-plantuml.sh`), then open the PNG and check it before committing it.
3. Add a line to `CHANGELOG.md` under an *Unreleased* heading (create it if needed).

## Release checklist

1. Bump the version in `.claude-plugin/plugin.json` and in **both** places in
   `.claude-plugin/marketplace.json`; rename *Unreleased* in `CHANGELOG.md` to the version + date.
2. `bash tests/run.sh && claude plugin validate .`
3. Commit, then tag `v<x.y.z>` and `sei-architecture-methodology--v<x.y.z>` (both tag styles are in use).
4. Push only when asked — pushing publishes to everyone who installed from `rtym/sei-architecture-methodology`.

To bump the vendored C4-PlantUML, follow `skills/sei-diagrams/assets/c4/README.md`.

## Style

- Commit messages: English, imperative mood, one change per commit.
- Markdown artifacts are the source of truth; rendered PNGs next to their sources are committed,
  ad-hoc renders are not.
