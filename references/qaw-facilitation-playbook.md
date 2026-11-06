# Reference — QAW facilitation playbook (how to run the room)

The question guide (`${CLAUDE_PLUGIN_ROOT}/references/qaw-question-guide.md`) says what to ask;
this playbook says how to run the workshop around those questions: which format to pick, how long
each step takes, who does what, what to do when the room goes wrong, how to tell a weak scenario
from a usable one, and what happens after everyone leaves. The method itself is in
`${CLAUDE_PLUGIN_ROOT}/references/qaw-method.md`.

## Choose a format

| Format | When it fits | Who and how many | What you give up |
|--------|--------------|------------------|------------------|
| **two-day** | A large or regulated system, many stakeholder groups, a contract or a programme at stake | 8–15 people in one room | Nothing; this is the method as the SEI describes it |
| **one-day** | Most new systems and major changes | 5–10 people in one room | Fewer brainstorming passes; refine 4–6 scenarios in the room and the rest in `/drivers` |
| **half-day** | A small team, a product increment, a refresh of an existing register (often called a mini-QAW) | 3–7 people | Refine the top 2–3 scenarios only; Steps 2–4 must lean on documentation sent before the session |
| **remote** | People in different places or time zones | 4–10 people on a call with a shared document | Three short sessions instead of one long day; voting between sessions is allowed |

Record the format in the report header (`- **Format**: one-day`). `qawkit.py agenda` turns the
timeboxes below into a dated agenda.

**Relayed** workshops — one person (often the architect) answers for a group that is not
present — use any format's step order. Note in the report that the vote is a proxy vote and
carries less weight.

## Timeboxes

Minutes per block. A *Next day* row starts a new day (or, for **remote**, a new session) at the
same start time on the next working day. Blocks run in the order listed.

### two-day

| Block | Minutes |
|-------|--------:|
| Step 1 — QAW presentation and introductions | 45 |
| Step 2 — Business and mission drivers | 90 |
| Break | 15 |
| Step 3 — Architectural plan | 60 |
| Lunch | 60 |
| Step 4 — Architectural drivers | 75 |
| Break | 15 |
| Step 5 — Scenario brainstorming | 120 |
| Next day | — |
| Recap of day 1 | 15 |
| Step 6 — Scenario consolidation | 60 |
| Step 7 — Scenario prioritisation | 45 |
| Break | 15 |
| Step 8 — Scenario refinement | 105 |
| Lunch | 60 |
| Step 8 — Scenario refinement (continued) | 75 |
| Break | 15 |
| Step 9 — Utility tree | 45 |
| Wrap-up — parked questions and next steps | 30 |

### one-day

| Block | Minutes |
|-------|--------:|
| Step 1 — QAW presentation and introductions | 20 |
| Step 2 — Business and mission drivers | 40 |
| Step 3 — Architectural plan | 30 |
| Break | 15 |
| Step 4 — Architectural drivers | 40 |
| Step 5 — Scenario brainstorming | 65 |
| Lunch | 45 |
| Step 6 — Scenario consolidation | 30 |
| Step 7 — Scenario prioritisation | 20 |
| Break | 10 |
| Step 8 — Scenario refinement | 90 |
| Break | 15 |
| Step 9 — Utility tree | 30 |
| Wrap-up — parked questions and next steps | 15 |

### half-day

| Block | Minutes |
|-------|--------:|
| Step 1 — QAW presentation and introductions | 10 |
| Step 2 — Business and mission drivers | 20 |
| Step 3 — Architectural plan | 10 |
| Step 4 — Architectural drivers | 20 |
| Step 5 — Scenario brainstorming | 45 |
| Break | 10 |
| Step 6 — Scenario consolidation | 15 |
| Step 7 — Scenario prioritisation | 15 |
| Step 8 — Scenario refinement | 60 |
| Step 9 — Utility tree | 20 |
| Wrap-up — parked questions and next steps | 15 |

### remote

| Block | Minutes |
|-------|--------:|
| Step 1 — QAW presentation and introductions | 20 |
| Step 2 — Business and mission drivers | 45 |
| Break | 10 |
| Step 3 — Architectural plan | 30 |
| Step 4 — Architectural drivers | 40 |
| Next day | — |
| Recap of session 1 | 10 |
| Step 5 — Scenario brainstorming | 70 |
| Break | 10 |
| Step 6 — Scenario consolidation | 30 |
| Step 7 — Scenario prioritisation | 20 |
| Next day | — |
| Recap of session 2 | 10 |
| Step 8 — Scenario refinement | 90 |
| Break | 10 |
| Step 9 — Utility tree | 25 |
| Wrap-up — parked questions and next steps | 15 |

When time runs short, cut the number of scenarios refined in Step 8, never the vote: an
unrefined scenario can be refined later in `/drivers`, but a list nobody prioritised cannot be
used to order design work.

## Roles in the room

| Role | Does | Can Claude do it? |
|------|------|-------------------|
| **Lead facilitator** | Runs the steps, asks the questions, keeps the room neutral | It can script the questions and suggest the next one; a person should lead a live room |
| **Scribe** | Writes every answer, scenario and vote into the report as it happens | Yes; the report is updated after every step |
| **Timekeeper** | Watches the agenda and calls the end of each block | It can track the agenda; someone in the room calls time |
| **Sponsor** | Presents Step 2, answers business-value questions in Step 9 | No |
| **Architect** | Presents Step 3, answers technical-risk questions in Step 9 | No; the architect owns the risk estimate |

The facilitator never contributes scenarios or votes. A facilitator who is also the system's
architect says so at the start and hands Step 3 to someone else if possible.

## Before the workshop

1. **Two weeks before.** Pick the format and the date. Invite one person for each role in the
   question guide's role table; for a role nobody can fill, name who will answer its questions
   afterwards.
2. **One week before.** Collect the documents the workshop will rely on (Step 0): brief,
   requirements, drivers register, earlier QAW report, architecture notes. Choose the entry mode.
3. **Three days before.** Generate `qaw-prep.md` and `qaw-agenda.md` with `qawkit.py` and send
   both, with the business drivers, as the pre-read. Ask the sponsor to bring numbers: users,
   budget, deadlines.
4. **The day before.** Open the report from the template, fill in Step 0 and the participant
   list, and prepare the board or shared document the scenarios will be written on.

## Difficult moments

| Signal | What to do | What to say |
|--------|------------|-------------|
| One person answers every question | Switch to strict round-robin; ask quiet people by name | "Let's hear from everyone once before anyone goes twice." |
| Someone has not spoken for a whole step | Ask their role's questions from the guide directly; offer to take a written answer | "From the on-call side, what would wake you up at night?" |
| Talk turns to technology ("we'll use Kafka") | Ask what it is for, write that down as the requirement, and park the idea as an issue | "What would that give us? Let's write the need down; the design comes later." |
| "Everything is critical" | Move on to the bad-day question; remind the room that the vote decides | "If this failed for a day, what would it cost? We'll compare those costs in the vote." |
| Two people argue about priority during brainstorming | Record both scenarios and defer to Step 7 | "Both go on the list. The vote settles which matters more." |
| Two people give different numbers | Record both as a range; bracket; park if still open | "So somewhere between one hour and one day. Who can decide which?" |
| Functional requests pile up ("it should also export PDFs") | Record each as a use-case candidate and ask what quality it implies | "Noted as a feature. What would make that export good enough — size, time, format?" |
| A complaint about the current system | Turn it into a scenario | "What would have to be true for that never to happen again?" |
| Nobody knows the answer | Bracket once; if still unknown, park it as `PQ-<n>` with an owner | "Let's park it. Who can answer it, and by when?" |
| Two scenarios pull against each other (security against ease of use) | Record the conflict as an issue on both; it is a tradeoff for ADD and ATAM to analyse | "Both are valid. We'll write down that they conflict and let the design weigh them." |
| The sponsor or a key role leaves early | Ask their Step 9 value questions before they go; park the rest for them | "Before you leave: which of these would hurt the business most if we missed it?" |
| The session runs late | Keep the vote; refine fewer scenarios; schedule the rest | "We'll refine the top three now and the rest in the drivers session on Thursday." |
| Remote: cameras off, people multitasking | Shorter blocks; written round-robin in the shared document; read out each new scenario | "Type your scenario in the document; I'll read each one out." |

## Scenarios that hold up

A refined scenario is usable when someone could test it. `qawkit.py lint` checks the rows marked
*automatic*; the facilitator checks the rest by reading.

| Smell | Example | Fix | Checked |
|-------|---------|-----|---------|
| Vague word in the measure | "responds fast" | Ask the guide's follow-up for that word and record a number | automatic |
| No number in the response measure | "users are happy" | Ask how anyone would test it; record value, unit and percentile | automatic |
| Generic source | "the user" | Name the role or system: "a first-time user", "the payment provider" | automatic |
| Empty part | no environment given | Ask the part's question from the guide's Step 8 table | automatic |
| No business goal | refined scenario cites no `BG-<n>` | Ask which goal it protects; a scenario no goal needs is a candidate for the bin | automatic |
| A solution in the scenario | "Redis caches the dashboard" | Ask what the cache is for; the scenario keeps the need, the design keeps the cache | reading |
| Two events in one stimulus | "a node fails and traffic doubles" | Split into two scenarios, or keep both events only if they must be handled together | reading |
| Response describes the implementation | "the circuit breaker opens" | Describe what an observer sees: "requests fail fast with a clear error" | reading |

## After the workshop

1. **Within one working day.** Generate `qaw-summary.md` and send it with the report to
   everyone who took part, and to the roles that were missing.
2. **Within one week.** Chase every parked question by its due date. Show the refined
   scenarios to the people who could not attend and record their corrections in the report.
3. **Within two weeks.** Run `/drivers` from the hand-off table, then start design with `/add`.
4. **Run the workshop again** (refresh mode) when one of these happens: a new market,
   customer type or regulation; growth of ten times in users or data; a major incident; a large
   architecture change; a change of team or of a key vendor; or six to twelve months without a
   review.
