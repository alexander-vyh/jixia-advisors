---
name: jixia
description: Use to convene the jixia method — Jixia Academy everyday counsel with a right-sized mix of practical advisor lenses. Trigger when the user asks to "run jixia", "convene jixia", or wants triaged general counsel with selected lenses, dissent, and one next action. Routes to the shared registry contract, not a hand-maintained roster.
---

# Jixia (convening method)

This skill makes the **jixia** convening method triggerable in Codex. It routes
to the same registry-backed contract the Claude `/jixia` command uses — it does
not define its own roster or output shape.

## Source of truth

The method contract lives in `jixia/registry.json` under `methods.jixia`. Read
that entry and obey it. Do **not** hardcode a roster here; the registry is
canonical. The Claude wrapper `claude/commands/jixia.md` documents the same
routing — keep behavior identical across surfaces.

Load and honor from the `jixia` entry: `entry_gate`, `refusal`, `phases` (run in
order), `output_fields`, `verb_field` (`next_action`), `default_roster_policy`
(`practical`), and `practical_selection`.

## Roster

Default is **practical**: triage the question and select the smallest useful mix
of advisors from `claude/agents/` by relevance, adding a counter-lens only when
it materially improves the answer. No historical reps by default.

**Override — historical:** if the user explicitly asks for historical
representatives, additionally load **only** `jixia/reps/jixia/` lenses, lazily and
method-scoped. The override changes the roster only; the registry's phases,
fields, verb field, gate, and refusal are unchanged.

## Output

Use the registry `output_fields` for `jixia`: `diagnosis`, `selected_lenses`,
`dissent`, `next_action`.
