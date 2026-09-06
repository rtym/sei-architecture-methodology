# BG-2: Sell to employers via SOC 2

- **Statement**: The company needs to pass a SOC 2 Type II audit so that it can sell the app to employers as a staff benefit.
- **Primary stakeholder**: Founder / Compliance
- **SEI business-goal category**: responsibility to society & law
- **Measure of success**: Clean SOC 2 Type II report before the enterprise sales push
- **Priority**: high
- **Status**: open

## Context

Early-stage SaaS; this goal is one of the four the architecture must serve. See
`../index.md` for the full driver set and traceability.

## Supported by

- Use cases: —
- Quality attribute scenarios: {1:"PQA-1, PQA-2, AQA-1, UQA-1", 2:"SQA-1", 3:"MQA-1", 4:"AQA-1"}[2]

## Notes

{1:"Growth pressure drives the performance and availability scenarios.",
  2:"Audit scope drives the security scenario and the encryption constraint.",
  3:"Velocity is in tension with CON-2 (one engineer) — that tension is itself a driver.",
  4:"Budget rules out self-managed HA; see CON-3."}[2]
