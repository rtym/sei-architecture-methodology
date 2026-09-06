# Quality Attribute Workshop — <system>

- **Date(s)**: <YYYY-MM-DD>
- **Facilitator(s)**: <names>
- **Sponsor**: <name>
- **Status**: in progress | complete

---

## Step 1 — QAW presentation and introductions

### Participants

| Name | Role | Concerns brought |
|------|------|------------------|
| | architect / dev / test / integrator / ops / security / product / sponsor / user rep | |

### Expected outputs
Raw scenarios · consolidated scenarios · prioritised scenarios · refined (six-part) scenarios.

## Step 2 — Business / mission drivers

| ID | Business driver / goal |
|----|------------------------|
| BG-1 | |

**Quality attributes the business named**: <list>
**Key functional requirements**: <list>
**Constraints**: <list>

## Step 3 — Architectural plan presentation

- **System boundary**: 
- **Known technical constraints**: 
- **External systems / interfaces**: 
- **Existing architectural context** (or "none yet"): 

## Step 4 — Architectural drivers

| ID | Architectural driver | Kind (QA / FR / constraint) | Supports |
|----|----------------------|----------------------------|----------|
| AD-1 | | | BG-1 |

## Step 5 — Scenario brainstorming (raw, verbatim)

| ID | Scenario (stimulus · environment · response) | Contributor | Driver(s) |
|----|----------------------------------------------|-------------|-----------|
| S-1 | | | AD-1 |

## Step 6 — Scenario consolidation

| Consolidated ID | Merged from | Scenario |
|-----------------|-------------|----------|
| CS-1 | S-1, S-4 | |

Dissent / notes: <record any objection to a merge>

## Step 7 — Scenario prioritisation

**Vote budget** = ceil(0.30 × <consolidated count>) = **<N>** votes per stakeholder.

| Scenario | <stakeholder A> | <stakeholder B> | … | Total |
|----------|-----------------|-----------------|---|-------|
| CS-1 | 2 | 1 | | 3 |

**Ranked**: CS-3 (7) > CS-1 (3) > …

## Step 8 — Scenario refinement (top scenarios)

### CS-<id> — <short name>

| Part | Value |
|------|-------|
| Source of stimulus | |
| Stimulus | |
| Artifact | |
| Environment | |
| Response | |
| Response measure | <numeric> |

- **Business goals**: BG-<…>
- **Relevant quality attributes (ISO/IEC 25010)**: <characteristic / sub>
- **Six-part scenario diagram**: 

![CS-<id> six-part scenario](../diagrams/scenario-CS-<id>.png) — visually verified: y/n
- **Questions**: <how would the architecture achieve this?>
- **Issues / assumptions**: 

## Next steps

- Feed refined scenarios into `architectural-drivers` as `<ATTR>QA-n` and into `/attribute-driven-design`.
- Schedule an ATAM once an architecture exists.
