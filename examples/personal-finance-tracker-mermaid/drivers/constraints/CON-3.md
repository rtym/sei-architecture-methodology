# CON-3: Low-cost managed cloud tiers

- **Type**: business
- **Constraint**: Launch on managed cloud low/free tiers; a paid upgrade path must exist.
- **Source**: Founder
- **Nature**: negotiable
- **Priority**: medium
- **Status**: open

## Rationale

Preserves runway ([BG-4](../business-goals/BG-4.md)); the architecture must have a clear
scale-up path off the low-cost tiers.

## Impact on the architecture

Favours managed data services; the design must not lock into a free tier and must keep a paid
upgrade path for PostgreSQL and Redis. Interacts with [AQA-1](../quality-attributes/AQA-1.md) —
the recovery target has to be met on a low-cost managed tier.

## Conflicts

None.

## Traces up to

- Business goals: [BG-4](../business-goals/BG-4.md)

---

**Navigation**: [constraints index](README.md) · [drivers README](../README.md)
