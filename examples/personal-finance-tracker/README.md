# Worked example — Personal Finance Tracker

A small SaaS personal-finance web app, carried through the SEI activities so you can see the shape
of each artifact. Not a real product; the numbers are illustrative.

| File | Produced by | Shows |
|------|-------------|-------|
| [`drivers.md`](drivers.md) | `/drivers` | The four driver kinds with the attribute-prefixed ID scheme (`BG-`, `UC-`, `CON-`, `AQA-`/`SQA-`/`PQA-`/`MQA-`/…), full use cases, and a traceability matrix with no orphan drivers |
| [`add/personal-finance-tracker-session.md`](add/personal-finance-tracker-session.md) | `/add` | An ADD 3.0 session log — iteration plan + iteration 1 (structure, security choke point, availability topology) across the seven activities |
| [`add/personal-finance-tracker-Architecture.md`](add/personal-finance-tracker-Architecture.md) | `/add` | The companion architecture document — 9 sections, context / container / component / sequence / deployment views in the flowchart-C4 house style, interfaces, and an ADR-style decision log |
| [`diagrams/`](diagrams/) | `/sei-diagram` | `.mmd` sources and rendered, visually-verified PNGs: a use-case diagram, a six-part quality-attribute-scenario diagram, and the architecture views |
| [`reports/architecture-package.html`](reports/architecture-package.html) | `scripts/build-report.sh` | `drivers.md` + the architecture document combined into one self-contained HTML report with the diagrams embedded, a cover page and a table of contents |

## Regenerate the diagrams and the report

```bash
# from the plugin root
bash skills/sei-diagrams/scripts/setup.sh          # one-time

bash skills/sei-diagrams/scripts/render.sh \
  examples/personal-finance-tracker/diagrams/

bash skills/sei-diagrams/scripts/render.sh --out examples/personal-finance-tracker/diagrams \
  examples/personal-finance-tracker/add/personal-finance-tracker-Architecture.md

scripts/build-report.sh \
  examples/personal-finance-tracker/drivers.md \
  examples/personal-finance-tracker/add/personal-finance-tracker-Architecture.md \
  --format both --embed-diagrams \
  --title "Personal Finance Tracker — Architecture Package" \
  --out examples/personal-finance-tracker/reports/architecture-package.html
```

## Validate

```bash
python tests/validate.py examples/personal-finance-tracker/**/*.md
```
