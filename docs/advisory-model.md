# Advisory Model

`jixia-advisors` is named for Jixia, the Warring States Qi intellectual
community where rulers supported thinkers from multiple traditions near power.
In this project, Jixia means an adaptive advisory forum. It does not imply a
single doctrine, a fixed roster, or a rule that every question deserves a large
council.

The default use case is everyday counsel. A normal prompt should be able to use
one advisor, or one advisor plus a counter-lens, without turning routine work
into a ceremony. Broader questions can call three to five advisors. Ambiguous or
high-stakes work can use a Seven Sages-style mode with up to seven selected
views from the larger pool.

## Convening Models

- **Jixia:** default everyday mode. Triage the question, select the smallest
  useful advisor mix, add a counter-lens only when it changes the answer, and
  synthesize one practical next action.
- **Seven Sages:** bounded breadth mode. Use up to seven selected views to
  produce compact principles, compare tensions, and converge on short counsel.
- **Areopagus:** adjudicative review mode. Gate jurisdiction, frame the case,
  classify evidence and harm, then return a verdict, remedy, or remand.
- **Junto:** mutual-improvement mode. Turn the topic into prepared queries,
  truth-seeking discussion, experiments, commitments, and follow-up checks.
- **Parishad:** interpretive stakeholder mode. Map sources of authority, roles,
  duties, conflicts, and the least-violating settlement.
- **Yushitai:** inspection and accountability mode. Trace evidence paths,
  identify misconduct or control gaps, assign severity, and recommend correction
  or escalation.

These names are labels for operating patterns, not claims of direct historical
continuity. They should help the user choose the shape of advice needed for the
work in front of them. Source packets and representative-limit notes for the
optional historical lenses live in
[historical-council-sources/README.md](historical-council-sources/README.md).

The method layer should fail if it only swaps advisor backgrounds while keeping
the same behavior. Each method needs its own entry gate, process phases, output
shape, and refusal or redirect condition.

## Benchmarking

The modes should be benchmarked against real work before they become defaults.
Benchmarking is optional and informs which modes to reach for, not whether to keep
them — the modes are kept for their intrinsic value regardless of measured payoff.
Useful comparisons:

- Single advisor vs one advisor plus counter-lens for everyday choices.
- Three to five selected advisors vs Seven Sages-style synthesis for ambiguous
  planning.
- Areopagus or Yushitai-style critique vs generic multi-agent review for
  high-stakes decisions.
- Junto-style counsel vs single-agent coaching for personal systems and habits.

Score outputs on usefulness, actionability, error catch rate, novelty, cost,
latency, and whether the result changed the next action. The expected winning
pattern is not always more agents. The likely strongest pattern is the smallest
set of independent, relevant perspectives that improves the work.
