---
description: Convene the Junto method — mutual-improvement practice for self-improvement, operating cadence, or civic/practical improvement. Prepare queries, keep debate truth-seeking, and commit to an experiment with a follow-up check.
---

# /junto

Convene the **Junto** convening method on the user's question.

## Source of truth — load the registry, do not improvise the contract

This wrapper is a thin entry point. The method's behavior contract lives in
`jixia/registry.json` under `methods.junto`. Before doing anything else, read
that entry and obey it. Do **not** restate or hardcode a roster here — the
registry is canonical and this file must never drift from it.

From the `junto` registry entry, load and honor:

- `entry_gate` — the condition under which this method applies.
- `refusal` — when to redirect instead of answering. If the prompt matches the
  refusal condition, name the better-fit method and stop.
- `phases` — run them in order; each phase `produces` specific output fields.
- `output_fields` — the exact shape your answer must take.
- `verb_field` (`experiment_or_commitment`) — the single committing output this
  method exists to produce. The answer is not done until this field is filled.
- `default_roster_policy` (`practical`) and `practical_selection` — how to pick
  the roster.

## Default roster: practical, question-driven

`junto` defaults to a **practical** roster. Per the registry's
`practical_selection`, select advisors from `claude/agents/` that aid
improvement practice, mutual aid, and civic artifact production. Do **not**
convene historical representatives by default.

## Roster override — explicit historical activation

If the user explicitly asks for historical representatives (e.g. "junto **with
historical representatives**", "historical roster", or names a specific
representative id), additionally load **only** this method's historical lenses
from `jixia/reps/junto/` — never another method's reps. Load them lazily, only on
this invocation.

The override changes the **roster only**. The phases, output fields,
`verb_field`, entry gate, and refusal from the registry are unchanged.

## Output

Produce output in the registry's `output_fields` shape for `junto`: `queries`,
`observations`, `experiment_or_commitment`, `followup_check`. Keep debate
truth-seeking rather than victory-seeking, and end with a concrete experiment or
commitment plus the next check-in.
