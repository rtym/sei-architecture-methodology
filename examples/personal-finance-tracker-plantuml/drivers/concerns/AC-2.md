# AC-2: Dashboard iteration speed must stay high

- **Concern**: New report types ship weekly; any design that makes a report type a schema or deployment event will slow the product loop.
- **Kind**: general (delivery process)
- **Raised by**: ST-1, ST-2
- **Priority**: medium
- **Status**: addressed

## Why it matters

Growth (BG-1) depends on reacting to user feedback with new views of the same data; the
modifiability scenario MQA-1 puts a number on it (≤ 1 person-day, 0 regressions), and the
report-type registry in the reporting module (ADR-1) is the answer.

## Related drivers

`BG-1`, `BG-3`, `MQA-1`, `UC-2`

<!-- changed 2026-09-06: recorded from the ADD session's architectural-concerns table -->
