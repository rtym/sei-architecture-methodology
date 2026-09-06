# BG-3: Keep feature pace with competitors

- **Statement**: Engineering needs to ship new report types weekly so that the product keeps pace with competitor feature velocity.
- **Primary stakeholder**: Eng lead
- **SEI business-goal category**: process quality
- **Measure of success**: ≥ 1 new report type released per week, sustained
- **Priority**: high
- **Status**: open

## Context

Early-stage SaaS; this goal is one of the four the architecture must serve. See
`../index.md` for the full driver set and traceability.

## Supported by

- Use cases: UC-1
- Quality attribute scenarios: {1:"PQA-1, PQA-2, AQA-1, UQA-1", 2:"SQA-1", 3:"MQA-1", 4:"AQA-1"}[3]

## Notes

{1:"Growth pressure drives the performance and availability scenarios.",
  2:"Audit scope drives the security scenario and the encryption constraint.",
  3:"Velocity is in tension with CON-2 (one engineer) — that tension is itself a driver.",
  4:"Budget rules out self-managed HA; see CON-3."}[3]
