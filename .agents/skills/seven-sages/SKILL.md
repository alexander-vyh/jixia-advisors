---
name: seven-sages
description: Use to convene the seven-sages method — bounded breadth on an ambiguous planning question, capped at seven voices. Trigger when the user asks to "run seven-sages", "convene the seven sages", or wants compact perspectives, a convergence/divergence map, and one distilled counsel. Routes to the shared registry contract, not a hand-maintained roster.
---

# Seven Sages (convening method)

This skill makes the **seven-sages** convening method triggerable in Codex. It
routes to the same registry-backed contract the Claude `/seven-sages` command
uses — it does not define its own roster or output shape.

## Source of truth

The method contract lives in `jixia/registry.json` under `methods.seven-sages`.
Read that entry and obey it. Do **not** hardcode a roster here; the registry is
canonical. The Claude wrapper `claude/commands/seven-sages.md` documents the same
routing — keep behavior identical across surfaces.

Load and honor from the `seven-sages` entry: `entry_gate`, `refusal`, `phases`
(run in order), `output_fields`, `verb_field` (`distilled_counsel`),
`default_roster_policy` (`practical`), and `practical_selection`.

## Roster

Default is **practical**: cap active voices at seven and draw the smallest useful
set from `claude/agents/` by relevance to the planning question. No historical
reps by default.

**Override — historical:** if the user explicitly asks for historical
representatives, additionally load **only** `jixia/reps/seven-sages/` lenses,
lazily and method-scoped, keeping the seven-voice cap. The override changes the
roster only; the registry's phases, fields, verb field, gate, and refusal are
unchanged.

## Output

Use the registry `output_fields` for `seven-sages`: `perspectives`,
`convergence_divergence_map`, `distilled_counsel`.
