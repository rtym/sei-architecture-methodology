# Architecture package — <SystemName>

- **Date**: <YYYY-MM-DD>
- **Owner**: <name>
- **Design purpose**: greenfield system | greenfield feature | brownfield replacement | brownfield extension | brownfield migration
- **Stakeholders**: [drivers/stakeholders.md](drivers/stakeholders.md)

> The index of `architecture/`. Every SEI activity registers its output here, so each sub-package's
> Navigation footer links **up** to this file and only **across** to packages that already exist.
> `/drivers` creates this file; every other skill updates its row and appends to the change log.
> Never link an output that has not been produced yet — `validate.py` fails on the broken link.

## Activities and outputs

| Activity | Command | Output | Status |
|----------|---------|--------|--------|
| Architectural drivers | `/drivers` | [drivers/README.md](drivers/README.md) | done <YYYY-MM-DD> |
| Quality attribute scenarios | `/quality-attributes` | `quality-attributes/scenarios.md` (link once it exists) | not run |
| Quality Attribute Workshop | `/qaw` | `qaw/qaw-report.md` | not run |
| ADD 3.0 design | `/add` | `add/<slug>-Architecture.md` + `add/adr/` | not run |
| ATAM evaluation | `/atam` | `atam/atam-report.md` | not run |
| Views and Beyond documentation | `/architecture-docs` | `docs/README.md` | not run |
| Deliverable reports | `build-report.sh` | `reports/` | not run |

## Change log

| Date | Activity | Change |
|------|----------|--------|
| <YYYY-MM-DD> | `/drivers` | package created; initial driver set |
