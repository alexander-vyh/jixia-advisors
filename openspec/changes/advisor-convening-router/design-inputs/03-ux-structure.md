# /advise-full — Information Structure

**Agent:** information-architect
**Date:** 2026-06-22
**Task:** Recommended decomposition for a two-axis (model × roster) menu with sub-choice (specific agents)

---

## Findings

### 1. The Decomposition Decision — Model First, Roster Collapsed

**Recommended structure: model-first, roster collapsed behind an expansion trigger.**

Do NOT present a 2D grid. Do NOT present model and roster as co-equal axes at the same level.

**Rationale — four structural facts drive this:**

1. **The registry already encodes defaults.** `default_roster_policy` in `registry.json` is set per model: `jixia`, `seven-sages`, `junto` → `practical`; `areopagus`, `parishad`, `yushitai` → `historical`. The orthogonality is theoretical (any model *can* take either roster), but the registry has already made a strong judgment about the natural pairing. Surfacing roster as a peer axis fights the registry's own opinion.

2. **The roster axis is not symmetric in weight.** Practical roster = 20 agents (question-driven triage from `claude/agents/`). Historical roster = 3–4 pre-specified representatives per model. The practical roster is the everyday path; historical is the power-user exception. Presenting them as equals misrepresents the frequency distribution.

3. **The cognitive load of a 2D first question is too high.** Showing six models AND two roster options simultaneously is 12 cells, plus the sub-choice of specific agents — well past the 7±2 working-memory limit for a decision the user wants to make in under 5 seconds. Progressive disclosure: collapse the smaller axis behind the choice of the larger.

4. **The research finding against judge-decides modes.** The salvaged synthesis specifically cautions against front-loading `areopagus`-style verdict structures. If model is chosen first, the user reads the entry gate and self-selects appropriately. If roster is chosen first, this safety is lost — a user picking "historical" could get pushed toward areopagus's judge mode before understanding they want it.

---

### 2. The Three-Layer Progressive Disclosure Structure

```
Layer 0 (classifier short-circuit):
  "Recommended: [Model Name] + [practical|historical] roster"
  → one-line, based on classifier output, accept with Enter or one keystroke
  → skips all of layers 1–3

Layer 1 (model choice — shown if user declines/overrides default):
  6 options, ordered by frequency of use and deliberation weight (see §3)
  → selecting a model REVEALS layer 2 inline, collapsed by default

Layer 2 (roster toggle — collapsed, default pre-selected per registry):
  "[practical ✓] or [historical]"  ← registry default pre-checked
  → expansion trigger: "change roster ↓" or "r" key
  → expanded state shows roster description (1 sentence each)

Layer 3 (agent sub-selection — collapsed, hidden unless user wants it):
  "Using [N] auto-selected agents  [customize ↓]"
  → expansion trigger: explicit "customize" action
  → shown only AFTER model is confirmed; lists agents for that model's roster
```

The key principle: **each layer is only revealed after the prior layer is committed**. A casual user never sees layers 2 or 3. A power user can reach them in two extra keystrokes.

---

### 3. Model Ordering Within Layer 1

Order the six models by **deliberation weight × frequency of use**, lightest first:

| Position | Model | Entry gate (condensed) | Default roster |
|----------|-------|------------------------|----------------|
| 1 | **Jixia Academy** | everyday counsel, right-sized lenses | practical |
| 2 | **Seven Sages** | bounded breadth on ambiguous planning | practical |
| 3 | **Junto** | self-improvement, operating cadence | practical |
| 4 | **Areopagus** | consequential decision before action | historical |
| 5 | **Parishad** | tradeoffs across roles/authority/stakeholders | historical |
| 6 | **Yushitai** | accountability, audit, failure-mode detection | historical |

**Rationale for this order:**
- The practical-roster models (1–3) are higher-frequency, lighter-weight, and produce actionable output (next_action, distilled_counsel, experiment). They belong first.
- The historical-roster models (4–6) are heavier: formal adjudication (verdict), authority settlement, audit findings. They belong later — reachable but not front-loaded, consistent with the research guidance to not push formal debate/judge modes onto casual users.
- Within the practical tier: Jixia (everyday default) first, Seven Sages (bounded breadth) second, Junto (commitment cadence) third — ordered by how often a typical user needs them.
- Within the historical tier: Areopagus (consequential decisions — most likely to be needed) before Parishad (multi-stakeholder treaty) before Yushitai (audit/remonstrance — most specialized).

---

### 4. How the Classifier Default Short-Circuits the Structure

The classifier supplies a `(model, roster)` recommendation. This enables **Layer 0**: the entire structure collapses to a single confirmation line.

```
> Recommend: Areopagus · historical roster  (consequential decision detected)
  [Enter to accept]  [↓ to change model]  [r to change roster]  [a to select agents]
```

Properties this satisfies:
- **A casual user completes the interaction in one keystroke.** The full option space never appears.
- **A power user has explicit expansion triggers** without any hidden menus — every axis is reachable in 1–2 keystrokes from the prompt line.
- **The orthogonality is exploitable.** `[r to change roster]` is always available, even when the default is `historical` — a user who wants Areopagus with a practical roster can get there without navigating a 2D grid.

---

### 5. Roster Axis — When to Expand It

The roster toggle (Layer 2) should surface automatically in exactly one case: **when the classifier is not confident** (no strong model match, or model and roster are both uncertain). In that state, show both axes:

```
> No strong match.  Choose model:  [jixia]  [seven-sages]  [junto]  …
  Roster:  [practical ✓]  [historical]
```

This is the only case where the 2D structure becomes visible — and even then, roster defaults to `practical` (the registry majority) rather than forcing a choice.

---

### 6. Sub-Choice (Specific Agents) — Layer 3 Design

Agent sub-selection belongs in Layer 3 and should remain hidden until explicitly expanded. Key constraints:

- **Only show agents appropriate for the selected model's roster.** Practical roster → 20 agents from `claude/agents/`. Historical roster → 3–4 pre-specified representatives.
- **Never show all 20 agents by default.** Show the classifier's auto-selected subset (e.g., 3–5 agents) with a "customize ↓" expansion.
- **For historical roster:** the roster is pre-specified and small; the expansion shows all 3–4 representatives but does not offer add/remove (the historical rep set is fixed by the model's source documents).
- **For practical roster:** the expansion shows the auto-selected agents with checkboxes, plus a search-to-add for the remaining agents.

---

### 7. What NOT to Build

Per the research synthesis:
- Do NOT build a free-form "N agents debate for K rounds" option — not supported by the literature and not in the six models.
- Do NOT present the roster axis as a first-choice question — this forces a decision whose answer is already encoded in the registry defaults.
- Do NOT front-load the historical-council models. They should be reachable but not the first thing a user sees.
- Do NOT expose agent-level selection before the model is confirmed — selecting agents for Areopagus vs Jixia is completely different; showing agent names before model selection creates false parallelism.

---

### 8. Summary: The Recommended Decomposition in One Paragraph

**Choose model first. Collapse roster to the registry default. Hide agents until model is confirmed. Short-circuit everything with the classifier recommendation.**

A user who accepts the classifier's recommendation never sees the decomposition at all — they interact with a single confirm line. A user who overrides sees six models ordered light-to-heavy (practical first, historical second) with the roster defaulting to the registry's per-model value and appearing as a one-line toggle, not a first-level axis. Agent sub-selection is Layer 3, hidden behind an explicit "customize" expansion and only meaningful after the model is chosen. The full 2D grid (6 × 2 × N) is never shown; the orthogonality is always exploitable via explicit expansion triggers, not a grid.
