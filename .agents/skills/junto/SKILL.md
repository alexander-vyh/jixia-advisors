---
name: junto
description: Use to convene the junto method — mutual-improvement practice for self-improvement, operating cadence, or civic/practical improvement. Trigger when the user asks to "run junto", "convene the junto", or wants prepared queries, truth-seeking debate, and an experiment-or-commitment with a follow-up check. Routes to the shared registry contract, not a hand-maintained roster.
---

# Junto (convening method)

This skill makes the **junto** convening method triggerable in Codex. It routes
to the same registry-backed contract the Claude `/junto` command uses — it does
not define its own roster or output shape.

## Source of truth

The method contract lives in `jixia/registry.json` under `methods.junto`. Read
that entry and obey it. Do **not** hardcode a roster here; the registry is
canonical. The Claude wrapper `claude/commands/junto.md` documents the same
routing — keep behavior identical across surfaces.

Load and honor from the `junto` entry: `entry_gate`, `refusal`, `phases` (run in
order), `output_fields`, `verb_field` (`experiment_or_commitment`),
`default_roster_policy` (`practical`), and `practical_selection`.

## Roster

Default is **practical**: select advisors from `claude/agents/` that aid
improvement practice, mutual aid, and civic artifact production. No historical
reps by default.

**Override — historical:** if the user explicitly asks for historical
representatives, additionally load **only** `jixia/reps/junto/` lenses, lazily and
method-scoped. The override changes the roster only; the registry's phases,
fields, verb field, gate, and refusal are unchanged.

## Output

Use the registry `output_fields` for `junto`: `queries`, `observations`,
`experiment_or_commitment`, `followup_check`.
