# Paste-in `classDef` lines

`render.sh` styles the semantic classes through the theme file, but the theme is **not** loaded
when a diagram is pasted into a chat message or an Artifact. So also put the relevant `classDef`
lines inside the diagram. They are harmless when the theme is loaded and essential when it is not.

## Flowchart / quality-attribute-scenario

```
classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
classDef artifact  fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
classDef response  fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
classDef internal  fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
classDef external  fill:#F5EEE3,stroke:#B07D3B,color:#1F2933;
classDef datastore fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
classDef emphasis  fill:#F6E4E4,stroke:#B04A46,color:#1F2933;
```

Apply with `class node1,node2 internal` (or the `:::internal` shorthand on a node).

## C4 diagrams

C4 element colours come from the theme file's `themeVariables` (person / system / container /
component / datastore / boundary). To emphasise one element in a C4 diagram without the theme, use
`UpdateElementStyle(alias, $bgColor="#F6E4E4", $borderColor="#B04A46")`.
