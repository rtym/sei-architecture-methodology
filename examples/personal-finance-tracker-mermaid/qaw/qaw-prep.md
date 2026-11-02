# QAW preparation — Personal Finance Tracker

- **Generated**: 2026-11-02
- **Suggested entry mode**: refresh
- **Drivers register**: [drivers register](../drivers/README.md)

This sheet prepares the facilitator for the next Quality Attribute Workshop on Personal Finance Tracker. It lists 15 answers the documentation already gives, to confirm rather than ask again, then the quality characteristics no scenario covers yet, and the questions for each participant's role. Start with the first table in Steps 2–4.

## Documented answers to confirm

Each row is already answered in the drivers register. Read it out with its source and ask only whether it still holds; a changed answer is recorded in the report with both versions.

| ID | What the documentation says | Source | Ask |
|----|-----------------------------|--------|-----|
| BG-1 | 10 000 monthly-active users by month 12 | [BG-1](../drivers/business-goals/BG-1.md) | Is this still the target, and still a goal? |
| BG-2 | Clean SOC 2 Type II report before the enterprise sales push | [BG-2](../drivers/business-goals/BG-2.md) | Is this still the target, and still a goal? |
| BG-3 | ≥ 1 new report type released per week, sustained | [BG-3](../drivers/business-goals/BG-3.md) | Is this still the target, and still a goal? |
| BG-4 | Infra spend ≤ budget at 10 000 users | [BG-4](../drivers/business-goals/BG-4.md) | Is this still the target, and still a goal? |
| CON-1 | The system must run in mobile browsers (iOS Safari, Android Chrome); no native app at launch. | [CON-1](../drivers/constraints/CON-1.md) | Who still requires this, and what would lifting it cost? |
| CON-2 | One founding engineer builds the MVP; target delivery in 3 months. | [CON-2](../drivers/constraints/CON-2.md) | Who still requires this, and what would lifting it cost? |
| CON-3 | Launch on managed cloud low/free tiers; a paid upgrade path must exist. | [CON-3](../drivers/constraints/CON-3.md) | Who still requires this, and what would lifting it cost? |
| CON-4 | All financial data encrypted in transit (TLS 1.2+) and at rest. | [CON-4](../drivers/constraints/CON-4.md) | Who still requires this, and what would lifting it cost? |
| CON-5 | The primary datastore must be PostgreSQL (team skill, managed availability options). | [CON-5](../drivers/constraints/CON-5.md) | Who still requires this, and what would lifting it cost? |
| AQA-1 | Reliability: Uptime ≥ 99.5 %/month; recovery < 60 s; RPO < 5 min | [AQA-1](../drivers/quality-attributes/AQA-1.md) | Does this measure still hold, and is there evidence the system meets it? |
| MQA-1 | Maintainability: ≤ 1 person-day; ≤ 3 modules touched; 0 regressions | [MQA-1](../drivers/quality-attributes/MQA-1.md) | Does this measure still hold, and is there evidence the system meets it? |
| PQA-1 | Performance efficiency: Fully interactive < 1.5 s at p95 | [PQA-1](../drivers/quality-attributes/PQA-1.md) | Does this measure still hold, and is there evidence the system meets it? |
| PQA-2 | Performance efficiency: Import completes < 30 s; dashboard p95 stays < 1.8 s during the import | [PQA-2](../drivers/quality-attributes/PQA-2.md) | Does this measure still hold, and is there evidence the system meets it? |
| SQA-1 | Security: 0 successful cross-user reads; 100 % of attempts logged; alert < 1 min | [SQA-1](../drivers/quality-attributes/SQA-1.md) | Does this measure still hold, and is there evidence the system meets it? |
| UQA-1 | Interaction capability: ≥ 85 % task-completion rate in a 10-person moderated usability test | [UQA-1](../drivers/quality-attributes/UQA-1.md) | Does this measure still hold, and is there evidence the system meets it? |

## Quality characteristics with no scenario

3 of the 8 ISO/IEC 25010 characteristics that scenarios cover have no scenario in the register. Ask these in Step 4; record each answer as a driver, or as not significant here with the reason. Functional suitability is left out because use cases cover it.

### Compatibility

1. Which other systems must it exchange data with, now and in the next year?
2. Who controls each interface, and how much notice do we get when it changes?
3. What happens when a partner sends data we do not expect — reject it, store it, guess?
4. Must it run alongside other software on shared infrastructure without slowing it down?
5. Measure: What share of messages may fail or be lost, and how quickly must a failure be noticed?

### Flexibility

1. How large could this become — users, data, transactions, regions — in one year and in three?
2. Must it run in another environment later: another cloud, on-premises, a customer's site?
3. Which vendor or component would we most like to be able to replace?
4. Must new customers or tenants be set up without engineering work?
5. How often must new versions reach production, and how quickly must a bad one be rolled back?
6. Measure: At 10× today's load, how should cost and response time behave, and how long may it take to add capacity?

### Safety

1. Can the system's output hurt a person, damage property or the environment?
2. Which inputs or failures could put it into a dangerous state?
3. What is the safe state, and how fast must the system reach it?
4. Who must be warned, and how?
5. Measure: How long may the move to a safe state take, and how many hazards may go undetected?

## Questions by participant

Taken from the stakeholder register's QAW participants and the question guide's role table. Ask them of the person directly when they are quiet.

### ST-1 — Founder (sponsor / product owner)

- What does success look like in numbers?
- What failure would end the project?
- What is the budget ceiling for running it?

### ST-2 — Eng lead (architect / developer)

- Which requirement are you least sure how to meet?
- What is hard to change today?
- What would you build differently with more time?

### ST-3 — Contractor QA (tester)

- What is hard to test, and why?
- Which defects reach production?
- What test data can we not get?

### ST-4 — Advisor (security)

- What must never happen?
- What must be logged and kept, for how long?
- Which audit is next?

### ST-5 — Design partner (end-user representative)

- What do you do most often?
- What frustrates you today?
- What would make you stop using it?

## Parked questions still open

From [the previous workshop](qaw-report.md). Get each answer before the session, or ask it in the step named.

| ID | Question | Raised in | Who can answer | Owner | Due |
|----|----------|-----------|----------------|-------|-----|
| PQ-1 | How long must the audit log be kept for the SOC 2 Type II audit? | CS-1 refinement | SOC 2 auditor | ST-4 | 2026-09-03 |
| PQ-2 | Which browsers and screen readers must first use support at launch? | CS-5 refinement | Design partner's users | ST-5 | 2026-09-03 |
| PQ-3 | What monthly infrastructure budget does BG-4 allow at 10 000 users? | Step 2 | Founder, after the funding round | ST-1 | 2026-09-17 |
