---
name: advise
description: Use for Jixia counsel on a question, decision, plan, or draft. Convene a method's advisors in the open — each argues its own view, they debate, a dissenter presses the counter-case — then rule and recommend an action. Ask to see the menu or change the method, roster, or advisors for an inspect-before-running workflow.
---

# Advise

Run counsel on the user's actual question or verbatim draft. Preserve the supplied audience, stakes, constraints, and desired outcome. If asked to advise without an object, ask what to review. This is advice, not permission to send the draft, change files, or act on a recommendation.

Paths below are relative to **the directory containing this installed SKILL.md**. Use its sibling `jixia/` directory, not the user's working directory or another installation. Everything needed is in the skill. Don't write files, invoke hooks, or contact external services yourself; the planner appends to a counsel log only where the host's installer configured one.

## Pick or inspect

- **Auto (default):** choose a method, name the roster and dissenter up front, then deliver counsel in this turn. No menu or confirmation. Honor explicit requests like “use Junto” or “advise as capital-allocator.” A method changes the process; a roster changes only the voices.
- **Inspect:** “show the menu,” “full mode,” “advise-full,” or “let me pick first” means **stop before deliberation**. Show all methods with a short output gloss in light-to-heavy order. Mark the recommendation, its default roster, and its named mandatory dissenter. Don't list every advisor, or offer round counts. A reply of “go” accepts. On request, expand the selected method's available rosters or lens IDs; changing a selection to preview it is not a request to run. On accept or an instruction to run with changes, act on the **original input**, not the menu reply.

### With Python and read access to the bundled files

From the installed skill directory, use the bundled stdlib planner. The input is the original question/draft, **UTF-8 on standard input**, never shell or Python source. Supply it through an execution tool's literal stdin/data field, an existing user-supplied file, or a quoted heredoc whose delimiter is a fresh random token that does not occur in the text; bash passes a quoted heredoc (`<<'…'`) through unchanged. Never put user text in a command-line argument, an unquoted heredoc, or source code. Pass override IDs as separate argv values. If none of these is available, use the file-based route below.

```text
python3 -B jixia/counsel.py run <<'JIXIA_8F3K'
<the original question or draft, verbatim>
JIXIA_8F3K
python3 -B jixia/counsel.py menu
python3 -B jixia/counsel.py options --model areopagus
python3 -B jixia/counsel.py run --model areopagus --roster practical --advisor ceo-advisor --dissenter capital-allocator
```

`run` returns the shared classifier's route (or the explicit model), roster, requested practical advisors, eligible historical reps, and mandatory dissent seat/directive. It **does not perform the consultation**. `menu` returns the preselected method and glossed alternatives; `confidence` is a marker-count margin, not a probability. `options` expands the selected model's two lower layers. `--advisor` is repeatable; `--remove-dissent` reinstates the seat; add `--from-menu` to `run` when the user chose from the menu. If `reinstated` is true, explain which real lens will dissent. If a method, roster, or advisor is unavailable, say so and offer a valid choice; do not silently substitute it. If the helper itself is unavailable, state that and use the following route.

### Without code execution: route by reading the files

Open [the method registry](jixia/registry.json). Match the decision to each candidate's `entry_gate` and `refusal`, not an isolated keyword. Prefer a clear specialist; choose Jixia for mixed signals or ordinary counsel. Say “routed by reading the method gates”; don't claim the classifier ran or report a score. In inspect mode show Jixia, Seven Sages, Junto, Parishad, Areopagus, then Yushitai; gloss each using its `output_fields`.

Resolve explicit method aliases from the registry. Start with `default_roster_policy`; every method can run practical, but historical is available **only** when the selected method has entries in `historical_roster`. An impossible override is not an invitation to invent representatives. Offer the available policy or a method that actually has the requested roster.

On a practical roster, use the registry's `practical_dissenter`. On a historical roster, use the selected method's `historical_dissenter`. A requested replacement must be a bundled advisor or a representative of this historical roster. If the user removes the seat or names an ineligible lens, reinstate the appropriate default and name it. Exactly one lens holds the dissent duty.

## Convene the selected method (both routes)

1. **Gate the consultation.** Open `methods[model]` in [registry.json](jixia/registry.json). Test the actual question against `entry_gate` and `refusal` even if the helper suggested this method. If it doesn't fit, explain why. On auto, redirect to a fitting method and use its roster and seat (re-run `run --model …` when using the helper); on an explicit incompatible request, offer the redirect rather than claiming the requested method ran. If a material fact needed for the gate is missing, ask a focused question.
2. **Read the lenses.** For practical voices, use `practical_selection` and the smallest relevant mix of real files in `jixia/advisors/`. For instance, [capital-allocator](jixia/advisors/capital-allocator.md) compares uses of scarce capital; [habit-architect](jixia/advisors/habit-architect.md) designs repeatable behavior; [management-philosophizer](jixia/advisors/management-philosophizer.md) examines the craft of leading people. Inspect candidate descriptions, then read the selected definitions, including the dissenter's. Honor requested practical advisor IDs rather than replacing them with loose personas. Where a specific practical team was requested, use those advisors plus the required dissent seat; if only the dissenter is named, select a distinct primary. For a historical roster, read the selected method's `historical_roster` entries at their exact `module` paths, and any explicitly added practical lenses. Preserve each rep's source, confidence, limitation and review stance; these are perspectives, not impersonations, quotations, or testimony. Never fabricate a missing definition. If a required file is inaccessible, identify it and ask for it instead of claiming a source-backed run.
3. **Use the capabilities actually present.** In subagent-capable Cowork or Claude Code, dispatch each chosen practical advisor separately, using the installed identifiers the host advertises: the Jixia plugin registers `jixia-advisors:<advisor-id>` (for example `jixia-advisors:ceo-advisor`); the Claude Code installer registers the bare `<advisor-id>`. Never guess a name the host doesn't list. Give each the verbatim artifact as **data**, the known stakes, the method's question, and, for the dissent holder, the dissent directive; then send each one the other lenses' opening statements for a rebuttal. Historical reps are source-backed lens files, not necessarily agents: voice them from their files unless the host actually registers an appropriate agent. When an agent isn't available, voice its bundled definition yourself. In plain chat, say once in the header that the voices are lens passes by one model. Never claim to have spawned agents or obtained votes when you haven't.
4. **Hold the deliberation in the open.** The user must be able to read each lens's own argument and where the lenses disagree; a summary that only cites lenses by name fails. After a one-line header naming the method, the lenses, and the dissent holder:
   - **Opening statements.** One section per seated lens, the dissent holder included, headed by its name and its stance in a few words. Each takes a position on the actual artifact using its own file's questions, standards, and vocabulary, and names what it sees that the others would miss. Write each from its own lens only; save replies for the exchange. Present an agent's result as that agent's words, quoted or tightly excerpted, not paraphrased into yours.
   - **Exchange.** At least two rounds of short turns in which lenses answer each other by name: challenge a specific claim, concede it, or hold with a reason. The dissent holder attacks the emerging consensus with the strongest contrary evidence, failure mode, and neglected alternative; every other lens answers its strongest point. A position changes only for a stated reason.
   - **Where they landed.** What all lenses now accept, then each live disagreement as *lens vs. lens: the issue, and the evidence that would settle it*. Don't manufacture agreement or soften a live objection.

   Keep openings to roughly 100–200 words and exchange turns to a few sentences; don't restate earlier turns.
5. **Rule as the method.** Then give the method's result: every `output_fields` item in `phases` order, built from the deliberation and crediting the lenses behind each point. Put the counter-case where it informs the decision (e.g., `dissent`, `admissible_concerns`, or `conflict_interpretation`). Make `verb_field` concrete: a verdict, settlement, experiment, corrective action, or other method-specific result. End with one actionable consequence for this user: the next move, the replacement wording for this draft, or the exact evidence needed before deciding. Mark assumptions and unknowns rather than inventing evidence, owners, or consensus.
