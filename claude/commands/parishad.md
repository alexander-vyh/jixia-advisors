---
description: Convene the Parishad method — source-constrained interpretive council for tradeoffs across roles, duties, sources of authority, or stakeholders. Map authority, identify role obligations, interpret the conflict, and reach the least-violating settlement.
---

# /parishad

Convene the **Parishad** convening method on the user's conflict.

## Source of truth — load the registry, do not improvise the contract

This wrapper is a thin entry point. The method's behavior contract lives in
`jixia/registry.json` under `methods.parishad`. Before doing anything else, read
that entry and obey it. Do **not** restate or hardcode a roster here — the
registry is canonical and this file must never drift from it.

From the `parishad` registry entry, load and honor:

- `entry_gate` — a real tradeoff to resolve across roles, duties, sources of
  authority, or stakeholders. If there is none, the refusal applies.
- `refusal` — redirect when the ask has no real role/source conflict and only
  needs tactical advice or audit.
- `phases` — run them in order; each phase `produces` specific output fields.
- `output_fields` — the exact shape your answer must take.
- `verb_field` (`settlement`) — the single committing output this method exists
  to produce. The council is not done until this field is filled.
- `default_roster_policy` (`historical`) and `practical_selection`.

## Default roster: historical representatives, method-scoped

`parishad` defaults to a **historical** roster. Load **only** this method's
historical representative lenses, lazily and only on invocation, from
`jixia/reps/parishad/` — the role/exemplar reps declared in the `parishad`
`historical_roster` (e.g. mimamsaka hermeneutician, dharmasastra reciter, narada
procedure exemplar). Never load another method's reps.

These are source-constrained interpretive lenses, not impersonations of an actual
council. Per the registry's `practical_selection`, you may add question-relevant
advisors from `claude/agents/` alongside the default historical reps when a
practical lens is useful.

## Roster override — practical-only

If the user asks for a **practical-only** roster (e.g. "/parishad <question>
**practical-only**"), skip the historical representatives and use question-driven
practical advisors from `claude/agents/` instead — loading no reps.

The override changes the **roster only**. The phases, output fields,
`verb_field`, entry gate, and refusal from the registry are unchanged: this stays
an authority-and-role settlement.

## Output

Produce output in the registry's `output_fields` shape for `parishad`:
`authority_map`, `role_obligations`, `conflict_interpretation`, `settlement`.
Map the sources of authority first, surface each role's obligations, interpret
the conflict, and end with the least-violating settlement and its caveats.
