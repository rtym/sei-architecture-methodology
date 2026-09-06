# BG-4: Preserve runway at launch scale

- **Statement**: Operations needs the monthly infrastructure bill to stay under budget at launch scale so that runway is preserved.
- **Primary stakeholder**: Founder
- **SEI business-goal category**: financial
- **Measure of success**: Infra spend ≤ budget at 10 000 users
- **Priority**: high
- **Status**: open

## Context

Early-stage SaaS; this goal is one of the four the architecture must serve. See
`../index.md` for the full driver set and traceability.

## Supported by

- Use cases: —
- Quality attribute scenarios: {1:"PQA-1, PQA-2, AQA-1, UQA-1", 2:"SQA-1", 3:"MQA-1", 4:"AQA-1"}[4]

## Notes

{1:"Growth pressure drives the performance and availability scenarios.",
  2:"Audit scope drives the security scenario and the encryption constraint.",
  3:"Velocity is in tension with CON-2 (one engineer) — that tension is itself a driver.",
  4:"Budget rules out self-managed HA; see CON-3."}[4]
