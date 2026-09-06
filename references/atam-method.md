# Reference — Architecture Tradeoff Analysis Method (ATAM)

Source: Kazman, Klein, Clements — *ATAM: Method for Architecture Evaluation*, CMU/SEI-2000-TR-004;
Bass, Clements, Kazman — *Software Architecture in Practice*, ch. on evaluation.

## Purpose

Assess the consequences of architectural decisions in light of quality-attribute requirements.
ATAM does not grade an architecture or produce precise numbers; it **surfaces risks** and shows
where quality attributes **trade off** before those risks become expensive. Evaluators need no
prior familiarity with the architecture or its business goals, and the system need not be built.
*If a system is important enough to explicitly design its architecture, that architecture should
be evaluated.*

## Decide up front

- **Who sees the results?** Some evaluations are fully open with all stakeholders; others are
  more private.
- **Which stakeholders participate?** Elicit the important stakeholders' goals and concerns;
  identifying the right individuals and securing their time is critical.
- **What are the business goals?** The evaluation answers whether the system will meet them —
  if they aren't captured and prioritised beforehand, spend part of the evaluation doing it.

## Participants — three groups

- **Evaluation team** — external to the project under evaluation; 3–5 people; recognised as
  competent, unbiased outsiders. Roles (one person may take several):

  | Role | Responsibilities |
  |------|------------------|
  | **Team leader** | sets up the evaluation; coordinates with the client; establishes the contract; forms the team; ensures the final report is produced and delivered |
  | **Evaluation leader** | runs the evaluation; facilitates scenario elicitation, the prioritisation vote, and the analysis of scenarios against the architecture |
  | **Scenario scribe** | writes scenarios in a shared, public form; halts discussion until the exact agreed wording is captured |
  | **E-scribe** | captures the proceedings electronically — raw scenarios, the **issue that motivated each scenario** (often lost in the final wording), analysis results; produces the adopted-scenario list |
  | **Questioner** | asks probing quality-attribute-based questions |

- **Project decision makers** — empowered to speak for the project or mandate changes: usually
  the project manager, a customer representative if one is footing the bill, and — **cardinal
  rule — the architect, who must willingly participate.**
- **Architecture stakeholders** — 10–25 for a large enterprise-critical system: developers,
  testers, integrators, maintainers, performance engineers, users, owners of interacting
  systems. They articulate the specific QA goals the architecture must meet, and **join only
  Phase 2** — not the whole exercise.

## Outputs (seven, plus intangibles)

1. A **concise presentation of the architecture** — the ATAM caps it at ≤ 1 hour, which forces
   clarity.
2. **Articulated business goals** — often heard by some participants for the first time; this
   description survives the evaluation and becomes part of the project's legacy.
3. **Prioritised quality-attribute requirements as scenarios** — reused from a prior
   requirements/QAW/ADD exercise if one exists, otherwise generated during the ATAM.
4. **Risks and non-risks** — a risk is a decision that may lead to undesirable consequences
   given the QA requirements; a non-risk is a decision that, on analysis, is deemed safe. The
   risks feed a risk-mitigation plan — the primary output.
5. **Risk themes** — systemic weaknesses (in the architecture, or in the process/team) that the
   full set of risks reveals; left untreated they threaten the business goals.
6. **Mapping of architectural decisions to quality requirements** — for each scenario analysed,
   the decisions that help achieve it; this *is* the recorded rationale for those decisions.
7. **Sensitivity points and tradeoff points** — a sensitivity point is a decision with a marked
   effect on one QA response; a tradeoff point is a decision to which ≥ 2 QA responses are
   sensitive, where one improves as another degrades.

Intangibles: a sense of community among stakeholders, open channels between architect and
stakeholders, and a shared understanding of the architecture's strengths and weaknesses.

## The four phases

| Phase | Activity | Participants | Typical time |
|-------|----------|--------------|--------------|
| **0** | Partnership & preparation | evaluation team leadership + key project decision makers | informal, over a few weeks |
| **1** | Evaluation | evaluation team + project decision makers | 1–2 days |
| **2** | Evaluation (continued) | + the architecture stakeholders | 2 days |
| **3** | Follow-up | evaluation team + evaluation client | ~1 week |

**Phase 0** — agree logistics and meeting technology; brief the evaluators so the team can be
supplemented with the right expertise; agree a **preliminary stakeholder list by name (not just
role)**; negotiate when the report is delivered and to whom; handle the SOW / NDA. The team
studies the architecture documentation. The evaluation leader tells the manager and architect
what to present in Phase 1 and helps build those presentations.

**Phase 3** — the team produces and delivers the final report (a formal document *or* a set of
slides). Circulate it to key stakeholders first to catch errors of understanding, then deliver
to the client.

## The nine steps

Steps 1–6 run in Phase 1 (team + decision makers). In Phase 2, steps 1–6 are **summarised** for
the wider group and steps 7–9 are carried out.

**Step 1 — Present the ATAM.** The evaluation leader explains the process, the techniques
(utility tree, approach analysis), and the outputs; sets context and expectations.

**Step 2 — Present the business goals.** A decision maker (ideally the PM or customer rep)
presents a system overview from the business perspective: the most important functions; relevant
technical / managerial / economic / political constraints; business goals and context; major
stakeholders; the architectural drivers (the architecturally significant requirements).

**Step 3 — Present the architecture.** The lead architect presents at a level of detail set by
how much of the architecture is designed and documented, how much time is available, and the
nature of the behavioural and quality requirements. Covers technical constraints (OS, mandated
platforms), other systems it interacts with, and — most importantly — the **architectural
approaches** used to meet the requirements. **Views** are the primary vehicle: context, C&C,
module decomposition/layered, and deployment are useful in almost every evaluation.

**Step 4 — Identify architectural approaches.** Catalog the patterns and tactics in use, for
their *known* effects on quality attributes (layered → portability + maintainability, possibly
at a performance cost; publish-subscribe → scalable in producers/consumers; active redundancy →
high availability). No analysis yet.

**Step 5 — Generate the quality-attribute utility tree.** Broad goals from Step 2 ("modifiable",
"high throughput", "portable") set direction but aren't analysable — *modifiable in what way?
throughput how high? ported to what and in how long?* Refine into concrete scenarios in the
**tabular utility tree** (`Utility → QA → refinement → scenario`). Built by the **architect and
the decision makers together**: the architect rates each scenario's **technical difficulty /
risk** (H/M/L); the decision makers rate its **business importance** (H/M/L). See
`references/architectural-drivers.md`.

**Step 6 — Analyze the architectural approaches.** Take the highest-ranked scenarios one at a
time; the architect explains how the architecture supports each; questioners probe for the
approaches invoked. For each, document the relevant decisions and catalog risks / non-risks /
sensitivity points (`S-n`) / tradeoff points (`T-n`). For well-known approaches, ask how the
architect overcame the approach's known weaknesses or gained assurance it sufficed. If the
architect **cannot characterise** a key parameter (e.g. the number of clients, how load
balancing allocates processes), that inability is itself a risk; where the questions *can* be
answered, do a **back-of-the-envelope analysis** to see whether the decisions are problematic
against the QA requirements. The analysis is **not** meant to be comprehensive — elicit just
enough to link the decisions to the QA requirements. Use the analysis template below and, as the
question bank, the **tactics-based questionnaire** for the relevant attribute
(`references/tactics-catalog.md`).

**Hiatus** (~1 week) — the team summarises what it learned and interacts informally with the
architect; a few more scenarios may be analysed and Phase-1 questions clarified.

**Step 7 — Brainstorm and prioritize scenarios.** With all stakeholders, brainstorm scenarios
that are operationally meaningful to each role (a maintainer → a modifiability scenario; a user
→ ease of operation; a QA person → testability / state-reproduction). Where the utility tree
captured *the architect's* view of the drivers, brainstorming takes *the wider community's*
pulse. Merge near-duplicates. Then **vote**: each stakeholder gets votes = **ceil(0.30 ×
scenario count)**, spendable any way (all on one, spread across many). Compare the ranked list
with the utility tree — agreement = alignment; a large discrepancy is itself a risk (the
stakeholders and architect disagree about what matters).

**Step 8 — Analyze the architectural approaches (again).** Repeat Step 6's activity for the
highest-ranked *new* scenarios from Step 7 — typically the top 5–10, as time allows.

**Step 9 — Present the results.** Group the risks into **risk themes** by common underlying
concern / systemic deficiency (e.g. several documentation risks → "documentation is given
insufficient consideration"; several failure-handling risks → "insufficient attention to
backup / high availability"). Map each theme to the **business goals from Step 2** it threatens
— this brings the evaluation full circle and elevates each risk to a threat against something
management is on record as caring about. Present: the documented approaches; the brainstormed &
prioritised scenarios; the utility tree; risks & non-risks; sensitivity & tradeoff points; risk
themes and the business goals each threatens.

### Step 6 / 8 scenario-analysis template

| Field | Content |
|-------|---------|
| Scenario # + text | `<ATTR>QA-id` — one-line scenario |
| Attribute(s) | ISO/IEC 25010 characteristic(s) |
| Environment · Stimulus · Response | the scenario's environment, stimulus, and required response measure |
| Architectural decisions | one row per relevant decision, each tagged with any of: **Sensitivity `S-n`**, **Tradeoff `T-n`**, **Risk `R-n`**, **Non-risk `N-n`** |
| Reasoning | why each decision does/doesn't achieve the response; references to the risks |
| Architecture diagram | a small diagram of the elements involved |

## Going off script

No evaluation ever goes exactly by the book — no architecture documented, the wrong architecture,
the architect leaving mid-exercise — yet they succeed, for three reasons: (1) everyone in the
room *wants* it to succeed and keeps it moving toward insight; (2) the team is **always honest**
— call a timeout and confer if it derails, never bluff (participants detect it and you lose
their respect); (3) the method maintains a steady consensus — the participants set the ground
rules for "a suitable architecture" and contribute risks at every step, so there are **no
surprises at the end.**

## Utility tree vs. scenario brainstorming

Two ways to get the prioritised scenarios, deliberately complementary:

| | Utility tree (Step 5) | Scenario brainstorming (Step 7) |
|---|-----------------------|--------------------------------|
| Driven by | the architect, top-down | the stakeholder group, bottom-up |
| Produces | QA → refinement → scenario, each rated `(V, R)` | use-case / growth / exploratory scenarios, vote-ranked |
| Bias it counters | stakeholders miss architecturally significant needs | the architect's blind spots and assumptions |

Convergence between the two is reassuring; divergence is informative — a highly-voted scenario
that isn't in the tree is a signal the tree missed something.

## Characterizing an attribute for analysis

Before Step 6, it helps to characterise each attribute under scrutiny in three parts — this is
the skeleton the tactics-based questionnaire fills in:

- **Stimuli** — the events the architecture must respond to for this attribute (arrival
  patterns and load for performance; fault types for availability; change categories for
  modifiability; attack types for security).
- **Responses** — the observable, measurable outcomes required (latency percentile; recovery
  time; effort to change; proportion of attacks detected).
- **Architectural decisions** — the parameters and structures that determine the response
  (concurrency and queueing for performance; redundancy and failover for availability;
  encapsulation and binding time for modifiability). These are where sensitivity and tradeoff
  points live.

## After the analysis — CBAM

ATAM says *where the risks and tradeoffs are*; it does not say *which fix is worth doing*. The
**Cost/Benefit Analysis Method (CBAM)** is the follow-on: for each candidate architectural
strategy, estimate the utility it adds (as levels of quality-attribute response), its cost, and
its schedule, then rank the strategies by return on investment. Run it after ATAM to turn risk
themes into a prioritised remediation backlog; it can also inform design directly.

## Definitions worth keeping straight

- **Sensitivity point**: "The response measure of quality attribute Q is sensitive to the value
  of property P of element E." (e.g. throughput is sensitive to the thread-pool size.)
- **Tradeoff point**: a sensitivity point involving ≥ 2 attributes pulling in opposite
  directions. (e.g. increasing cache TTL improves latency but worsens data freshness.)
- **Risk**: an architectural decision that has not been made, or has been made and is
  questionable given the drivers. Phrase as: *"decision X may lead to consequence Y, which
  endangers driver Z."*
- **Non-risk**: a good decision — but always record the **assumption** that makes it good, since
  assumptions can change.
- **Risk theme**: a set of risks with a common root (e.g. "no operational monitoring anywhere",
  "availability depends on several unreplicated singletons"). Themes, not individual risks, drive
  the recommendations.

## Lightweight Architecture Evaluation (LAE)

A full ATAM is a two-phase, multi-day exercise with external evaluators and a formal report —
right for a high-risk, high-cost, or contested architecture. **LAE** is the same method for a
**project-internal peer review, run regularly** (each ADD round, before a release, when the
architecture or its drivers change, or to examine a previously unreviewed part). Because the
scope is limited, most ATAM steps are shortened or omitted. Convened and led by the **project
architect**; a couple of hours to a full day; carried out entirely by people internal to the
organisation. No final report — a scribe captures the results for sharing and risk remediation.

Typical LAE agenda:

| Step | In an LAE |
|------|-----------|
| 1 Present the method | may be **omitted** if participants know the process |
| 2 Review the business goals | **brief** — ensure they're fresh and there are no surprises |
| 3 Review the architecture | **brief** overview, ≥ module + C&C views, highlight changes since the last review, trace 1–2 scenarios through the views |
| 4 Review the architectural approaches | usually done as **part of step 3** |
| 5 Review the utility tree | a tree already exists — **review and update** it (new scenarios, new response goals, new priorities / risk ratings) |
| 6 Brainstorm & prioritize scenarios | a **brief** brainstorm — do any new scenarios merit analysis? |
| 7 Analyze the architectural approaches | the **bulk of the time** — map the highly-ranked scenarios onto the architecture, focusing on the most recent changes or an unanalysed part; reanalyse high-priority scenarios if the architecture changed |
| 8 Capture the results | review existing + newly found risks / non-risks / sensitivities / tradeoffs; note any new risk themes |

Trade-off: an internal team is **less objective** than an external one — fewer new ideas, fewer
dissenting opinions — but it's cheap, low-ceremony, and easy to convene, so it works as a
routine architecture-quality sanity check.

**Escalate to a full ATAM** when: an LAE keeps surfacing the same systemic risk theme;
stakeholders disagree about which quality attributes matter; the cost of being wrong is high;
the architecture is being handed between organisations.

Even lighter still — the **tactics-based questionnaire** (~1 hour per quality attribute; each
tactic becomes a "Does the system support …?" question) — can be run solo by the architect for
reflection, or as a short evaluator↔architect Q&A. It reveals design decisions taken *and not
taken*, and the risks buried in them, very quickly. Also: reflective questions and a
scenario-based design review (`references/design-reviews.md`).

## After ATAM

Risk themes become the input to targeted **ADD** iterations. Update the `architectural-drivers`
register's `Status` column with what ATAM found.
