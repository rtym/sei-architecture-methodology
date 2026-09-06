# Quality Attribute Utility Tree — Personal Finance Tracker

- **Date**: 2026-09-06
- **Built from**: the QAW refined scenarios ([`../../qaw/qaw-report.md`](../../qaw/qaw-report.md) Step 9)
- **Purpose**: the summary of the quality attributes in the architectural drivers; ATAM step 5 reuses it.

The utility tree is a **table**. Three levels are captured in the columns: the **root**
(Utility — fitness for purpose), the **quality attribute** (an ISO/IEC 25010 characteristic
with a short *refinement* naming the concern), and the **leaf scenarios**.

Each leaf carries a priority pair **`(V, R)`** — **business value** V and **technical risk** R,
each `H`/`M`/`L` (`V ≈ Importance to the business`, `R ≈ architectural difficulty`). A `(H, H)`
leaf is architecturally significant — marked `★`.

## Utility tree — Root: Utility (fitness for purpose)

| Quality attribute | Refinement (concern) | Leaf scenario (ID — one line, with response measure) | Priority (V, R) | Status |
|-------------------|----------------------|-----------------------------------------------------|:---------------:|:------:|
| Security | Confidentiality | [SQA-1](SQA-1.md) — cross-user access rejected and logged (0 successful reads; 100 % logged; alert < 1 min) | (H, H) `★` | in design |
| Reliability | Availability | [AQA-1](AQA-1.md) — traffic shifts to the healthy AZ; data tier fails over (≥ 99.5 %/month; recovery < 60 s) | (H, H) `★` | open |
| Performance efficiency | Time behaviour | [PQA-1](PQA-1.md) — dashboard interactive < 1.5 s @ p95 at 500 concurrent users | (H, M) | open |
| Performance efficiency | Capacity | [PQA-2](PQA-2.md) — 5 000-row CSV import < 30 s without hurting interactive p95 | (M, M) | open |
| Maintainability | Modifiability | [MQA-1](MQA-1.md) — add a report type in ≤ 1 person-day, ≤ 3 modules, 0 regressions | (M, M) | open |
| Interaction capability | Operability | [UQA-1](UQA-1.md) — first-time user records a transaction without help; ≥ 85 % completion | (M, M) | open |

`Status` ∈ `open` / `in design` / `partially` / `addressed` / `retired`.

## Reading the tree

- **Two leaves are architecturally significant** (`★` — high value **and** high risk):
  **SQA-1** and **AQA-1**. Both concentrate on isolation and failure handling in the single API
  service and the managed data tier.
- No quality attribute or refinement is left without a leaf scenario; if one were, that would be
  a prompt to check for an unrecorded ASR, not automatically a defect.
- Nothing is `addressed` yet; SQA-1 and UC-1 are `in design` after ADD iteration 1.

## Analysis targets

The `(H,H)` and `(H,M)` leaves are what ADD iterations and ATAM analysis target first:
**SQA-1, AQA-1, PQA-1**.

---

**Navigation**: [quality-attributes index](README.md) · [drivers README](../README.md) ·
[QAW report](../../qaw/qaw-report.md) · [ATAM report](../../atam/atam-report.md)
