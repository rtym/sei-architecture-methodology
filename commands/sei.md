---
description: Entry point for the SEI architecture methodology — routes you to architectural drivers, quality attributes, QAW, ADD, ATAM, Views-and-Beyond documentation, or diagrams.
argument-hint: "[drivers | quality-attributes | qaw | add | atam | docs | diagram | brownfield]"
---

# /sei — SEI architecture methodology

Read `${CLAUDE_PLUGIN_ROOT}/skills/sei-architecture/SKILL.md` and follow it. Route the user to the right activity
(architectural drivers, quality attributes, QAW, ADD, ATAM, Views-and-Beyond documentation, or
diagrams), then follow that skill's `SKILL.md` exactly.

Arguments: `$ARGUMENTS`. If an activity name is given, skip the routing question and go straight to
that skill's `SKILL.md`; `brownfield` runs the brownfield intake (read the repository and pre-draft
the drivers and as-built views) before activity 0; otherwise route as the skill describes.
