# Worked example — Personal Finance Tracker (PlantUML / C4-PlantUML notation)

A small SaaS personal-finance web app, carried through every SEI activity so you can see the
shape of each artifact. Not a real product; the numbers are illustrative. **Every diagram in
this tree is PlantUML**: context / container / component / deployment use **C4-PlantUML**
(vendored under `skills/sei-diagrams/assets/c4/`, so it renders offline); use cases use native
PlantUML `usecase`; the six-part quality-attribute scenarios use the house PlantUML pattern. The
same example drawn entirely in **Mermaid** is at
[`../personal-finance-tracker-mermaid/`](../personal-finance-tracker-mermaid/README.md) — the
prose, drivers, scenarios and decisions are identical; only the diagram notation differs.

| Path | Produced by | Shows |
|------|-------------|-------|
| [`drivers/`](drivers/README.md) | `/drivers` | The drivers **directory** — [`README.md`](drivers/README.md) (ID legend, traceability matrix with no orphans, prioritised list, change log) + a `README.md` index per subdirectory + one file per driver under `business-goals/` (4), `use-cases/` (3), `constraints/` (5), `quality-attributes/` (6) |
| [`drivers/use-cases/`](drivers/use-cases/README.md) | `/drivers` + `/sei-diagram` | Each use case with its own **proper UML use case diagram** (native PlantUML — stick-figure actors, ellipse use cases, boundary rectangle, dashed `<<include>>` / `<<extend>>`) rendered to `diagrams/UC-<n>.png`, plus an overview diagram |
| [`drivers/quality-attributes/`](drivers/quality-attributes/README.md) | `/drivers` | Each quality attribute as a **six-part scenario** + its own six-part scenario diagram (PlantUML pattern); [`utility-tree.md`](drivers/quality-attributes/utility-tree.md) — the summary of the QA drivers **as a table** (`(V, R)` per leaf) |
| [`qaw/qaw-report.md`](qaw/qaw-report.md) | `/qaw` | The SEI 8-step workshop + Step 9 **utility tree** (a table) built from the refined scenarios (handed to `/drivers`) |
| [`quality-attributes/scenarios.md`](quality-attributes/scenarios.md) | `/quality-attributes` | The dedicated quality-attribute run — six-part scenarios, ISO/IEC 25010, tabular utility tree, prioritised drivers |
| [`add/`](add/personal-finance-tracker-Architecture.md) | `/add` | An ADD 3.0 session log + companion architecture document — 9 sections; context / container / component / sequence / deployment views in **C4-PlantUML**; interfaces; ADR-style decisions |
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
