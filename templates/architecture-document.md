# Architecture: <name>

- **System**: <one line>
- **Date**: <YYYY-MM-DD>
- **Session**: `<slug>-session.md`
- **Drivers**: [`../drivers/README.md`](../drivers/README.md)

> Companion document produced by `/attribute-driven-design`. For a full Views-and-Beyond
> description, run `/architecture-docs`; this document is the ADD working architecture.

<!-- Mermaid: every diagram appears as BOTH a ```mermaid block AND, immediately after it,
     a ![title](diagrams/<name>.png) line pointing at the verified render in ./diagrams/ .
     PlantUML: the ![title](diagrams/<name>.png) line + a Source: link to diagrams/<name>.puml
     (no inlined ```plantuml block — GitHub does not render it).
     The relative, forward-slash, no-leading-slash path renders on GitHub and GitLab. -->

_Example of the diagram + image pattern used throughout this document:_

```mermaid
flowchart LR
  %% example
  a["A"] --> b["B"]
```

![example](diagrams/example.png)

## 1. Introduction
<Purpose, scope, high-level description.>

## 2. Context diagram
### Diagram
```mermaid
flowchart TB
  %% Context — <name> (C4 level 1)
  user(["User role<br/><i>how they access</i>"])
  subgraph sys["<name>"]
    core["<name><br/><i>the system under design</i>"]
  end
  user -->|"Submits requests (HTTPS)"| core
  classDef source  fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  class user source
  class core internal
```
### Description
<Plain-English explanation.>

## 3. Architectural drivers
### Quality Attribute Scenarios (key)
| ID | QA (ISO 25010) | Stimulus | Response | Measure | Priority |
|----|----------------|----------|----------|---------|----------|
### Primary functional requirements — use cases (key)
| ID | Name | Priority |
|----|------|----------|
### Constraints (key)
| ID | Type | Description |
|----|------|-------------|

## 4. Container diagram
### Diagram
```mermaid
flowchart TB
  %% Container diagram — <name> (C4 level 2)
  user(["User role<br/><i>mobile browser</i>"])
  subgraph sys["<name>"]
    direction TB
    web["Web App<br/><i>tech stack</i>"]
    api["API Service<br/><i>tech stack</i>"]
    db[("Database<br/><i>PostgreSQL 15</i>")]
  end
  user -->|"Uses over HTTPS"| web
  web -->|"Calls REST API (JSON)"| api
  api -->|"Reads / writes (SQL/TLS)"| db
  classDef source  fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef datastore fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class user source
  class web,api internal
  class db datastore
```
### Description
<Plain-English explanation.>

## 5. Component diagrams
### <Container name>
#### Diagram
```mermaid
flowchart TB
  %% Component diagram — <container name> (C4 level 3)
  caller(["Calling container<br/><i>tech stack</i>"])
  subgraph c["<container name>"]
    direction TB
    ctrl["Request Controller<br/><i>tech</i>"]
    svc["Domain Service<br/><i>tech</i>"]
    repo[("Repository<br/><i>tech</i>")]
  end
  caller -->|"HTTP request (REST)"| ctrl
  ctrl -->|"Delegates commands"| svc
  svc -->|"Queries / persists"| repo
  classDef source  fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef datastore fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class caller source
  class ctrl,svc internal
  class repo datastore
```
#### Description
<Plain-English explanation.>

## 6. Sequence diagrams
<One per key scenario. Each followed immediately by a plain-English description paragraph.>

## 7. Deployment diagram
### Diagram
```mermaid
flowchart TB
  %% Deployment — <name> (production topology)
  subgraph region["Cloud region"]
    subgraph cluster["Container platform"]
      api["API Service<br/><i>N replicas, multi-AZ</i>"]
    end
    subgraph data["Managed data tier"]
      db[("PostgreSQL 15<br/><i>primary + standby</i>")]
    end
  end
  api -->|"SQL / TLS"| db
  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef datastore fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class api internal
  class db datastore
```
### Description
<Plain-English explanation.>

## 8. Interfaces and events
### Interfaces
| Component | Interface | Protocol | Description |
|-----------|-----------|----------|-------------|
### Events
| Event | Publisher | Consumers | Description |
|-------|-----------|-----------|-------------|

## 9. Design decisions
| Decision | Rationale (cite driver IDs) | Alternatives discarded |
|----------|-----------------------------|------------------------|
