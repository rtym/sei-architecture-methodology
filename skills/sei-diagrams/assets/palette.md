# SEI diagrams — palette

One calm, print-friendly, colour-blind-safe palette. Colour is **semantic**: it tells the reader
what kind of thing an element is, never decorates. Every fill/stroke pair below meets WCAG AA for
text on the fill.

| Role | Fill | Stroke | Use for |
|------|------|--------|---------|
| **Internal** | `#EDF2F8` | `#3E6DA5` | System-owned containers, components, modules |
| **External** | `#F5EEE3` | `#B07D3B` | External systems, third-party services, actors outside the boundary |
| **Person / actor** | `#E7E3F3` | `#6B5BA6` | Users and roles |
| **Datastore** | `#E4F0E9` | `#3F7D5C` | Databases, caches, queues, blob stores |
| **Emphasis** | `#F6E4E4` | `#B04A46` | The element under discussion, a risk, a hotspot |
| **Boundary** | `none` | `#9AA7B4` (dashed) | System / context / subsystem boundaries |
| Ink (text) | — | `#1F2933` | All label text |
| Line (edges) | — | `#6B7A8D` | Relationships / message arrows |
| Note | `#FBF6EC` | `#B07D3B` | Sequence-diagram notes |

## Quality-attribute-scenario roles

| Part | class name | Fill | Stroke |
|------|-----------|------|--------|
| Source of stimulus, Stimulus | `source` | `#E7E3F3` | `#6B5BA6` |
| Artifact (inside Environment) | `artifact` | `#EDF2F8` | `#3E6DA5` |
| Response, Response measure | `response` | `#E4F0E9` | `#3F7D5C` |

## Using the palette

- **Mermaid, rendered via `render.sh`**: `assets/mermaid-theme.json` sets all of the above through
  `themeVariables` and `themeCSS`. You still add `class <node> <role>` in flowcharts and the
  `classDef` lines from `assets/classdefs.md` so the diagram is also correct when pasted into chat
  or an Artifact (which don't load the theme file).
- **PlantUML**: `!include assets/plantuml-theme.puml` at the top of the `.puml`.

## Font

`Inter, "Helvetica Neue", Arial, sans-serif` at 15 px. Inter is not bundled; the fallback stack
renders cleanly everywhere.
