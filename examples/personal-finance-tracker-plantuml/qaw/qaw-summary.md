# QAW summary — Personal Finance Tracker

- **Workshop date**: 2026-08-20
- **Format**: half-day
- **Report status**: complete
- **Entry mode**: partial
- **Full report**: [qaw-report.md](qaw-report.md)

5 participants produced 8 raw scenarios, consolidated to 6; 2 were refined into measurable six-part scenarios. 2 carry the highest business value and technical risk, and 3 questions remain open.

## Priorities

Vote ranking: CS-1 (3) = CS-5 (3) > CS-2 (2) > CS-3 (1) = CS-4 (1) > CS-6 (0).

Highest value and risk — (H, H) in the utility tree:

- SQA-1 (CS-1) — cross-user access rejected and logged; 0 reads; alert < 1 min
- AQA-1 (CS-3) — survive an AZ loss, recover < 60 s; ≥ 99.5 %/mo

## Refined scenarios

- CS-1 — Cross-user access attempt is rejected and logged
- CS-5 — First-time user succeeds without help

## Open questions

| ID | Question | Owner | Due |
|----|----------|-------|-----|
| PQ-1 | How long must the audit log be kept for the SOC 2 Type II audit? | ST-4 | 2026-09-03 |
| PQ-2 | Which browsers and screen readers must first use support at launch? | ST-5 | 2026-09-03 |
| PQ-3 | What monthly infrastructure budget does BG-4 allow at 10 000 users? | ST-1 | 2026-09-17 |

## Next step

12 workshop IDs are mapped to register IDs in the report's hand-off table. Run `/drivers` to carry them into the drivers register, then `/add` to design against them.
