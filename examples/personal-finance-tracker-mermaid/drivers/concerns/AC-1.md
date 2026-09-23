# AC-1: Keep the SOC 2 surface small

- **Concern**: Every external dependency and every place data is copied widens the SOC 2 audit scope; the design should need as few of both as possible.
- **Kind**: general (compliance posture of a one-person team)
- **Raised by**: ST-1, ST-4
- **Priority**: high
- **Status**: in design

## Why it matters

The founder's route to enterprise customers runs through SOC 2 (BG-2). Each managed service and
each data copy is a control to evidence; with one engineer (CON-2) the audit workload must stay
small or the certification slips.

## Related drivers

`BG-2`, `SQA-1`, `CON-2`, `CON-4`

<!-- changed 2026-09-06: recorded from the ADD session's architectural-concerns table -->
