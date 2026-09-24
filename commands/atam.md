---
description: Run the SEI nine-step Architecture Tradeoff Analysis Method evaluation — utility tree, scenario analysis, risks, sensitivity points, tradeoff points, and risk themes.
argument-hint: "[full | lightweight] [<path to the architecture description>]"
---

# /atam — Architecture Tradeoff Analysis Method

Read `${CLAUDE_PLUGIN_ROOT}/skills/atam/SKILL.md` and follow it exactly. Run the SEI nine-step ATAM evaluation and
record approaches, utility tree, scenario analysis, risks, non-risks, sensitivity points, tradeoff
points and risk themes in `architecture/atam/atam-report.md`.

Arguments: `$ARGUMENTS`. `lightweight` selects the Lightweight Architecture Evaluation mode and `full`
the default full ATAM — either skips the mode question; a path is the architecture package to evaluate.
