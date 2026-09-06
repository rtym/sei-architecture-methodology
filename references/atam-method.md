# Reference — Architecture Tradeoff Analysis Method (ATAM)

Source: Kazman, Klein, Clements — *ATAM: Method for Architecture Evaluation*, CMU/SEI-2000-TR-004;
Bass, Clements, Kazman — *Software Architecture in Practice*, ch. on evaluation.

## Purpose

Assess the consequences of architectural decisions in light of quality-attribute requirements.
ATAM does not grade an architecture or produce precise numbers; it **surfaces risks** and shows
where quality attributes **trade off** before those risks become expensive.

## Participants

- **Evaluation team** — ideally outside the project. Roles: team leader, evaluation leader,
  scenario scribe, proceedings scribe, questioner(s).
- **Project decision makers** — sponsor, project manager, lead architect.
- **Architecture stakeholders** — developers, testers, integrators, maintainers, operators,
  users, and owners of interfacing systems (brought in for Phase 2).

## Outputs

- A concise presentation of the architecture.
- Articulated business goals.
- Quality requirements captured as a **utility tree** of prioritised scenarios.
- The set of **architectural approaches / decisions** identified.
- The mapping of approaches to quality attributes, with:
  - **Risks** — decisions that, given the drivers, may cause problems.
  - **Non-risks** — decisions that are safe *under a stated assumption*.
  - **Sensitivity points** — a property of one or more elements that is critical to a particular
    quality-attribute response.
  - **Tradeoff points** — a sensitivity point that affects more than one quality attribute,
    where improving one worsens another.
- **Risk themes** — recurring, related risks that reveal a systemic weakness; each tied to the
  business driver(s) it threatens.

## The four phases and nine steps

### Phase 0 — Partnership and preparation
Team and project leadership agree logistics, scope, the architecture package to be evaluated, the
stakeholder roster for Phase 2, and the schedule.

### Phase 1 — Evaluation (evaluation team + project decision makers, ~1–2 days)

1. **Present the ATAM.** Evaluation leader explains the method, the steps, the techniques
   (utility tree, approach analysis), and the outputs.
2. **Present the business drivers.** A project spokesperson describes: the system's purpose,
   primary functional requirements, business goals and context, major stakeholders, constraints,
   and the quality attributes that matter most.
3. **Present the architecture.** The lead architect presents at an appropriate level of detail:
   technical constraints, other systems it interacts with, and the architectural approaches used
   to meet quality requirements. The team listens for approaches and asks clarifying questions.
4. **Identify architectural approaches.** The team catalogs the styles, patterns, reference
   architectures, and tactics used (e.g. layering, microservices, publish-subscribe, redundancy,
   caching, broker). No analysis yet.
5. **Generate the quality attribute utility tree.** Build a tree:
   `Utility → quality attributes → attribute refinements → concrete scenarios`. Each leaf
   scenario is rated on two axes, usually (H, M, L): **importance to the system** and
   **difficulty / risk to achieve** in the architect's judgement. The tree focuses the rest of
   the evaluation on what matters.
6. **Analyze architectural approaches.** For each high-priority scenario (typically the (H,H) and
   (H,M) leaves): identify the approaches that affect it, ask probing questions, and document
   risks, non-risks, sensitivity points and tradeoff points. Record the reasoning.

### Phase 2 — Evaluation (add the broader stakeholder group, ~2 days)

7. **Brainstorm and prioritize scenarios.** With all stakeholders, brainstorm scenarios —
   **use-case** scenarios (normal use), **growth** scenarios (anticipated change), and
   **exploratory** scenarios (extreme change / stress). Then prioritise by voting (each
   stakeholder gets a vote budget ≈ 30 % of the scenario count). Compare with the Step-5 utility
   tree — convergence is reassuring; divergence is informative.
8. **Analyze architectural approaches.** Repeat Step 6 for the top-voted scenarios from Step 7
   that were not already analysed.
9. **Present results.** The evaluation team recapitulates: approaches, utility tree, scenarios,
   the risks/non-risks/sensitivity/tradeoff registers, and the **risk themes** with their impact
   on business drivers. A written report follows (Phase 3, follow-up).

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

## After ATAM

Risk themes become the input to targeted **ADD** iterations. Update the `architectural-drivers`
register's `Status` column with what ATAM found.
