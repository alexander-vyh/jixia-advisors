---
description: Convene the Yushitai (Censorate) method — accountability, audit, remonstrance, and failure-mode detection. Trace the inspection path, collect evidence, assign owner and severity, and recommend a corrective action.
---

# /yushitai

Convene the **Yushitai (Censorate)** convening method on the user's situation.

## Source of truth — load the registry, do not improvise the contract

This wrapper is a thin entry point. The method's behavior contract lives in
`jixia/registry.json` under `methods.yushitai`. Before doing anything else, read
that entry and obey it. Do **not** restate or hardcode a roster here — the
registry is canonical and this file must never drift from it.

From the `yushitai` registry entry, load and honor:

- `entry_gate` — a need for accountability, audit, remonstrance, or failure-mode
  detection. If there is none, the refusal applies.
- `refusal` — redirect when the ask needs open-ended ideation or balanced
  synthesis rather than inspection and accountability.
- `phases` — run them in order; each phase `produces` specific output fields.
- `output_fields` — the exact shape your answer must take.
- `verb_field` (`corrective_action`) — the single committing output this method
  exists to produce. The inspection is not done until this field is filled.
- `default_roster_policy` (`historical`) and `practical_selection`.

## Default roster: historical representatives, method-scoped

`yushitai` defaults to a **historical** roster. Load **only** this method's
historical representative lenses, lazily and only on invocation, from
`jixia/reps/yushitai/` — the role/exemplar reps declared in the `yushitai`
`historical_roster` (e.g. investigating censor, circuit-inspection censor,
discipline-impeachment censor). Never load another method's reps.

These are source-backed inspection lenses, not impersonations of the imperial
Censorate. Per the registry's `practical_selection`, you may add
question-relevant advisors from `claude/agents/` alongside the default historical
reps when a practical lens is useful.

## Roster override — practical-only

If the user asks for a **practical-only** roster (e.g. "/yushitai <question>
**practical-only**"), skip the historical representatives and use question-driven
practical advisors from `claude/agents/` instead — loading no reps.

The override changes the **roster only**. The phases, output fields,
`verb_field`, entry gate, and refusal from the registry are unchanged: this stays
an inspection-and-accountability pass that ends in a corrective action.

## Output

Produce output in the registry's `output_fields` shape for `yushitai`:
`findings`, `evidence_path`, `owner`, `severity`, `corrective_action`. Trace the
inspection path, ground each finding in evidence, assign an accountable owner and
severity, and end with a corrective action.
