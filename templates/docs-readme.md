# Architecture Description — <SystemName>

<One or two plain sentences: this is the documentation roadmap of the Views-and-Beyond package for
<SystemName>; start with the table below.>

## How this documentation is organised

| File | V&B part | Read it to… |
|------|----------|-------------|
| [`README.md`](README.md) (this file) | Roadmap + organisation | know what exists and where to look |
| [`system-overview.md`](system-overview.md) | System overview | understand what the system does and its context |
| [`view-<name>.md`](view-<name>.md) | <Module / C&C / Allocation> view (<style>) | <the question this view answers> |
| [`mapping-between-views.md`](mapping-between-views.md) | Mapping between views | correlate a module ↔ runtime component ↔ node |
| [`rationale.md`](rationale.md) | Rationale | understand why the big decisions were made (ADR log) |
| [`directory.md`](directory.md) | Directory | look up a term, an acronym, or where an element is defined |
| [`change-log.md`](change-log.md) | — | revision history of this description |

Every view in this package shares one key — [`diagrams/legend.png`](diagrams/legend.png) — referenced
from each view packet's §1 rather than repeated inside every diagram.

## View selection — stakeholder concerns → views

| Stakeholder | Concern | View(s) |
|-------------|---------|---------|
| <role> | <the question they need answered> | [<view>](view-<name>.md) |

## Where do I look to answer…

- *"<a question a reader will have>"* → [<view or file>](view-<name>.md) <section>.

## Related artifacts

- Drivers register: [`../drivers/README.md`](../drivers/README.md)
- Quality attribute scenarios: [`../quality-attributes/scenarios.md`](../quality-attributes/scenarios.md)
- ADD architecture: [`../add/<slug>-Architecture.md`](../add/<slug>-Architecture.md)

---

**Navigation**: [architecture package](../README.md) · [drivers](../drivers/README.md)
