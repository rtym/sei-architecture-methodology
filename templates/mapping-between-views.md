# Mapping between views — <SystemName>

<One sentence: how elements correspond across the Module, C&C and Allocation views, so a reader can
move between them and internal consistency is demonstrable.>

## Module → runtime component (C&C)

| Module (`view-<module view>.md`) | Runtime component (`view-<C&C view>.md`) | Notes |
|----------------------------------|------------------------------------------|-------|
| `<module>` | <component> | <1:1 / grouped / shared library> |

## Runtime component (C&C) → deployment node (Allocation)

| Runtime component | Deployment node (`view-<allocation view>.md`) | Notes |
|-------------------|-----------------------------------------------|-------|
| <component> | <node> | <replicas, statefulness> |

## Driver → element realising it

| Driver | Realised by |
|--------|-------------|
| `<ATTR>QA-<n>` | <module → component → node> |

---

**Navigation**: [docs README](README.md) · [architecture package](../README.md)
