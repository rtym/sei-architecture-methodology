# ATAM Evaluation — <SystemName>

- **Date(s)**: <YYYY-MM-DD>
- **Evaluation team**: <names / roles>
- **Architect(s)**: <names>
- **Architecture evaluated**: <path / version>
- **Mode**: Full ATAM | Lightweight Architecture Evaluation (Steps 7–8 omitted)
- **Stakeholders**: [`../drivers/stakeholders.md`](../drivers/stakeholders.md)
- **Status**: Phase 1 | Phase 2 | Phase 3 complete

---

## Phase 0 — Partnership and preparation

- **Scope**: 
- **Stakeholders for Phase 2**: 
- **Schedule**: 

## Step 1 — Present the ATAM
Method and outputs explained: approaches, utility tree, scenario analyses, risks, non-risks,
sensitivity points, tradeoff points, risk themes.

## Step 2 — Present the business drivers

| ID | Business goal |
|----|---------------|
| BG-1 | |

- **Primary functional requirements**: 
- **Constraints**: 
- **Most important quality attributes**: 

## Step 3 — Present the architecture

- **Technical constraints**: 
- **External systems**: 
- **Overview** (context → containers → key components; key flows; deployment): 
- Diagrams (```mermaid block + image line): ![…](diagrams/….png) — visually verified: y/n

## Step 4 — Identify architectural approaches

| ID | Approach / style / tactic | Where applied | Intended quality attribute |
|----|---------------------------|---------------|----------------------------|
| AA-1 | Layered | whole system | modifiability |
| AA-2 | Cache-aside (Redis) | dashboard read path | performance |

## Step 5 — Quality attribute utility tree

A **table** (see `${CLAUDE_PLUGIN_ROOT}/templates/utility-tree.md`). `(V, R)` = (business value, technical risk);
`★` = architecturally significant (H, H).

| Quality attribute | Refinement (concern) | Leaf scenario (ID — one line + measure) | Priority (V, R) | Status |
|-------------------|----------------------|----------------------------------------|:---------------:|:------:|
| Security | Confidentiality | SQA-1 — 0 cross-tenant reads; 100 % logged | (H, H) `★` | open |
| Reliability | Availability | AQA-1 — AZ failure recovers < 60 s; ≥ 99.5 %/mo | (H, H) `★` | open |
| Performance efficiency | Time behaviour | PQA-1 — dashboard < 1.5 s @ p95, 500 concurrent | (H, M) | open |

_Reading the tree_: a refinement with no leaf → look for an unrecorded ASR; the `★` `(H,H)`
leaves get the most analysis. The `★` and `(H,M)` leaves are what Step 6 analyses.

## Step 6 — Analyse architectural approaches (Phase 1 scenarios)

### <ATTR>QA-id — <one-line scenario> (Imp, Diff)
- **Attribute / refinement**: <ISO 25010 characteristic / refinement>
- **Approaches invoked**: AA-1, AA-2
- **Analysis questions & answers**:
  - Q: … A: …

| Finding | Type | Element / decision | Affected attribute(s) | Note |
|---------|------|--------------------|-----------------------|------|
| R-1 | Risk | | | |
| N-1 | Non-risk | | | assumption: … |
| SP-1 | Sensitivity point | | | |
| TP-1 | Tradeoff point | | <attr A> vs <attr B> | |

## Step 7 — Brainstorm and prioritise scenarios (Phase 2 — Full ATAM only; omit in Lightweight mode)

**Vote budget** = ceil(0.30 × <count>) = **<N>** per stakeholder.

| ID | Scenario | Type (use-case / growth / exploratory) | Votes |
|----|----------|----------------------------------------|-------|
| P-1 | | | |

Ranked: P-3 (8) > P-1 (5) > … · Agreement with utility tree: <notes>

## Step 8 — Analyse architectural approaches (Phase 2 scenarios — Full ATAM only)

<repeat the Step 6 analysis structure for the top Phase 2 scenarios not already covered>

## Step 9 — Results

### Architectural approaches
<consolidated AA- list>

### Risks
| ID | Risk | Affected attribute | Related driver |
|----|------|--------------------|----------------|

### Non-risks
| ID | Non-risk | Assumption under which it holds |
|----|----------|--------------------------------|

### Sensitivity points
| ID | Element property | Attribute affected | Direction |
|----|------------------|--------------------|-----------|

### Tradeoff points
| ID | Element property | Attribute A ↑ | Attribute B ↓ |
|----|------------------|---------------|---------------|

### Risk themes
| Theme | Risks | Business driver(s) endangered | Recommendation |
|-------|-------|------------------------------|----------------|
| RT-1 | R-1, R-4, R-7 | BG-3 | ADD iteration targeting availability of the cache tier |

### Recommendations / next steps
- <targeted ADD iterations, spikes, monitoring, doc updates>

### Drivers register write-back
- Scenarios with ≥ 1 Risk set to `at risk` in [`../drivers/README.md`](../drivers/README.md): <ATTR>QA-<n> (R-…), …
- Change-log line appended to the drivers README and to the package index `../README.md`.
