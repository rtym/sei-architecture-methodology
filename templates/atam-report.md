# ATAM Evaluation — <system>

- **Date(s)**: <YYYY-MM-DD>
- **Evaluation team**: <names / roles>
- **Architect(s)**: <names>
- **Architecture evaluated**: <path / version>
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

<indented list + Mermaid mindmap — see templates/utility-tree.md>


![Utility tree](diagrams/utility-tree.png) — visually verified: y/n

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
| S-1 | Sensitivity point | | | |
| T-1 | Tradeoff point | | <attr A> vs <attr B> | |

## Step 7 — Brainstorm and prioritise scenarios (Phase 2)

**Vote budget** = ceil(0.30 × <count>) = **<N>** per stakeholder.

| ID | Scenario | Type (use-case / growth / exploratory) | Votes |
|----|----------|----------------------------------------|-------|
| P-1 | | | |

Ranked: P-3 (8) > P-1 (5) > … · Agreement with utility tree: <notes>

## Step 8 — Analyse architectural approaches (Phase 2 scenarios)

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
