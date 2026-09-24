# Architecture Description — Personal Finance Tracker

Views-and-Beyond documentation package. This file is the **documentation roadmap** (GitHub
renders it on directory browse). Every diagram in this package is Mermaid.

## How this documentation is organised

| File | V&B part | Read it to… |
|------|----------|-------------|
| [`README.md`](README.md) (this file) | Roadmap + organisation | know what exists and where to look |
| [`system-overview.md`](system-overview.md) | System overview | understand what the system does and its context |
| [`view-module-decomposition.md`](view-module-decomposition.md) | Module view (decomposition) | see the code units and who owns what |
| [`view-cnc-runtime.md`](view-cnc-runtime.md) | Component-and-Connector view (service) | see what runs and how parts interact at runtime |
| [`view-allocation-deployment.md`](view-allocation-deployment.md) | Allocation view (deployment) | see where each part runs in production |
| [`view-security.md`](view-security.md) | Quality view (security) | see where confidentiality is enforced and how attempts are logged (SQA-1, BG-2) |
| [`mapping-between-views.md`](mapping-between-views.md) | Mapping between views | correlate a module ↔ runtime component ↔ node |
| [`rationale.md`](rationale.md) | Rationale | understand why the big decisions were made (ADR log) |
| [`directory.md`](directory.md) | Directory | look up a term, an acronym, or where an element is defined |
| [`change-log.md`](change-log.md) | — | revision history of this description |

Every view in this package shares one key — [`diagrams/legend.png`](diagrams/legend.png) ([source](diagrams/legend.mmd)) — rendered once and referenced from each view packet's
§1 rather than repeated inside every diagram.

Only a stub view set is included in this example (one view per viewtype). A real package adds a
uses/layered module view, more C&C views, and install / work-assignment allocation views as
stakeholder concerns require.

## View selection — stakeholder concerns → views

| Stakeholder | Concern | View(s) |
|-------------|---------|---------|
| New developer | Where does the code live? What can depend on what? | [Module decomposition](view-module-decomposition.md) |
| Developer / architect | What runs at runtime? How is tenant isolation enforced? | [C&C runtime](view-cnc-runtime.md) |
| Performance | Where is the dashboard latency budget spent? | [C&C runtime](view-cnc-runtime.md) + sequence diagrams in the ADD [Architecture.md §6](../add/personal-finance-tracker-Architecture.md) |
| Operations | What is deployed where? How does it survive an AZ loss? | [Allocation deployment](view-allocation-deployment.md) |
| Security / auditor | Where is the confidentiality control? How are attempts logged? | [Security view](view-security.md) + [C&C runtime](view-cnc-runtime.md) + [`rationale.md`](rationale.md) |
| Project lead | Who is responsible for which module? | [Module decomposition](view-module-decomposition.md) (owner column) |

## Where do I look to answer…

- *"If I change the category logic, what else is affected?"* → [Module decomposition](view-module-decomposition.md) (dependencies).
- *"How is `SQA-1` (cross-user isolation) achieved?"* → [Security view](view-security.md), then [C&C runtime](view-cnc-runtime.md) §5 rationale + [`rationale.md`](rationale.md) ADR-2.
- *"What happens on a cache miss?"* → ADD [`Architecture.md`](../add/personal-finance-tracker-Architecture.md) §6.
- *"What recovers us from an AZ failure?"* → [Allocation deployment](view-allocation-deployment.md) view + [`rationale.md`](rationale.md) ADR-3.

## Related artifacts

- Drivers register: [`../drivers/README.md`](../drivers/README.md)
- Quality attribute scenarios: [`../quality-attributes/scenarios.md`](../quality-attributes/scenarios.md)
- ADD working architecture: [`../add/personal-finance-tracker-Architecture.md`](../add/personal-finance-tracker-Architecture.md)
- ATAM evaluation: [`../atam/atam-report.md`](../atam/atam-report.md)

---

**Navigation**: [example root](../README.md) · [drivers](../drivers/README.md) ·
[ADD architecture](../add/personal-finance-tracker-Architecture.md) · [ATAM](../atam/atam-report.md)
