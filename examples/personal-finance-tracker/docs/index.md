# Architecture Description — Personal Finance Tracker

Views-and-Beyond documentation package. This file is the **documentation roadmap**.

## How this documentation is organised

| File | V&B part | Read it to… |
|------|----------|-------------|
| `index.md` (this file) | Roadmap + organisation | know what exists and where to look |
| `system-overview.md` | System overview | understand what the system does and its context |
| `view-module-decomposition.md` | Module view (decomposition) | see the code units and who owns what |
| `view-cnc-runtime.md` | Component-and-Connector view (service) | see what runs and how parts interact at runtime |
| `view-allocation-deployment.md` | Allocation view (deployment) | see where each part runs in production |
| `mapping-between-views.md` | Mapping between views | correlate a module ↔ runtime component ↔ node |
| `rationale.md` | Rationale | understand why the big decisions were made (ADR log) |
| `directory.md` | Directory | look up a term, an acronym, or where an element is defined |

Only a stub view set is included in this example (one view per viewtype). A real package adds a
uses/layered module view, more C&C views, and install / work-assignment allocation views as
stakeholder concerns require.

## View selection — stakeholder concerns → views

| Stakeholder | Concern | View(s) |
|-------------|---------|---------|
| New developer | Where does the code live? What can depend on what? | Module decomposition |
| Developer / architect | What runs at runtime? How is tenant isolation enforced? | C&C runtime |
| Performance | Where is the dashboard latency budget spent? | C&C runtime + sequence diagrams in the ADD `Architecture.md` §6 |
| Operations | What is deployed where? How does it survive an AZ loss? | Allocation deployment |
| Security / auditor | Where is the confidentiality control? | C&C runtime + `rationale.md` |
| Project lead | Who is responsible for which module? | Module decomposition (owner column) |

## Where do I look to answer…

- *"If I change the category logic, what else is affected?"* → Module decomposition (dependencies).
- *"How is `SQA-1` (cross-user isolation) achieved?"* → C&C runtime view §5 rationale + `rationale.md` ADR-2.
- *"What happens on a cache miss?"* → ADD `../add/personal-finance-tracker-Architecture.md` §6.
- *"What recovers us from an AZ failure?"* → Allocation deployment view + `rationale.md` ADR-3.

## Related artifacts

- Drivers register: `../drivers.md`
- Quality attribute scenarios: `../scenarios.md`
- ADD working architecture: `../add/personal-finance-tracker-Architecture.md`
- ATAM evaluation: `../atam/atam-report.md`
