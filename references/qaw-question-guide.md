# Reference — QAW question guide (what to ask, step by step)

This is the facilitator's script for the Quality Attribute Workshop: the questions to ask at each
step, the questions that draw out each quality attribute, and the questions that test
documentation which already exists. The method itself (roles, the eight steps, outputs) is in
`${CLAUDE_PLUGIN_ROOT}/references/qaw-method.md`; this file is only about what to say in the room.

Start with **Choose the entry mode** below, then work through **Questions by step** in order. The
attribute and role sections are pools you draw from during Steps 4, 5 and 8.

## How to ask

- **Rely on the documentation available.** Before asking a question, check whether the documents
  found in Step 0 already answer it. If they do, quote the answer and its source and ask only
  whether it still holds ("The brief sets 99.5 % uptime per month — still right?"). Ask open
  questions only about what the documents do not cover. When a stakeholder contradicts a
  document, record both and what the group decided.
- **One question at a time.** Wait for the answer, play it back in one line, then move on.
- **Ask about situations, not qualities.** "Should it be secure?" gets "yes" and nothing else.
  "Who would want to see data that isn't theirs, and what would they try?" gets a scenario.
- **Ask for the bad day.** Stakeholders describe the normal day by default. Every attribute
  section below has at least one question about failure, overload or change.
- **Never put a technology in a question.** "Do we need Kafka?" is a design decision in disguise.
  When a stakeholder answers with a technology ("we'll use Redis"), ask what it is *for* — the
  answer to that is the requirement.
- **Translate jargon both ways.** Ask in the stakeholder's words; record in the six-part form.
- **No answer is an answer.** If nobody in the room knows, record the question as a parked
  question (`PQ-<n>`) with an owner and a date, and keep going. Do not invent a number to fill
  the gap.
- **Find the number by bracketing.** When a stakeholder cannot give a number, offer values from
  far too lenient to far too strict until they object at both ends ("Would a day be acceptable?
  An hour? A minute? A second?"). A range is enough to choose a design approach — see the "play
  dumb" technique in `${CLAUDE_PLUGIN_ROOT}/references/architectural-drivers.md`.

## Choose the entry mode (before Step 1)

The workshop runs in one of three modes. Decide it from what exists, say it out loud, and record
it in the report's *Starting point* section.

| Mode | When | What changes in the workshop |
|------|------|------------------------------|
| **greenfield** | Nothing documented: no drivers register, no scenarios, no architecture | Every step starts from open questions. Expect Steps 2–4 to take longest. |
| **partial** | Some inputs exist: a product brief, a requirements document, a codebase, a few loose scenarios, an old slide deck | Read them before Step 1. Present what they say as a draft in Steps 2–4 and ask the group to correct it. Mark anything taken from code as *derived — confirm* (`${CLAUDE_PLUGIN_ROOT}/references/brownfield-intake.md`). |
| **refresh** | A drivers register (`architecture/drivers/`) and quality attribute scenarios already exist, possibly from an earlier QAW | Steps 2–4 confirm and challenge the existing drivers instead of eliciting them. Step 5 starts from the existing scenarios and spends its time on the gaps. Steps 7–8 re-prioritise everything, old and new together. |

Questions that settle the mode:

1. Is there a written list of business goals, use cases, constraints or quality requirements for
   this system? Where?
2. Has a QAW, an architecture review or an ATAM been run before? When, and who took part?
3. Does an architecture or a codebase exist yet, or is this before design?
4. Of what exists, what does the team still trust, and what does everyone know is out of date?
5. What has changed since the documents were written: users, load, team, regulations, vendors,
   incidents?

If a previous `architecture/qaw/qaw-report.md` exists, the earlier workshop is history, not a
draft to overwrite: keep it as `architecture/qaw/qaw-report-<its date>.md` and link it from the
new report's *Starting point*.

## Questions by step

### Step 1 — Introductions

Ask each participant:

1. What is your role on this system, and what do you need from it?
2. What would make you call this system a failure a year from now?
3. Which part of the system do you know best, and which part worries you most?
4. Who else should be here and is not? (Record absent roles; a scenario no one in the room can
   speak for is a parked question for that role.)

*Refresh:* Who here took part last time? For newcomers: what concern do you bring that the
earlier workshop might have missed?

### Step 2 — Business and mission drivers

Ask the sponsor or product owner:

1. Why is this system being built (or changed) now? What happens if it is not?
2. What must be true in 12 months for this to count as a success? How will you measure it?
3. Who pays for it, who uses it, and who loses if it fails?
4. What is the deadline, and what moves it: a contract, a market window, a regulation?
5. What budget limits apply: build cost, monthly running cost, team size?
6. Which laws, standards or audits apply (privacy, accessibility, financial, safety, industry)?
7. If you could have only two of *fast*, *cheap to run* and *quick to change*, which two?
8. What do competitors or the system being replaced do well that this one must at least match?

*Refresh:* For each existing `BG-<n>`, ask: Is this still a goal? Has its target or deadline
moved? Is there a goal we are now pursuing that is not on this list? Mark goals that no longer
apply `retired`; never delete them.

### Step 3 — Architectural plan

Ask the architect or technical lead:

1. Where does the system's boundary lie: what is inside it, and what is someone else's?
2. Which external systems does it talk to? For each: who owns it, how reliable is it, can its
   interface change without warning?
3. What is already decided and not open for discussion: platform, language, cloud, datastore,
   vendors? Who decided, and why?
4. What exists already that must be reused or kept running?
5. Where will it run, and who will operate it at 3 a.m.?
6. What does the team know well, and what would be new to them?

*Greenfield with no plan:* record "none yet" and ask only questions 3, 5 and 6 — constraints
exist even before an architecture does.
*Refresh:* What has changed in the architecture since the drivers were written? Which existing
ADRs or views no longer match the running system?

### Step 4 — Architectural drivers

Present the draft driver list, then ask:

1. Is anything on this list wrong, or out of date?
2. What is missing — what would hurt most if the architecture ignored it?
3. Which two of these would you defend if we could address only two?
4. Does any driver conflict with another? (Write the conflict down; it becomes a tradeoff to
   analyse, not a debate to settle now.)
5. Which of these is a constraint we must accept, and which is a goal we could negotiate?

*Refresh:* Walk the existing register — every `<ATTR>QA-<n>`, `CON-<n>`, and the use cases marked
architecturally significant — and ask questions 1, 2 and 5 of each. Then name every ISO/IEC 25010
characteristic that has **no** scenario in the register, and ask: is this one truly unimportant
here, or did nobody ask? (The attribute sections below are the follow-up.)

### Step 5 — Scenario brainstorming

Each turn, the participant completes one prompt. Rotate across the three scenario types so the
list is not all normal-day use:

- **Use-case:** "When a [user / system / operator] does [action] during [normal day / month end
  / launch], the system should ..."
- **Growth:** "In a year, when [users / data / features / regions] have grown to [amount], we
  need to [change or scale] within [time or effort] ..."
- **Exploratory:** "On the worst day — when [component] fails / [load] spikes / [attacker] tries
  [action] / [vendor] disappears — the system must at least ..."

Prompts to restart a stalled round:

1. What is the most expensive thing that could go wrong?
2. What do customers complain about in the current system (or a competitor's)?
3. What change are you already expecting that the system will have to absorb?
4. What would an auditor, an attacker or the on-call engineer ask about?
5. Which driver from Step 4 has no scenario yet?

*Refresh:* Show the existing scenarios first, then aim the round only at gaps: characteristics
with no scenario, drivers with no scenario, and anything that changed since the last session.
Existing scenarios enter the list as they are, tagged *existing*, so they are voted on alongside
the new ones.

### Step 6 — Consolidation

1. Are these two describing the same event and the same response? If one is broader, which
   wording do we keep?
2. Does anyone object to merging these? (An objection keeps them separate; record why.)
3. Is this scenario really two — one about normal operation and one about failure? (Split it.)

### Step 7 — Prioritisation

Before voting, remind the group what a vote means, then ask:

1. Vote for the scenarios that, if the system failed them, would hurt the business goals most.
2. After the tally: does the top of this list surprise anyone? Is something important ranked low
   because it is unglamorous rather than unimportant?

*Refresh:* Vote on existing and new scenarios together. A scenario that drops sharply in the
ranking is a finding — ask what changed.

### Step 8 — Refinement

For each top scenario, fill the six parts with one question each:

| Part | Question |
|------|----------|
| Source of stimulus | Who or what starts this? Name the role or system, not "the user". |
| Stimulus | What exactly happens? Describe the single event. |
| Artifact | Which part of the system receives it — the whole system, one service, a datastore, the deployment pipeline? |
| Environment | What state is the system in at that moment: normal, peak, degraded, mid-deployment, recovering? |
| Response | What should be observable afterwards? Describe behaviour, not implementation. |
| Response measure | How would we test that it happened? What number, in what unit, at what percentile? |

Then ask:

1. Which business goal does this scenario protect? (Every refined scenario cites at least one
   `BG-<n>`.)
2. How would the architecture have to work to achieve this — and what is the hardest part?
   (Record these as the scenario's *questions*; do not design in the room.)
3. What are we assuming that might not be true? (Record as *issues*.)
4. Under what conditions would this number no longer be good enough?

### Step 9 — Utility tree priorities

For each leaf scenario, two questions set the `(V, R)` pair:

1. **Business value** — ask the sponsor: if we miss this, what does it cost? (High: a goal fails.
   Medium: a goal is delayed or weakened. Low: an annoyance.)
2. **Technical risk** — ask the architect: how confident are we that we know how to achieve this?
   (High: no proven approach for this context. Medium: known approach, unproven here. Low: done
   it before.)

## Questions by quality attribute (ISO/IEC 25010:2023)

Use these when a characteristic is missing from the drivers, when a brainstorming round stalls,
or when a stakeholder's answer is too vague to refine. Each list ends with a question that draws
out the response measure. Characteristic definitions and measures are in
`${CLAUDE_PLUGIN_ROOT}/references/quality-attribute-taxonomy.md`.

### Performance efficiency

1. Which actions must feel instant to the user, and which can take a while?
2. How many people or systems use it at the busiest moment? When is that moment — a time of day,
   a month end, a campaign?
3. What happens to the business if a page or job takes ten times longer than usual?
4. Is there a batch or report that must finish inside a window (overnight, before market open)?
5. Which resource is expensive or capped — CPU, memory, database connections, third-party API calls?
6. *Measure:* At peak, how long may the slowest 5 % of requests take before users complain or
   leave?

### Compatibility

1. Which other systems must it exchange data with, now and in the next year?
2. Who controls each interface, and how much notice do we get when it changes?
3. What happens when a partner sends data we do not expect — reject it, store it, guess?
4. Must it run alongside other software on shared infrastructure without slowing it down?
5. *Measure:* What share of messages may fail or be lost, and how quickly must a failure be
   noticed?

### Interaction capability (usability)

1. Who are the users — how often do they use it, and how much training do they get?
2. What is the one task a first-time user must manage without help?
3. Which mistakes would be costly for a user, and can they be undone?
4. Which accessibility standard applies (for example WCAG 2.2 AA), and on which devices and
   languages?
5. *Measure:* What share of first-time users must complete the key task, in how many minutes,
   with how many errors?

### Reliability (availability, fault tolerance, recoverability)

1. When must the system be available — around the clock, business hours, specific windows?
2. What does an hour of downtime cost, and who notices first?
3. Which external dependency is most likely to fail, and what should the system do when it does?
4. How much data could the business lose in a disaster — none, the last minute, the last day?
5. How long may a full recovery take after the worst plausible failure?
6. *Measure:* What uptime per month, what maximum data loss (RPO) and what maximum recovery
   time (RTO)?

### Security

1. Which data would cause the most harm if it leaked, was altered, or was deleted?
2. Who would want to attack this system, and what would they try first?
3. Who may see or change what? Are there users who must never see each other's data?
4. What must be provable afterwards — who did what, and when?
5. Which regulations or audits apply (GDPR, SOC 2, PCI DSS, HIPAA), and what do they require
   of the system?
6. *Measure:* How quickly must an attack be detected, how many may succeed (usually zero), and
   what share of attempts must be logged?

### Maintainability (modifiability, testability, analysability)

1. What changes do you expect most often — new features, rules, reports, integrations, UI?
2. Who makes those changes, and how much do they know about the system?
3. When a defect is reported, how long should it take to find the cause?
4. Which parts of the system does everyone avoid touching, and why?
5. How much of the behaviour must be testable automatically before a release?
6. *Measure:* How many person-days may a typical change take, and how many modules may it touch?

### Flexibility (scalability, adaptability, installability)

1. How large could this become — users, data, transactions, regions — in one year and in three?
2. Must it run in another environment later: another cloud, on-premises, a customer's site?
3. Which vendor or component would we most like to be able to replace?
4. Must new customers or tenants be set up without engineering work?
5. How often must new versions reach production, and how quickly must a bad one be rolled back?
6. *Measure:* At 10× today's load, how should cost and response time behave, and how long may
   it take to add capacity?

### Safety

1. Can the system's output hurt a person, damage property or the environment?
2. Which inputs or failures could put it into a dangerous state?
3. What is the safe state, and how fast must the system reach it?
4. Who must be warned, and how?
5. *Measure:* How long may the move to a safe state take, and how many hazards may go undetected?

### Functional suitability

Usually captured as use cases, not quality scenarios — but ask:

1. Which calculation or rule would cause real harm if it were wrong (money, dosage, legal
   deadlines)?
2. How would anyone notice it was wrong?
3. *Measure:* What error rate is acceptable, and how is correctness checked?

## Questions by stakeholder role

When one role is quiet, ask its questions directly.

| Role | Ask |
|------|-----|
| Sponsor / product owner | What does success look like in numbers? What failure would end the project? What is the budget ceiling for running it? |
| End user or their representative | What do you do most often? What frustrates you today? What would make you stop using it? |
| Architect / developer | Which requirement are you least sure how to meet? What is hard to change today? What would you build differently with more time? |
| Tester / QA | What is hard to test, and why? Which defects reach production? What test data can we not get? |
| Operations / on-call | What wakes you up at night? How do you know the system is healthy? How long does a deploy or a rollback take? |
| Security / compliance | What must never happen? What must be logged and kept, for how long? Which audit is next? |
| Integration partner | How often does your interface change? What do you do when ours is down? What volume do you send at peak? |
| Support / customer success | What do customers call about most? What can you not answer without an engineer? |

## Testing what already exists (partial and refresh modes)

When a document or register already exists, do not read it back for approval — test it. For each
artifact type:

**Business goals (`BG-<n>`)**
1. Is this goal still current, and does it still have a measurable target?
2. Which scenarios support it? A goal with no supporting scenario is a gap; ask what would show
   progress toward it.

**Quality attribute scenarios (`<ATTR>QA-<n>`)**
1. Does the response measure still hold, or has the business moved it?
2. Is there evidence the system meets it today — a dashboard, an SLO, a test? If not, how would
   we know?
3. Is the environment still right? A scenario written for normal operation often needs a
   degraded-mode twin.
4. Has an incident since the scenario was written shown that it was wrong or incomplete?

**Constraints (`CON-<n>`)**
1. Who imposed this, and do they still require it?
2. What would it cost to lift it, and has that changed?

**Use cases (`UC-<n>`)**
1. Is this still how users work, and is it still architecturally significant?
2. Has a new use case appeared that crosses a trust boundary, dominates load, or adds an
   integration?

**Utility tree**
1. Do the `(V, R)` pairs still hold? A leaf whose risk was retired by a design decision moves
   to *addressed*.
2. Which characteristic now has no leaf?

**Architecture documentation, ADRs, as-built views**
1. Which decision record would we decide differently today, and why?
2. Where does the running system differ from the documented one? (Each difference is a finding.)

## Turning vague answers into scenarios

| The stakeholder says | Ask next |
|----------------------|----------|
| "It must be fast." | Which action, at what load, measured how? How slow is too slow? |
| "It must always be up." | Always — including during deploys and maintenance? What does an hour of downtime cost? |
| "It must be secure." | Against whom, protecting what, and what must happen when someone tries? |
| "It must scale." | Scale in what — users, data, tenants, regions? To how much, by when? |
| "It must be easy to use." | For whom, doing which task, measured how — time, errors, completion? |
| "It must be easy to change." | Which change, made by whom, in how long? |
| "Real-time." | Within how many milliseconds or seconds, and what happens if a deadline is missed? |
| "Like the current system." | Which behaviour of the current system, exactly? Is it measured today? |

## Questions not to ask

- **Yes/no questions about qualities** ("Is availability important?") — everyone says yes.
- **Questions that name a solution** ("Should we cache this?") — they skip the requirement.
- **Questions that rank attributes in the abstract** ("Is security more important than
  performance?") — ask instead which *scenario* matters more; the answer differs by scenario.
- **Questions that put one stakeholder's view up for the room to judge** — collect every
  scenario first; the vote in Step 7 decides priority.
