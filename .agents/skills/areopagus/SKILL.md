---
name: areopagus
description: Use to convene the areopagus method — constrained adjudicative review of a consequential decision before action. Trigger when the user asks to "run areopagus", "convene the areopagus", or wants a case record, admissible concerns, a verdict, and a remedy-or-remand. Routes to the shared registry contract, not a hand-maintained roster.
---

# Areopagus (convening method)

This skill makes the **areopagus** convening method triggerable in Codex. It
routes to the same registry-backed contract the Claude `/areopagus` command
uses — it does not define its own roster or output shape.

## Source of truth

The method contract lives in `jixia/registry.json` under `methods.areopagus`.
Read that entry and obey it. Do **not** hardcode a roster here; the registry is
canonical. The Claude wrapper `claude/commands/areopagus.md` documents the same
routing — keep behavior identical across surfaces.

Load and honor from the `areopagus` entry: `entry_gate` (a consequential
decision), `refusal` (refuse routine brainstorming with no decision to
adjudicate), `phases` (run in order), `output_fields`, `verb_field` (`verdict`),
`default_roster_policy` (`historical`), and `practical_selection`.

## Roster

Default is **historical**: load **only** this method's reps from
`jixia/reps/areopagus/` (the `historical_roster` declared in the registry —
former-archon councillor, homicide juror, power limiter), lazily and
method-scoped. Never load another method's reps. These are source-backed review
lenses, not impersonations of the historical council. You may add
question-relevant `claude/agents/` advisors when a practical lens helps.

**Override — practical-only:** if the user asks for a practical-only roster,
skip the historical reps and use question-driven `claude/agents/` advisors
instead, loading no reps. The override changes the roster only; the registry's
phases, fields, verb field, gate, and refusal are unchanged — this stays an
adjudicative review ending in a verdict.

## Output

Use the registry `output_fields` for `areopagus`: `case_record`,
`admissible_concerns`, `verdict`, `remedy_or_remand`.
