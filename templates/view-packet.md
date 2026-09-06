# View: <name>  (<Module | Component-and-Connector | Allocation> / <style>)

- **Viewtype**: <Module | C&C | Allocation>
- **Style**: <decomposition | uses | layered | generalization | data model | client-server | pub-sub | pipe-and-filter | shared-data | service-oriented | deployment | install | implementation | work-assignment>
- **Stakeholders / concerns addressed**: <list>
- **Date**: <YYYY-MM-DD>

## 1. Primary presentation

<The main diagram — via the `sei-diagrams` skill: a ```mermaid block, then the image line below.
≤ ~10 elements; split into sub-views if larger. Include or reference a legend.>

![View: <name>](diagrams/view-<name>.png)

_visually verified: yes/no · relative path renders on GitHub / GitLab_

## 2. Element catalog

### 2.1 Elements and their properties

| Element | Responsibility / role | Key properties |
|---------|-----------------------|----------------|

### 2.2 Relations and their properties

| From | Relation | To | Properties |
|------|----------|----|-----------|

### 2.3 Element interfaces

<For significant elements: provided / required interfaces, operations, data types, error handling.
Reference the ADD `Architecture.md` §8 if it exists rather than duplicating.>

### 2.4 Element behavior

<Sequence / state diagrams for behavior not evident from structure — via `sei-diagrams`.>

## 3. Context diagram

<This view's scope boundary and what sits outside it.>

## 4. Variability guide

<Built-in points of variation: configuration, plug-in points, feature flags, product-line options,
and how to exercise each. If there is genuinely none, write "None." — do not omit the section.>

## 5. Rationale

<Why this structure; alternatives considered and rejected; how it serves the drivers — cite
`<ATTR>QA-`, `UC-`, `CON-` IDs. Link related ADRs.>
