---
name: parishad
description: Use to convene the parishad method — source-constrained interpretive council for tradeoffs across roles, duties, sources of authority, or stakeholders. Trigger when the user asks to "run parishad", "convene the parishad", or wants an authority map, role obligations, conflict interpretation, and a settlement. Routes to the shared registry contract, not a hand-maintained roster.
---

# Parishad (convening method)

This skill makes the **parishad** convening method triggerable in Codex. It
routes to the same registry-backed contract the Claude `/parishad` command
uses — it does not define its own roster or output shape.

## Source of truth

The method contract lives in `jixia/registry.json` under `methods.parishad`.
Read that entry and obey it. Do **not** hardcode a roster here; the registry is
canonical. The Claude wrapper `claude/commands/parishad.md` documents the same
routing — keep behavior identical across surfaces.

Load and honor from the `parishad` entry: `entry_gate` (a real role/source
conflict), `refusal` (redirect when there is no real conflict), `phases` (run in
order), `output_fields`, `verb_field` (`settlement`), `default_roster_policy`
(`historical`), and `practical_selection`.

## Roster

Default is **historical**: load **only** this method's reps from
`jixia/reps/parishad/` (the `historical_roster` declared in the registry —
mimamsaka hermeneutician, dharmasastra reciter, narada procedure exemplar),
lazily and method-scoped. Never load another method's reps. These are
source-constrained interpretive lenses, not impersonations of an actual council.
You may add question-relevant `claude/agents/` advisors when a practical lens
helps.

**Override — practical-only:** if the user asks for a practical-only roster,
skip the historical reps and use question-driven `claude/agents/` advisors
instead, loading no reps. The override changes the roster only; the registry's
phases, fields, verb field, gate, and refusal are unchanged — this stays an
authority-and-role settlement.

## Output

Use the registry `output_fields` for `parishad`: `authority_map`,
`role_obligations`, `conflict_interpretation`, `settlement`.
