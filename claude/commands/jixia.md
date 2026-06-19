---
description: Convene the Jixia Academy method — everyday counsel with a right-sized mix of practical advisor lenses. Triage the question, select the smallest useful set of advisors, add a counter-lens only when it earns its place, and synthesize one practical next action.
---

# /jixia

Convene the **Jixia Academy** convening method on the user's question.

## Source of truth — load the registry, do not improvise the contract

This wrapper is a thin entry point. The method's behavior contract lives in
`jixia/registry.json` under `methods.jixia`. Before doing anything else, read
that entry and obey it. Do **not** restate or hardcode a roster here — the
registry is canonical and this file must never drift from it.

From the `jixia` registry entry, load and honor:

- `entry_gate` — the condition under which this method applies.
- `refusal` — when to redirect instead of answering. If the prompt matches the
  refusal condition, name the better-fit method and stop. Do not force-fit.
- `phases` — run them in order; each phase `produces` specific output fields.
- `output_fields` — the exact shape your answer must take.
- `verb_field` (`next_action`) — the single committing output this method exists
  to produce. The answer is not done until this field is filled.
- `default_roster_policy` (`practical`) and `practical_selection` — how to pick
  the roster.

## Default roster: practical, question-driven

`jixia` defaults to a **practical** roster. Per the registry's
`practical_selection`, triage the question and select the smallest useful mix of
advisors from `claude/agents/` by relevance, adding a counter-lens only when it
materially improves the answer. Do **not** convene historical representatives by
default.

## Roster override — explicit historical activation

If the user explicitly asks for historical representatives (e.g. "jixia **with
historical representatives**", "historical roster", or names a specific
representative id), additionally load **only** this method's historical lenses
from `jixia/reps/jixia/` — never another method's reps. Load them lazily, only on
this invocation.

The override changes the **roster only**. The phases, output fields,
`verb_field`, entry gate, and refusal from the registry are unchanged.

## Output

Produce output in the registry's `output_fields` shape for `jixia`:
`diagnosis`, `selected_lenses`, `dissent`, `next_action`. Surface genuine
dissent between lenses rather than smoothing it away, and end with a concrete
`next_action`.
