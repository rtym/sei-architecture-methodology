---
description: Facilitate a SEI Attribute-Driven Design (ADD 3.0) session — iterative, driver-focused decomposition producing an architecture, C4/UML views, and an ADR log.
argument-hint: "[new <slug> | continue [<slug>] | report]"
---

# /add — Attribute-Driven Design (ADD 3.0)

Read `${CLAUDE_PLUGIN_ROOT}/skills/attribute-driven-design/SKILL.md` and follow it exactly. Facilitate a SEI ADD 3.0
design session, writing `architecture/add/<slug>-session.md` and `<slug>-Architecture.md`.

Arguments: `$ARGUMENTS`. If present, skip the opening question: `new <slug>` starts a fresh session
with that slug; `continue [<slug>]` resumes the matching `architecture/add/*-session.md` (list them if
nothing matches); `report` prints the session file path. If empty, ask as the skill describes.
