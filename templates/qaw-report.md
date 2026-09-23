# Quality Attribute Workshop — <SystemName>

- **Date(s)**: <YYYY-MM-DD>
- **Facilitator(s)**: <names>
- **Sponsor**: <name>
- **Status**: in progress | complete

---

## Step 1 — QAW presentation and introductions

### Participants

Imported from [`../drivers/stakeholders.md`](../drivers/stakeholders.md) (create it there if it does not exist yet).

| ID | Name | Role | Concerns brought |
|----|------|------|------------------|
| ST-1 | | architect / dev / test / integrator / ops / security / product / sponsor / user rep | |

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

| ID | Scenario (stimulus · environment · response) | Type (use-case / growth / exploratory) | Contributor | Driver(s) |
|----|----------------------------------------------|----------------------------------------|-------------|-----------|
| S-1 | | use-case | | AD-1 |

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

![CS-<id> six-part scenario](diagrams/scenario-CS-<id>.png)

Rendered to `architecture/qaw/diagrams/scenario-CS-<id>.png` · visually verified: y/n
- **Questions**: <how would the architecture achieve this?>
- **Issues / assumptions**: 

## Step 9 — Quality attribute utility tree

A **table** (see `${CLAUDE_PLUGIN_ROOT}/templates/utility-tree.md`). Every refined / surviving scenario is a leaf row.
`(V, R)` = (business value, technical risk), each H/M/L; `★` = (H, H).

| Quality attribute (ISO/IEC 25010) | Refinement (concern) | Leaf scenario (ID — one line + measure) | Priority (V, R) | Status |
|-----------------------------------|----------------------|----------------------------------------|:---------------:|:------:|
| <characteristic> | <concern> | <ATTR>QA-<n> — <one line> (<measure>) | (H, M) | open |

_Reading the tree_: a QA / refinement with no leaf → look for an unrecorded ASR; the `★`
leaves get the most attention; note which leaves are `addressed` vs `open`.

## Next steps — hand-off to the drivers register

| Workshop ID | Becomes | Notes |
|-------------|---------|-------|
| CS-<id> | <ATTR>QA-<n> | refined here; six-part detail copied to the register |
| CS-<id> | <ATTR>QA-<n> | consolidated but not refined — refine in `/drivers` Step 5 |
| AD-<n> | BG-<n> / UC-<n> / CON-<n> / <ATTR>QA-<n> | every workshop driver maps to a register ID |

- Run `/drivers` to create or update `architecture/drivers/` from this table.
- Schedule an ATAM once an architecture exists.
