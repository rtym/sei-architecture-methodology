# CON-1: Mobile web only at launch

- **Type**: technical
- **Constraint**: The system must run in mobile browsers (iOS Safari, Android Chrome); no native app at launch.
- **Source**: Product
- **Nature**: hard
- **Priority**: high
- **Status**: open

## Rationale

Fastest path to users on every device without app-store review, in support of
[BG-1](../business-goals/BG-1.md).

## Impact on the architecture

Rules out native modules; shapes the Web App container as a Progressive Web App served from a CDN.

## Conflicts

None.

## Traces up to

- Business goals: [BG-1](../business-goals/BG-1.md)

---

**Navigation**: [constraints index](README.md) · [drivers README](../README.md)
