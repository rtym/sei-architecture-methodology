---
description: Collect and track the four SEI architectural driver kinds — business goals, use cases, constraints, and six-part quality attribute scenarios — as a traceable architecture/drivers/ register.
argument-hint: "[<path to brief / PRD / requirements …>]"
---

# /drivers — Architectural drivers register

Read `${CLAUDE_PLUGIN_ROOT}/skills/architectural-drivers/SKILL.md` and follow its instructions exactly. Collect and
track the four driver kinds — business goals, primary functional requirements (as proper UML
**use cases**, each with its own use case diagram), constraints, and quality attribute scenarios
(six-part, each with its own horizontal scenario diagram) — as a **directory**,
`architecture/drivers/`, with one file per driver under `business-goals/`, `use-cases/`,
`constraints/`, `quality-attributes/`; a top `README.md` (traceability matrix + coverage check +
prioritised list + change log); a small `README.md` index in each subdirectory; and a
`quality-attributes/utility-tree.md` — the **tabular** utility tree summarising the quality
attributes. Every cross-reference is a working relative Markdown link.

Arguments: `$ARGUMENTS`. Any paths given are the Step-1 source material — read them before drafting
instead of asking what exists.
