# CON-5: PostgreSQL primary datastore

- **Type**: technical
- **Constraint**: The primary datastore must be PostgreSQL (team skill, managed availability options).
- **Source**: Eng lead
- **Nature**: negotiable
- **Priority**: medium
- **Status**: open

## Rationale

The team knows PostgreSQL, and its managed primary/standby offering meets the availability need
([AQA-1](../quality-attributes/AQA-1.md)) cheaply — consistent with
[BG-4](../business-goals/BG-4.md).

## Impact on the architecture

Fixes the datastore; the `persistence` module isolates the query builder so a later dialect
change stays contained.

## Conflicts

None.

## Traces up to

- Business goals: [BG-1](../business-goals/BG-1.md)

---

**Navigation**: [constraints index](README.md) · [drivers README](../README.md)
