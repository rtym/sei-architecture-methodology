# Quality attribute scenarios

Index for `drivers/quality-attributes/`. The authoritative traceability matrix is in the
[drivers README](../README.md). Grouped by ISO/IEC 25010 characteristic, in the same order as
the [utility tree](utility-tree.md). Each scenario has its own horizontal six-part scenario
diagram.

| ID | ISO 25010 characteristic / sub | One-line scenario | (V, R) | Diagram | Status |
|----|-------------------------------|-------------------|:------:|---------|:------:|
| [SQA-1](SQA-1.md) | Security / confidentiality | Cross-user access rejected + logged; 0 reads | (H, H) | [scenario](diagrams/scenario-SQA-1.png) | in design |
| [AQA-1](AQA-1.md) | Reliability / availability | Single-AZ failure recovers < 60 s; ≥ 99.5 %/mo | (H, H) | [scenario](diagrams/scenario-AQA-1.png) | open |
| [PQA-1](PQA-1.md) | Performance efficiency / time behaviour | Dashboard < 1.5 s @ p95, 500 concurrent | (H, M) | [scenario](diagrams/scenario-PQA-1.png) | open |
| [PQA-2](PQA-2.md) | Performance efficiency / capacity | 5 000-row CSV import < 30 s, interactive unaffected | (M, M) | [scenario](diagrams/scenario-PQA-2.png) | open |
| [MQA-1](MQA-1.md) | Maintainability / modifiability | Add a report type in ≤ 1 person-day, 0 regressions | (M, M) | [scenario](diagrams/scenario-MQA-1.png) | open |
| [UQA-1](UQA-1.md) | Interaction capability / operability | First transaction without help; ≥ 85 % completion | (M, M) | [scenario](diagrams/scenario-UQA-1.png) | open |

**[Utility tree (table) →](utility-tree.md)** — the summary of these quality attributes, `(V, R)`
per leaf; `★` on each `(H, H)` leaf. ISO/IEC 25010:2023.

---

**Navigation**: [drivers README](../README.md) · [example root](../../README.md)
