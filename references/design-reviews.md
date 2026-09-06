# Reference — Lightweight architecture & design reviews

Design and analysis interleave. Between full evaluations (ATAM) there are cheap, repeatable
checks an architect or a small team runs every iteration or before a release. All three below
feed the same registers as ATAM (risks / non-risks / sensitivity points / tradeoff points) and
hand their findings back to `/drivers` (`Status`) and `/add`.

## 1. Tactics-based analysis

Use the per-attribute **tactic taxonomies** (`references/tactics-catalog.md`) as an interview /
questionnaire. For each relevant tactic ask:

- Is this tactic used in the architecture? **Where** (which element / decision)?
- How well is it implemented — fully, partially, by a framework, ad hoc?
- If it is **not** used, is that a deliberate, safe choice (a non-risk with a stated
  assumption) or a gap (a risk)?

Fast — an hour per attribute — and it surfaces the "we never considered failure detection at
all" class of problem. Record each answer; the gaps are the output.

## 2. Reflective questions

The architect turns the analysis inward, before claiming an iteration goal is met. Generic
prompts, made specific to the iteration's drivers:

- Which driver does each element I just added serve? Any element that serves none?
- For each `(H,H)` / `(H,M)` scenario: name the elements and decisions that achieve its
  response measure. Can I defend the number?
- What did I decide *not* to do, and what assumption makes that safe?
- What is the single decision most likely to be wrong here, and what would tell me sooner?
- Which decisions are now expensive to reverse? Are they the ones I'm most confident in?

If a question has no good answer, that is a backlog item, not a "done".

## 3. Scenario-based design review

A short (½–1 day) peer review, lighter than ATAM: no external evaluators, no stakeholder
brainstorming round.

1. The architect presents the drivers (utility tree) and the current structures.
2. Reviewers pick the top scenarios (the `★` and `(H,M)` leaves, plus any growth/exploratory
   scenario they're worried about).
3. For each scenario the group walks the architecture, asks the tactics-based questions, and
   records risks / non-risks / sensitivity points / tradeoff points.
4. Cluster the risks into themes; each theme maps to a business goal and gets a recommended
   action (an ADD iteration, a spike, a monitoring gap to close).

Output: the registers appended to `atam-report.md` marked `Lightweight` (see
`references/atam-method.md` → *Lightweight Architecture Evaluation*), or an inline note in the
ADD session log.

## When to escalate to a full ATAM

- a lightweight pass keeps surfacing the same systemic risk theme;
- stakeholders disagree about which quality attributes matter most;
- the cost of being wrong is high (safety, regulatory, large committed spend);
- the architecture is being handed between organisations.
