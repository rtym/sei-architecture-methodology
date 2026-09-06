# Quality Attribute Utility Tree: <system>

- **Date**: <YYYY-MM-DD>
- **Purpose**: prioritise quality-attribute requirements as scenarios (input to ATAM step 6 / ADD)

The utility tree is a **table**, not a diagram. It has three levels: the **root** ("Utility" —
overall fitness for purpose), the **quality attribute** (an ISO/IEC 25010 characteristic, with
a short *refinement* naming the specific concern), and the **leaf scenarios**. Each leaf is a
concrete quality attribute scenario with an explicit response and a numeric response measure.

Each leaf carries a **priority pair `(V, R)`**:

- **V — business value**: `H` = must-have (its omission would be project failure), `M` =
  important but not fatal if dropped, `L` = nice to have.
- **R — technical risk**: `H` = hard to achieve / touches much of the architecture / keeps you
  up at night, `M` = a concern but manageable, `L` = confident it can be met.

`V ≈ importance to the business`; `R ≈ architectural difficulty`. A leaf that is **`(H, H)`** is
architecturally significant — mark it `★`.

## Utility tree — Root: Utility (fitness for purpose)

| Quality attribute | Refinement (concern) | Leaf scenario (ID — one line, with the response measure) | Priority (V, R) | Status |
|-------------------|----------------------|---------------------------------------------------------|:---------------:|:------:|
| Performance efficiency | Time behaviour | `PQA-1` — dashboard interactive < 1.5 s @ p95 under 500 concurrent users | (H, M) | open |
| Performance efficiency | Capacity | `PQA-2` — sustain 50 req/s write throughput with < 1 % error | (M, M) | open |
| Reliability | Availability | `AQA-1` — single-AZ failure recovers < 60 s; ≥ 99.5 %/mo | (H, H) `★` | open |
| Reliability | Recoverability | `RQA-1` — restore from backup within RTO 4 h, RPO 15 min | (M, M) | open |
| Security | Confidentiality | `SQA-1` — 0 successful cross-tenant reads; 100 % of attempts logged | (H, H) `★` | open |
| Maintainability | Modifiability | `MQA-1` — add a report type in ≤ 1 person-day, 0 regressions | (M, M) | open |

`Status` ∈ `open` / `in design` / `partially` / `addressed` / `retired`.

## Reading the tree

- A quality attribute or refinement with **no** leaf scenario is not automatically an omission
  — but investigate whether there is an unrecorded ASR in that area.
- The `★` `(H, H)` leaves deserve the most design attention; a large number of them is itself a
  signal to question whether the system as scoped is achievable.
- Track which leaves are `addressed` vs still `open` as ADD iterations and ATAM findings land.

## Analysis targets

The `(H,H)` and `(H,M)` leaves are analysed first by ADD iterations and ATAM: e.g. `SQA-1`,
`AQA-1`, `PQA-1`.
