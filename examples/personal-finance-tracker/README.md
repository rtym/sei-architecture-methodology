# Worked example — Personal Finance Tracker

A small SaaS personal-finance web app, carried through every SEI activity so you can see the shape
of each artifact. Not a real product; the numbers are illustrative. Every diagram here was
rendered and visually cross-verified.

| Path | Produced by | Shows |
|------|-------------|-------|
| [`drivers/`](drivers/) | `/drivers` | The drivers **directory** — `index.md` (ID legend, traceability matrix with no orphans, prioritised list, change log) + one file per driver under `business-goals/` (4), `use-cases/` (3), `constraints/` (5), `quality-attributes/` (6) |
| [`drivers/use-cases/`](drivers/use-cases/) | `/drivers` + `/sei-diagram` | Each use case with its own **proper UML use case diagram** (PlantUML — stick-figure actors, ellipse use cases, boundary rectangle, dashed `<<include>>`) rendered to `diagrams/UC-<n>.png`, plus an overview diagram |
| [`drivers/quality-attributes/`](drivers/quality-attributes/) | `/drivers` | Each quality attribute as a **six-part scenario** + its own **horizontal** six-part scenario diagram; `utility-tree.md` — the summary of the QA drivers, rendered as a `mindmap` |
| [`qaw/qaw-report.md`](qaw/qaw-report.md) | `/qaw` | The SEI 8-step workshop + Step 9 **utility tree** built from the refined scenarios (handed to `/drivers`) |
| [`scenarios.md`](scenarios.md) | `/quality-attributes` | The dedicated quality-attribute run — six-part scenarios, ISO/IEC 25010, utility tree, prioritised drivers |
| [`add/`](add/) | `/add` | An ADD 3.0 session log + companion architecture document — 9 sections, context / container / component / sequence / deployment views in the flowchart-C4 house style (C4 principles), interfaces, ADR-style decisions; diagrams embedded as `mermaid` + `![](../diagrams/*.png)` |
| [`docs/`](docs/) | `/architecture-docs` | A Views-and-Beyond package — roadmap (`index.md`), system overview, one view packet per viewtype (Module / C&C / Allocation), mapping between views, rationale + ADRs, directory |
| [`reports/`](reports/) | `scripts/build-report.sh` | `architecture-package.*` (drivers + ADD architecture) and `vandb-architecture-description.*` (the `docs/` package ordered per the V&B structure) — self-contained HTML with diagrams embedded, cover page and TOC |

## Regenerate the diagrams and the reports

```bash
# from the plugin root
bash skills/sei-diagrams/scripts/setup.sh          # one-time (Mermaid); PlantUML needs `brew install openjdk`

# quality-attribute scenario diagrams + utility tree (Mermaid)
bash skills/sei-diagrams/scripts/render.sh \
  examples/personal-finance-tracker/drivers/quality-attributes/diagrams/

# use case diagrams (PlantUML — true UML notation)
bash skills/sei-diagrams/scripts/render-plantuml.sh \
  examples/personal-finance-tracker/drivers/use-cases/diagrams/

# ADD architecture views
bash skills/sei-diagrams/scripts/render.sh --out examples/personal-finance-tracker/diagrams \
  examples/personal-finance-tracker/add/personal-finance-tracker-Architecture.md

# combined report
scripts/build-report.sh \
  examples/personal-finance-tracker/drivers/index.md \
  examples/personal-finance-tracker/add/personal-finance-tracker-Architecture.md \
  --format both --embed-diagrams --title "Personal Finance Tracker — Architecture Package" \
  --out examples/personal-finance-tracker/reports/architecture-package.html

# Views-and-Beyond report
scripts/build-report.sh --profile vandb examples/personal-finance-tracker/docs/ \
  --format both --embed-diagrams --title "Architecture Description — Personal Finance Tracker" \
  --out examples/personal-finance-tracker/reports/vandb-architecture-description.html
```

## Validate

```bash
python tests/validate.py examples/personal-finance-tracker/drivers   # directory: cross-file + every file
python tests/validate.py examples/personal-finance-tracker/**/*.md
```
