---
description: Draw clean, low-crossing UML / C4 diagrams in Mermaid or PlantUML and render them to high-resolution PNG with the SEI palette.
argument-hint: "[context | container | component | deployment | sequence | class | state | use-case | scenario] [mermaid | plantuml] [<what to draw>]"
---

# /sei-diagram — Clean UML / C4 diagrams rendered to PNG

Read `${CLAUDE_PLUGIN_ROOT}/skills/sei-diagrams/SKILL.md` and follow it exactly. Draw the requested diagram (context,
container, component, sequence, deployment, class, state, use case, or quality-attribute
scenario) in Mermaid or PlantUML, show the source, render it to PNG with the SEI palette, then
`Read` the PNG and visually cross-verify it for correctness and minimal edge crossings before
presenting it. (The quality-attribute utility tree is a table, not a diagram.)

Arguments: `$ARGUMENTS`. A diagram type and/or notation given here are taken as decided — do not ask
again; anything else is the subject to draw.
