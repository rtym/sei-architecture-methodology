# references/ — deep method notes

Each skill points at the relevant file(s) here when a step needs more depth than the `SKILL.md`
carries. Nothing here is executable; it is the encoded SEI body of knowledge.

## Foundations

| File | Covers |
|------|--------|
| [`architecture-fundamentals.md`](architecture-fundamentals.md) | what an architecture is (module / C&C / allocation structures, views); why it matters; the process + structural "good architecture" rules of thumb |
| [`glossary.md`](glossary.md) | every term used across the skills and references, with the file that treats it in depth |
| [`best-practices-checklist.md`](best-practices-checklist.md) | the quality gate every skill runs against its own output |

## Drivers and quality attributes

| File | Covers |
|------|--------|
| [`architectural-drivers.md`](architectural-drivers.md) | the four driver kinds; ASR criteria and sources; 7-part PALM business-goal scenario; the tabular utility tree |
| [`quality-attribute-taxonomy.md`](quality-attribute-taxonomy.md) | ISO/IEC 25010; the six-part scenario; general-scenario "portions" summary; tactics-based-questionnaire framing |
| [`quality-attribute-scenarios.md`](quality-attribute-scenarios.md) | the full general-scenario portion table for all 10 attributes + a worked concrete example each |
| [`qaw-method.md`](qaw-method.md) | the SEI 8-step Quality Attribute Workshop |
| [`tactics-catalog.md`](tactics-catalog.md) | per-attribute tactic lists + questionnaire cues (ADD Step 4, ATAM Step 6) |

## Design

| File | Covers |
|------|--------|
| [`add-method.md`](add-method.md) | ADD 3.0 — the 7 steps; the design roadmap by system type; identify/select design concepts; the design backlog |
| [`design-concepts.md`](design-concepts.md) | the 5 design-concept categories; per-QA starting points; select via pros/cons + SWOT / CBAM |
| [`architecture-patterns.md`](architecture-patterns.md) | patterns grouped by the QA they serve, each with its principal tradeoff; reference architectures |
| [`interfaces.md`](interfaces.md) | interface concepts, the four agreement points, design principles, documenting (ADD Step 5, V&B §2.3) |

## Evaluation

| File | Covers |
|------|--------|
| [`atam-method.md`](atam-method.md) | ATAM — 9 steps, 2 phases; utility tree vs. brainstorming; attribute characterization; Lightweight Architecture Evaluation; CBAM |
| [`design-reviews.md`](design-reviews.md) | tactics-based analysis, reflective questions, scenario-based design review — the lightweight in-iteration checks |

## Documentation and lifecycle

| File | Covers |
|------|--------|
| [`views-and-beyond.md`](views-and-beyond.md) | V&B — the three viewtypes, the view packet, beyond-views docs, notation choice, combining views, documenting behaviour, the seven rules |
| [`architecture-in-the-lifecycle.md`](architecture-in-the-lifecycle.md) | architecture debt & hotspots (DSM, anti-patterns, quantification); how much design up front (Agile, Iteration 0); distributed development; the architect's role and competence |
| [`runtime-environments.md`](runtime-environments.md) | virtualization (VM / container / pod / serverless), the cloud (failure, multiple instances, state, cost), and mobile — and how each shapes the deployment view and QA scenarios |
