---
name: yushitai
description: Use to convene the yushitai (Censorate) method — accountability, audit, remonstrance, and failure-mode detection. Trigger when the user asks to "run yushitai on this plan", "convene the censorate", or wants findings, an evidence path, an owner, a severity, and a corrective action. Routes to the shared registry contract, not a hand-maintained roster.
---

# Yushitai / Censorate (convening method)

This skill makes the **yushitai** convening method triggerable in Codex. It
routes to the same registry-backed contract the Claude `/yushitai` command
uses — it does not define its own roster or output shape.

## Source of truth

The method contract lives in `jixia/registry.json` under `methods.yushitai`.
Read that entry and obey it. Do **not** hardcode a roster here; the registry is
canonical. The Claude wrapper `claude/commands/yushitai.md` documents the same
routing — keep behavior identical across surfaces.

Load and honor from the `yushitai` entry: `entry_gate` (a need for
accountability/audit/remonstrance/failure-mode detection), `refusal` (redirect
when the ask needs open-ended ideation or balanced synthesis), `phases` (run in
order), `output_fields`, `verb_field` (`corrective_action`),
`default_roster_policy` (`historical`), and `practical_selection`.

## Roster

Default is **historical**: load **only** this method's reps from
`jixia/reps/yushitai/` (the `historical_roster` declared in the registry —
investigating censor, circuit-inspection censor, discipline-impeachment censor),
lazily and method-scoped. Never load another method's reps. These are
source-backed inspection lenses, not impersonations of the imperial Censorate.
You may add question-relevant `claude/agents/` advisors when a practical lens
helps.

**Override — practical-only:** if the user asks for a practical-only roster,
skip the historical reps and use question-driven `claude/agents/` advisors
instead, loading no reps. The override changes the roster only; the registry's
phases, fields, verb field, gate, and refusal are unchanged — this stays an
inspection-and-accountability pass ending in a corrective action.

## Output

Use the registry `output_fields` for `yushitai`: `findings`, `evidence_path`,
`owner`, `severity`, `corrective_action`.
