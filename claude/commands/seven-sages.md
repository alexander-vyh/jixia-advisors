---
description: Convene the Seven Sages method — bounded breadth on an ambiguous planning question. Cap the active voices at seven, gather compact maxims, map convergence and divergence, and converge on one distilled counsel.
---

# /seven-sages

Convene the **Seven Sages** convening method on the user's question.

## Source of truth — load the registry, do not improvise the contract

This wrapper is a thin entry point. The method's behavior contract lives in
`jixia/registry.json` under `methods.seven-sages`. Before doing anything else,
read that entry and obey it. Do **not** restate or hardcode a roster here — the
registry is canonical and this file must never drift from it.

From the `seven-sages` registry entry, load and honor:

- `entry_gate` — the condition under which this method applies.
- `refusal` — when to redirect instead of answering. If the prompt matches the
  refusal condition, name the better-fit method and stop.
- `phases` — run them in order; each phase `produces` specific output fields.
- `output_fields` — the exact shape your answer must take.
- `verb_field` (`distilled_counsel`) — the single committing output this method
  exists to produce. The answer is not done until this field is filled.
- `default_roster_policy` (`practical`) and `practical_selection` — how to pick
  the roster.

## Default roster: practical, question-driven, capped at seven

`seven-sages` defaults to a **practical** roster. Per the registry's
`practical_selection`, cap active voices at seven and draw the smallest useful
set from `claude/agents/` by relevance to the planning question. Do **not**
convene historical representatives by default.

## Roster override — explicit historical activation

If the user explicitly asks for historical representatives (e.g. "seven-sages
**with historical representatives**", "historical roster", or names a specific
representative id), additionally load **only** this method's historical lenses
from `jixia/reps/seven-sages/` — never Jixia, Junto, Parishad, Areopagus, or
Yushitai representatives. Load them lazily, only on this invocation, and keep the
seven-voice cap.

The override changes the **roster only**. The phases, output fields,
`verb_field`, entry gate, and refusal from the registry are unchanged.

## Output

Produce output in the registry's `output_fields` shape for `seven-sages`:
`perspectives`, `convergence_divergence_map`, `distilled_counsel`. Keep each
perspective terse, make the convergence/divergence map honest, and end with one
distilled counsel statement.
