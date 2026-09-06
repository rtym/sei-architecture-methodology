# CON-1: Mobile web only at launch

- **Type**: technical
- **Constraint**: The system must run in mobile browsers (iOS Safari, Android Chrome); no native app at launch.
- **Source**: Product
- **Nature**: hard
- **Priority**: high
- **Status**: open

## Rationale

{1:"Fastest path to users on every device without app-store review (BG-1).",
  2:"Funding reality; sets the complexity budget for the whole architecture.",
  3:"Preserves runway (BG-4); the architecture must have a clear scale-up path.",
  4:"Required by the SOC 2 audit scope (BG-2); non-negotiable.",
  5:"Team knows PostgreSQL; managed primary/standby meets the availability need cheaply."}[1]

## Impact on the architecture

{1:"Rules out native modules; shapes the Web App container as a PWA.",
  2:"Rules out microservices / self-managed HA; favours a modular monolith.",
  3:"Favours managed data services; the design must not lock into a free tier.",
  4:"Adds a tenant-guard + encrypted stores; part of every data-path decision.",
  5:"Fixes the datastore; the persistence module isolates the query builder."}[1]

## Conflicts

None.

## Traces up to

- Business goals: `BG-1`
