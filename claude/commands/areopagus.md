---
description: Convene the Areopagus method — constrained adjudicative review of a consequential decision before action. Gate jurisdiction, frame the case, classify admissible concerns, then issue a verdict and remedy-or-remand.
---

# /areopagus

Convene the **Areopagus** convening method on the user's decision.

## Source of truth — load the registry, do not improvise the contract

This wrapper is a thin entry point. The method's behavior contract lives in
`jixia/registry.json` under `methods.areopagus`. Before doing anything else, read
that entry and obey it. Do **not** restate or hardcode a roster here — the
registry is canonical and this file must never drift from it.

From the `areopagus` registry entry, load and honor:

- `entry_gate` — a consequential decision to review before action. If there is
  none, the refusal applies.
- `refusal` — refuse routine brainstorming or advice when there is no
  consequential decision to adjudicate. Redirect to a better-fit method.
- `phases` — run them in order; each phase `produces` specific output fields.
- `output_fields` — the exact shape your answer must take.
- `verb_field` (`verdict`) — the single committing output this method exists to
  produce. The review is not done until this field is filled.
- `default_roster_policy` (`historical`) and `practical_selection`.

## Default roster: historical representatives, method-scoped

`areopagus` defaults to a **historical** roster. Load **only** this method's
historical representative lenses, lazily and only on invocation, from
`jixia/reps/areopagus/` — the role/exemplar reps declared in the `areopagus`
`historical_roster` (e.g. former-archon councillor, homicide juror, power
limiter). Never load Jixia, Seven Sages, Junto, Parishad, or Yushitai reps.

These are source-backed review lenses, not impersonations of the historical
council. Per the registry's `practical_selection`, you may add question-relevant
advisors from `claude/agents/` alongside the default historical reps when a
practical lens is useful.

## Roster override — practical-only

If the user asks for a **practical-only** roster (e.g. "/areopagus <question>
**practical-only**"), skip the historical representatives and use question-driven
practical advisors from `claude/agents/` instead — loading no reps.

The override changes the **roster only**. The phases, output fields,
`verb_field`, entry gate, and refusal from the registry are unchanged: this stays
an adjudicative review that ends in a verdict.

## Output

Produce output in the registry's `output_fields` shape for `areopagus`:
`case_record`, `admissible_concerns`, `verdict`, `remedy_or_remand`. Gate
jurisdiction first, classify concerns by admissibility, and end with a verdict
plus an explicit remedy or remand.
