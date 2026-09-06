# CON-5: PostgreSQL primary datastore

- **Type**: technical
- **Constraint**: The primary datastore must be PostgreSQL (team skill, managed availability options).
- **Source**: Eng lead
- **Nature**: negotiable
- **Priority**: medium
- **Status**: open

## Rationale

{1:"Fastest path to users on every device without app-store review (BG-1).",
  2:"Funding reality; sets the complexity budget for the whole architecture.",
  3:"Preserves runway (BG-4); the architecture must have a clear scale-up path.",
  4:"Required by the SOC 2 audit scope (BG-2); non-negotiable.",
  5:"Team knows PostgreSQL; managed primary/standby meets the availability need cheaply."}[5]

## Impact on the architecture

{1:"Rules out native modules; shapes the Web App container as a PWA.",
  2:"Rules out microservices / self-managed HA; favours a modular monolith.",
  3:"Favours managed data services; the design must not lock into a free tier.",
  4:"Adds a tenant-guard + encrypted stores; part of every data-path decision.",
  5:"Fixes the datastore; the persistence module isolates the query builder."}[5]

## Conflicts

None.

## Traces up to

- Business goals: `BG-1`
