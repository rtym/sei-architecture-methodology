# Quality Attribute Scenario: <ATTR>QA-<n>

| Part | Value |
|------|-------|
| **ID** | <ATTR>QA-<n> |
| **ISO/IEC 25010 characteristic** | <e.g. Reliability> |
| **Sub-characteristic** | <e.g. availability> |
| **Source of stimulus** | <who/what> |
| **Stimulus** | <the event/condition> |
| **Artifact** | <the part stimulated> |
| **Environment** | <system state: normal / peak / degraded / deployment> |
| **Response** | <what the system must do> |
| **Response measure** | <numeric, with a percentile/threshold/time bound> |
| **Business goals supported** | BG-<…> |
| **Priority** | Importance = H/M/L · Difficulty = H/M/L |
| **Type** | general | concrete |

## Six-part scenario diagram

```mermaid
flowchart LR
  %% <ATTR>QA-<n> — <ISO 25010 characteristic / sub>
  src["<b>Source of stimulus</b><br/><source>"]
  stim["<b>Stimulus</b><br/><stimulus>"]
  subgraph env["Environment: <environment>"]
    art["<b>Artifact</b><br/><artifact>"]
  end
  resp["<b>Response</b><br/><response>"]
  meas["<b>Response measure</b><br/><measure>"]
  src -->|generates| stim --> art
  art --> resp -->|measured by| meas
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact  fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef response  fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class src,stim source
  class art artifact
  class resp,meas response
```

![<ATTR>QA-<n> six-part scenario](diagrams/scenario-<ATTR>QA-<n>.png)

Rendered from the block above · visually verified: yes/no · relative path renders on GitHub / GitLab

## Notes / assumptions

<open questions, tactics likely needed, links to related scenarios>
