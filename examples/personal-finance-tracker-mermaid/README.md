# Worked example — Personal Finance Tracker (Mermaid notation)

A small SaaS personal-finance web app, carried through every SEI activity so you can see the
shape of each artifact. Not a real product; the numbers are illustrative. **Every diagram in
this tree is Mermaid** (use-case diagrams use the Mermaid `flowchart` fallback). The same example
drawn entirely in **PlantUML / C4-PlantUML** is at
[`../personal-finance-tracker-plantuml/`](../personal-finance-tracker-plantuml/README.md) — the
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
| ATAM evaluation | `/atam` | [atam/atam-report.md](atam/atam-report.md) | done 2026-09-07 |
| Views and Beyond documentation | `/architecture-docs` | [docs/README.md](docs/README.md) | done 2026-09-06 |
| Deliverable reports | `build-report.sh` | [reports/](reports/) | done 2026-09-06 |

## Change log

| Date | Activity | Change |
|------|----------|--------|
| 2026-08-20 | `/qaw` | workshop run; refined scenarios handed off |
| 2026-09-06 | `/drivers` | package created; initial driver set |
| 2026-09-06 | `/quality-attributes` | register-mode scenario summary added |
| 2026-09-06 | `/add` | architecture designed; ADR log started |
| 2026-09-06 | `/architecture-docs` | Views-and-Beyond package written |
| 2026-09-06 | `build-report.sh` | HTML/Markdown reports generated |
| 2026-09-07 | `/atam` | evaluation of the ADD 3.0 architecture; SQA-1 and AQA-1 set to at risk |

## Package contents

| Path | Produced by | Shows |
|------|-------------|-------|
| [`drivers/`](drivers/README.md) | `/drivers` | The drivers **directory** — [`README.md`](drivers/README.md) (ID legend, traceability matrix with no orphans, prioritised list, change log) + a `README.md` index per subdirectory + one file per driver under `business-goals/` (4), `use-cases/` (3), `constraints/` (5), `quality-attributes/` (6) |
| [`drivers/stakeholders.md`](drivers/stakeholders.md) · [`drivers/concerns/`](drivers/concerns/README.md) | `/drivers` | The **stakeholder register** (`ST-n`, read by QAW / ATAM / V&B) and the **architectural concerns** (`AC-n`, ADD input) — the two ADD 3.0 inputs that used to be re-collected per activity |
| [`drivers/use-cases/`](drivers/use-cases/README.md) | `/drivers` + `/sei-diagram` | Each use case with its own use case diagram (Mermaid `flowchart` fallback — actors outside the boundary, use cases inside, dashed `include`/`extend`) rendered to `diagrams/UC-<n>.png`, plus an overview diagram |
| [`drivers/quality-attributes/`](drivers/quality-attributes/README.md) | `/drivers` | Each quality attribute as a **six-part scenario** + its own **horizontal** six-part scenario diagram; [`utility-tree.md`](drivers/quality-attributes/utility-tree.md) — the summary of the QA drivers **as a table** (business value and technical risk per leaf) |
| [`qaw/qaw-report.md`](qaw/qaw-report.md) | `/qaw` | The SEI 8-step workshop + Step 9 **utility tree** (a table) built from the refined scenarios (handed to `/drivers`) |
| [`qaw/qaw-prep.md`](qaw/qaw-prep.md) · [`qaw/qaw-agenda.md`](qaw/qaw-agenda.md) · [`qaw/qaw-vote-sheet.md`](qaw/qaw-vote-sheet.md) · [`qaw/qaw-tally.md`](qaw/qaw-tally.md) · [`qaw/qaw-summary.md`](qaw/qaw-summary.md) | `scripts/qawkit.py` | The **QAW kit**, generated from the documentation. For the next workshop, a refresh run remotely: the preparation sheet (documented answers to confirm, characteristics set aside last time with their reasons, the regulated-data questions, each participant's questions, open parked questions) and the three-session agenda. From the half-day workshop on 2026-08-20: the vote sheet as filled in, its tally (the source of the report's Step 7), and the one-page summary for the sponsor |
| [`quality-attributes/scenarios.md`](quality-attributes/scenarios.md) | `/quality-attributes` | **Register-mode** summary — six-part table + links to the per-scenario files and diagrams in `drivers/quality-attributes/`; no duplicated copy |
| [`add/`](add/personal-finance-tracker-Architecture.md) | `/add` | An ADD 3.0 session log + companion architecture document — 9 sections incl. a module decomposition view and an [`adr/`](add/adr/ADR-1.md) log; context / container / component / sequence / deployment views in the flowchart-C4 house style (C4 principles); interfaces; ADR-style decisions |
| [`docs/`](docs/README.md) | `/architecture-docs` | A Views-and-Beyond package — roadmap ([`README.md`](docs/README.md)), system overview, one view packet per viewtype (Module / C&C / Allocation), mapping between views, rationale + ADRs, directory, change log |
| [`reports/`](reports/) | `scripts/build-report.sh` | `architecture-package.*` (drivers + ADD architecture) and `vandb-architecture-description.*` (the `docs/` package ordered per the V&B structure) — self-contained HTML with diagrams embedded, cover page and TOC |

## Regenerate the diagrams and the reports

```bash
# from the plugin root
bash skills/sei-diagrams/scripts/setup.sh          # one-time (Mermaid renderer)

EX=examples/personal-finance-tracker-mermaid

# every diagram in the tree, rendered to the PNG its document shows: the standalone .mmd files
# (drivers, QAW, docs legend) beside their source, and the Mermaid blocks embedded in the ADD
# architecture and the docs views (a `%% name:` names the PNG; other blocks are numbered)
bash scripts/render-all.sh $EX

# check the layout of every standalone source: crossings, overlaps, palette
python3 skills/sei-diagrams/scripts/diagramlint.py $(find $EX -name '*.mmd')

# combined report
scripts/build-report.sh \
  $EX/drivers/README.md \
  $EX/add/personal-finance-tracker-Architecture.md \
  --format both --embed-diagrams --title "Personal Finance Tracker — Architecture Package" \
  --out $EX/reports/architecture-package.html

# Views-and-Beyond report
scripts/build-report.sh --profile vandb $EX/docs/ \
  --format both --embed-diagrams --title "Architecture Description — Personal Finance Tracker" \
  --out $EX/reports/vandb-architecture-description.html
```

## Regenerate the QAW kit

```bash
# from the plugin root — the committed files are golden fixtures: tests/test_qawkit.py fails if they drift
EX=examples/personal-finance-tracker-mermaid
python3 scripts/qawkit.py prep --drivers $EX/drivers --previous-report $EX/qaw/qaw-report.md \
  --domain regulated --system "Personal Finance Tracker" --date 2026-11-02 --out $EX/qaw/qaw-prep.md
python3 scripts/qawkit.py agenda --format remote --date 2026-11-10 --start 10:00 \
  --system "Personal Finance Tracker" --out $EX/qaw/qaw-agenda.md
python3 scripts/qawkit.py tally   $EX/qaw/qaw-vote-sheet.md --out $EX/qaw/qaw-tally.md
python3 scripts/qawkit.py summary $EX/qaw/qaw-report.md --out $EX/qaw/qaw-summary.md
python3 scripts/qawkit.py status  $EX/qaw/qaw-report.md     # prints progress and gaps
python3 scripts/qawkit.py lint    $EX/qaw/qaw-report.md     # prints scenario smells; exits 1 if any
```

`qaw-vote-sheet.md` is the sheet `qawkit.py ballot` wrote, with the votes filled in by hand;
the test checks that emptying its vote cells gives the ballot back, and that the report's Step 7
is the tally's block. Regenerate the ballot only when the consolidated scenarios change.

## Validate

```bash
python tests/validate.py examples/personal-finance-tracker-mermaid/drivers   # directory: cross-file + every file
python tests/validate.py examples/personal-finance-tracker-mermaid/**/*.md
```
