# PQA-1: Dashboard fast under load

- **Status**: open
- **Source**: authored here (kept in sync with [`../../quality-attributes/scenarios.md`](../../quality-attributes/scenarios.md))

Documented as a **six-part quality attribute scenario** and supported by its own **horizontal
six-part scenario diagram**.

| Part | Value |
|------|-------|
| **ID** | PQA-1 |
| **ISO/IEC 25010 characteristic** | Performance efficiency |
| **Sub-characteristic** | time behaviour |
| **Source of stimulus** | Registered user |
| **Stimulus** | Loads the monthly dashboard with 500 concurrent users |
| **Artifact** | Dashboard read path |
| **Environment** | Normal operation |
| **Response** | Renders totals, category chart, recent activity and savings-goal progress |
| **Response measure** | Fully interactive < 1.5 s at p95 |
| **Business goals supported** | BG-1 |
| **Priority** | Importance = H · Difficulty = M |
| **Candidate tactics** | **Performance** — *manage resources*: maintain multiple copies of computations (cache-aside), introduce concurrency, increase resources; *control resource demand*: reduce overhead, bound execution times |
| **Type** | concrete |

## Six-part scenario diagram

Read left to right: the source of stimulus produces the stimulus, which arrives at the artifact in
the environment shown; the artifact's response follows, and the last box is how it is measured.

![PQA-1 six-part scenario](diagrams/scenario-PQA-1.png)

Source: [`diagrams/scenario-PQA-1.puml`](diagrams/scenario-PQA-1.puml).

## Notes / assumptions

`p95` is the 95th percentile: the limit holds for 95 % of requests, and the slowest 5 % may
exceed it.

See [`../README.md`](../README.md) for traceability and the utility tree.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) · [utility tree](utility-tree.md)
