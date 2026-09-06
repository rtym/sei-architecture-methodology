# Reference — Best-practices quality gate

Every skill runs this checklist against its own output **before declaring the activity done**, and
runs `python tests/validate.py <artifact>` (the automated subset). Report each item as
`ok` / `fix: …`. Fix, re-check, repeat.

---

## All artifacts

- [ ] Written under `architecture/<activity>/`; Markdown is the source of truth and is current.
- [ ] Every ID follows the scheme: `BG-`, `UC-`, `CON-`, `<ATTR>QA-` (never flat `QAS-`).
- [ ] IDs are sequential within their prefix and never reused or renumbered.
- [ ] Every claim, decision, risk, or analysis row cites ≥ 1 driver ID.
- [ ] Every diagram: rendered to PNG, opened with `Read`, and visually verified — correctness
      and minimal edge crossings — before being embedded.
- [ ] No TODO / `<placeholder>` / empty table left in a "finished" artifact.

## "Good architecture" rules of thumb (apply to any design or review — see `architecture-fundamentals.md`)

- [ ] Produced by one architect / a small team with a technical lead, connected to the dev team.
- [ ] Built on a **prioritised list of well-specified quality-attribute scenarios**.
- [ ] Documented with **views** chosen for the most important stakeholders' concerns.
- [ ] **Evaluated early** for its ability to deliver the important quality attributes.
- [ ] Lends itself to **incremental implementation** (a skeletal system grown by increments).
- [ ] Well-defined **modules** using information hiding + separation of concerns; each with an
      interface that hides the changeable parts.
- [ ] Quality attributes achieved with **known patterns and tactics** per attribute.
- [ ] **No dependency on a specific version** of a commercial product/tool (or it is isolated).
- [ ] **Data producers separated from data consumers.**
- [ ] A **small number of simple, uniform component-interaction patterns.**
- [ ] A **small, explicit set of resource-contention areas**, each with a stated resolution /
      enforced budget.

## Architectural drivers (`architecture/drivers/` directory)

- [ ] It is a **directory**: `README.md` + `business-goals/`, `use-cases/`, `constraints/`,
      `quality-attributes/` with **one file per driver**. The top `README.md` is the aggregate
      file; each subdirectory has its own small `README.md` index. Every cross-reference is a
      working **relative Markdown link**; each `README.md` ends with a Navigation footer.
- [ ] All four kinds present. Every driver file carries `**Status**`.
- [ ] Each business goal is `<stakeholder> needs <outcome> so that <business value>` with a category.
- [ ] Each use case has a primary actor, a trigger, and a numbered main success scenario — not a
      one-liner; the architecturally significant alternate flows are listed.
- [ ] **Each use case has its own proper UML use case diagram** — stick-figure actors outside the
      boundary rectangle, ellipse use cases inside, dashed `<<include>>`/`<<extend>>` — rendered
      (PlantUML preferred) and visually cross-verified, embedded as `![](diagrams/UC-<n>.png)`.
      Plus one overview diagram per actor group.
- [ ] Each constraint has a type (business / technical / regulatory), a source, and hard/negotiable.
- [ ] **Each quality attribute is documented as a six-part quality attribute scenario** with a
      **numeric** response measure and an ISO/IEC 25010 classification (characteristic + sub),
      **and its own horizontal (`flowchart LR`) six-part scenario diagram**, verified and embedded.
- [ ] `quality-attributes/utility-tree.md` exists — the summary of the QA drivers as a
      **table** (columns: Quality attribute · Refinement · Leaf scenario · Priority (V, R) ·
      Status), one leaf per row, `★` on each `(H, H)` leaf, plus a "Reading the tree" note.
      No diagram. Imported from the QAW (its Step 9) when one was run.
- [ ] `README.md` traceability matrix present; **no orphans** — every BG supported by ≥ 1 UC/QA
      scenario, every UC/QA scenario/CON traces up to ≥ 1 BG. Gaps reported explicitly.
- [ ] `README.md` prioritised list leads with the `(H,H)` then `(H,M)` quality scenarios; has a change log.

## Quality attribute scenarios (`scenarios.md`)

- [ ] 8–15 scenarios (more than ~20 → the net is too wide; fewer than ~5 → probably incomplete).
- [ ] Every scenario: six parts + numeric measure + ISO/IEC 25010 class + priority pair `(Imp,Diff)`.
- [ ] Generic sources ("the user", "the system") replaced with specific roles/systems.
- [ ] Every scenario visualised as a six-part UML scenario diagram (verified).
- [ ] Every scenario cites ≥ 1 business goal.

## Quality Attribute Workshop (`qaw-report.md`)

- [ ] All eight steps present as sections, plus Step 9 (utility tree).
- [ ] Participant list with roles.
- [ ] Raw brainstormed scenarios kept **verbatim**; consolidation has a merge map; dissent recorded.
- [ ] Vote budget stated explicitly as `ceil(0.30 × consolidated count)`.
- [ ] Refined top scenarios have the six-part form + numeric measure + questions + issues.
- [ ] Step 9 utility tree is a **table** (one leaf per row, `(V, R)` pair, `★` on (H,H)), not a diagram.

## ADD 3.0 (`<slug>-session.md` + `<slug>-Architecture.md`)

- [ ] Design purpose classified (greenfield / brownfield variant).
- [ ] Iteration plan covers **every** driver ID from Step 1 in ≥ 1 iteration row.
- [ ] Each iteration: goal is one sentence; selected drivers favour high-importance × high-difficulty.
- [ ] Each design concept evaluated against ≥ 1 alternative; rationale cites driver IDs.
- [ ] Every instantiated element has a single clear responsibility and defined interfaces.
- [ ] Architecture.md has all 9 sections; each diagram obeys the ten rules and is verified.
- [ ] Every sequence diagram is followed by a plain-English description paragraph.
- [ ] Every §9 design decision rationale cites ≥ 1 driver ID.
- [ ] Step 7 analysis marks each driver yes / partially / no with notes; no driver silently dropped.

## ATAM (`atam-report.md`)

- [ ] Business drivers, architecture presentation, and architectural approaches (`AA-n`) recorded.
- [ ] Utility tree present **as a table**; each leaf row carries a `(V, R)` pair (business
      value, technical risk); the `★` (H,H)/(H,M) leaves are analysed.
- [ ] Every analysed scenario names the approaches invoked and the analysis questions asked.
- [ ] Risks, non-risks, sensitivity points, tradeoff points each populated (or explicitly "none found").
- [ ] Every **non-risk** records the assumption under which it holds.
- [ ] Every **tradeoff point** names ≥ 2 quality attributes in tension.
- [ ] Risk themes cluster the risks and each maps to ≥ 1 business goal.
- [ ] Recommendations are actionable (targeted ADD iterations / spikes / monitoring), not vague.

## Views and Beyond (`docs/`)

- [ ] All three viewtypes covered: Module, Component-and-Connector, Allocation (extra views allowed).
- [ ] Standard V&B document layout: roadmap (`README.md`), system overview, view packets,
      mapping between views, rationale, directory.
- [ ] Every view packet has all five sections (primary presentation, element catalog, context
      diagram, variability guide, rationale). "Variability guide" may say "None." but must exist.
- [ ] `mapping-between-views.md` actually cross-references the views produced — no placeholders.
- [ ] The seven rules for sound documentation are respected (reader's POV, no needless repetition,
      no ambiguity, standard organisation, rationale recorded, current, reviewed for fitness).
- [ ] Every rationale cites ≥ 1 driver ID.

## Reports (`build-report.sh` output)

- [ ] Format matches what the user asked for (Markdown / HTML / both).
- [ ] HTML is self-contained (no external requests); cover page + table of contents present.
- [ ] `--embed-diagrams` used when diagrams should travel with the report; embedded PNGs are the
      verified ones.
