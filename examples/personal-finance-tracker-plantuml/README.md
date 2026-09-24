# Worked example — Personal Finance Tracker (PlantUML / C4-PlantUML notation)

A small SaaS personal-finance web app, carried through every SEI activity so you can see the
shape of each artifact. Not a real product; the numbers are illustrative. **Every diagram in
this tree is PlantUML**: context / container / component / deployment use **C4-PlantUML**
(vendored under `skills/sei-diagrams/assets/c4/`, so it renders offline); use cases use native
PlantUML `usecase`; the six-part quality-attribute scenarios use the house PlantUML pattern. The
same example drawn entirely in **Mermaid** is at
[`../personal-finance-tracker-mermaid/`](../personal-finance-tracker-mermaid/README.md) — the
prose, drivers, scenarios and decisions are identical; only the diagram notation differs.

This file also doubles as the **architecture package index** every sub-package's Navigation
footer links up to (`/drivers` creates it from `templates/architecture-readme.md`).

## Activities and outputs

| Activity | Command | Output | Status |
|----------|---------|--------|--------|
| Quality Attribute Workshop | `/qaw` | [qaw/qaw-report.md](qaw/qaw-report.md) | done 2026-08-20 |
| Architectural drivers | `/drivers` | [drivers/README.md](drivers/README.md) | done 2026-09-06 |
| Quality attribute scenarios | `/quality-attributes` | [quality-attributes/scenarios.md](quality-attributes/scenarios.md) | done 2026-09-06 |
| ADD 3.0 design | `/add` | [add/personal-finance-tracker-Architecture.md](add/personal-finance-tracker-Architecture.md) + [add/adr/](add/adr/ADR-1.md) | done 2026-09-06 |
| ATAM evaluation | `/atam` | [atam/atam-report.md](atam/atam-report.md) | done 2026-09-05 |
| Views and Beyond documentation | `/architecture-docs` | [docs/README.md](docs/README.md) | done 2026-09-06 |
| Deliverable reports | `build-report.sh` | [reports/](reports/) | done 2026-09-06 |

## Change log

| Date | Activity | Change |
|------|----------|--------|
| 2026-08-20 | `/qaw` | workshop run; refined scenarios handed off |
| 2026-09-05 | `/atam` | evaluation of the ADD 3.0 architecture |
| 2026-09-06 | `/drivers` | package created; initial driver set |
| 2026-09-06 | `/quality-attributes` | register-mode scenario summary added |
| 2026-09-06 | `/add` | architecture designed; ADR log started |
| 2026-09-06 | `/architecture-docs` | Views-and-Beyond package written |
| 2026-09-06 | `build-report.sh` | HTML/Markdown reports generated |

## Package contents

| Path | Produced by | Shows |
|------|-------------|-------|
| [`drivers/`](drivers/README.md) | `/drivers` | The drivers **directory** — [`README.md`](drivers/README.md) (ID legend, traceability matrix with no orphans, prioritised list, change log) + a `README.md` index per subdirectory + one file per driver under `business-goals/` (4), `use-cases/` (3), `constraints/` (5), `quality-attributes/` (6) |
| [`drivers/stakeholders.md`](drivers/stakeholders.md) · [`drivers/concerns/`](drivers/concerns/README.md) | `/drivers` | The **stakeholder register** (`ST-n`, read by QAW / ATAM / V&B) and the **architectural concerns** (`AC-n`, ADD input) — the two ADD 3.0 inputs that used to be re-collected per activity |
| [`drivers/use-cases/`](drivers/use-cases/README.md) | `/drivers` + `/sei-diagram` | Each use case with its own **proper UML use case diagram** (native PlantUML — stick-figure actors, ellipse use cases, boundary rectangle, dashed `<<include>>` / `<<extend>>`) rendered to `diagrams/UC-<n>.png`, plus an overview diagram |
| [`drivers/quality-attributes/`](drivers/quality-attributes/README.md) | `/drivers` | Each quality attribute as a **six-part scenario** + its own six-part scenario diagram (PlantUML pattern); [`utility-tree.md`](drivers/quality-attributes/utility-tree.md) — the summary of the QA drivers **as a table** (`(V, R)` per leaf) |
| [`qaw/qaw-report.md`](qaw/qaw-report.md) | `/qaw` | The SEI 8-step workshop + Step 9 **utility tree** (a table) built from the refined scenarios (handed to `/drivers`) |
| [`quality-attributes/scenarios.md`](quality-attributes/scenarios.md) | `/quality-attributes` | **Register-mode** summary — six-part table + links to the per-scenario files and diagrams in `drivers/quality-attributes/`; no duplicated copy |
| [`add/`](add/personal-finance-tracker-Architecture.md) | `/add` | An ADD 3.0 session log + companion architecture document — 9 sections incl. a module decomposition view and an [`adr/`](add/adr/ADR-1.md) log; context / container / component / sequence / deployment views in **C4-PlantUML**; interfaces; ADR-style decisions |
| [`docs/`](docs/README.md) | `/architecture-docs` | A Views-and-Beyond package — roadmap ([`README.md`](docs/README.md)), system overview, one view packet per viewtype (Module / C&C / Allocation), mapping between views, rationale + ADRs, directory, change log |
| [`reports/`](reports/) | `scripts/build-report.sh` | `architecture-package.*` and `vandb-architecture-description.*` — self-contained HTML with diagrams embedded, cover page and TOC |

## Regenerate the diagrams and the reports

```bash
# from the plugin root — PlantUML needs a Java runtime (brew install openjdk)
EX=examples/personal-finance-tracker-plantuml

bash skills/sei-diagrams/scripts/render-plantuml.sh $EX/drivers/use-cases/diagrams/
bash skills/sei-diagrams/scripts/render-plantuml.sh $EX/drivers/quality-attributes/diagrams/
bash skills/sei-diagrams/scripts/render-plantuml.sh --out $EX/diagrams $EX/add/diagrams/
bash skills/sei-diagrams/scripts/render-plantuml.sh --out $EX/docs/diagrams $EX/docs/diagrams/

scripts/build-report.sh \
  $EX/drivers/README.md \
  $EX/add/personal-finance-tracker-Architecture.md \
  --format both --embed-diagrams --title "Personal Finance Tracker — Architecture Package" \
  --out $EX/reports/architecture-package.html

scripts/build-report.sh --profile vandb $EX/docs/ \
  --format both --embed-diagrams --title "Architecture Description — Personal Finance Tracker" \
  --out $EX/reports/vandb-architecture-description.html
```

## Validate

```bash
python tests/validate.py examples/personal-finance-tracker-plantuml/drivers
python tests/validate.py examples/personal-finance-tracker-plantuml/**/*.md
```
