# UX Surface: `/advise-full` Terminal Menu Design

Agent: 02-ux-surface (UI Design Critic)
Date: 2026-06-22

## Findings

### Model Inventory (from registry.json)

These are the six convening models, their entry gates, output structures, and
default rosters. The glosses below are derived from the registry's `entry_gate`
and `verb_field` fields — they describe what the model *does* structurally, not
what it is culturally.

| Model | Entry gate (when to use) | Output shape | Roster default |
|---|---|---|---|
| **jixia** | everyday counsel, right-sized lenses | diagnosis + dissent + next_action | practical |
| **seven-sages** | ambiguous planning question, bounded breadth | perspectives + convergence map + distilled counsel | practical |
| **areopagus** | consequential decision, pre-action review | case record + verdict + remedy | historical |
| **junto** | self-improvement, operating cadence | queries + observations + commitment + follow-up | practical |
| **parishad** | roles/duties/authority conflict | authority map + obligations + settlement | historical |
| **yushitai** | audit, accountability, failure-mode detection | findings + evidence + owner + severity + corrective action | historical |

---

### Design Constraints

**Surface:** GitHub-flavored markdown rendered in a terminal (Claude Code CLI).
No color guarantees beyond GFM bold/italic/code. No GUI. Output is conversational
— it appears inline in a chat-style terminal stream.

**User mental model:** Most users will not know what "areopagus" or "parishad"
means. The name is a flavoring detail; the *output structure* is what differentiates
models and must be legible in the gloss.

**Gloss requirement:** Each model needs a ~5-word plain description of what it
*produces*, not what it is historically. "Seven wise voices" is flavor; "seven
angles + one synthesis" is structure.

**Recommended default:** The classifier's auto-pick must be unmissable. A user
scanning in under 2 seconds must see: (1) there is a recommendation, (2) which
model it is, (3) what they'll get. Everything else is subordinate.

**Compactness:** Must fit in a single terminal screen (~40 lines at typical font
sizes) without scrolling. A "full" variant can be slightly longer but must not
feel like a reference doc.

---

### Mockup A: Recommended-Default-Prominent (tight)

This variant foregrounds the recommendation, compresses alternatives into a
secondary table. Optimized for the case where the user mostly takes the default.

```
Convening model: **areopagus** (recommended)
> Adjudicative review — case record, verdict, remedy.

Other models:

  jixia         everyday counsel — diagnosis, dissent, next action
  seven-sages   breadth on ambiguity — 7 angles + convergence map
  junto         improvement practice — commitment + follow-up
  parishad      authority conflict — obligation map + settlement
  yushitai      audit/accountability — findings, owner, severity, fix

Roster: **historical** (default for areopagus) | or: practical

Reply with a model name, or press Enter to use areopagus.
```

**Critique of Mockup A:**

Strengths:
- The recommendation is the first thing read. Bold + "(recommended)" is a double
  signal — either one would survive; both together make it unmissable.
- The blockquote under the recommendation gives the output gloss without competing
  for hierarchy with the model name.
- The alternatives table uses consistent left-alignment; the em-dash separator
  reads faster than colons (less visual noise) and the 5-word glosses stay parallel.
- The roster line is compact: shows the default, offers the override, does not
  demand a decision if the user doesn't care.
- Total: 12 lines. Fits in any terminal without scrolling.

Weaknesses:
- The alternatives section has no visual weight to help the eye distinguish
  "names" from "glosses". A user skimming by model name must track across the
  whitespace. Monospace alignment helps but is not guaranteed in proportional
  terminals.
- "Reply with a model name, or press Enter to use areopagus" is a prompt-style
  close that works well for interactive skills but may look odd if the skill auto-
  presents and awaits input differently.
- No signal for the practical/historical distinction on alternatives — the roster
  line is siloed at the bottom and requires reading to understand it applies to all.

---

### Mockup B: Full-Expansion with Roster Column

This variant adds a roster column and uses a proper GFM table. Useful when the
user wants to compare models before choosing. Slightly longer but still compact.

```
## Choose a convening model

| Model | What you get | Roster |
|---|---|---|
| **areopagus** ★ | case record, verdict, remedy | historical |
| jixia | diagnosis, dissent, next action | practical |
| seven-sages | 7 angles, convergence map, counsel | practical |
| junto | commitment, observations, follow-up | practical |
| parishad | obligation map, authority settlement | historical |
| yushitai | findings, owner, severity, corrective action | historical |

★ Recommended by classifier. Reply with a model name to override, or continue
to accept **areopagus**.

**Roster** — *historical*: source-backed period reps + optional practical advisors.
*practical*: domain advisors only, no historical reps.
```

**Critique of Mockup B:**

Strengths:
- The GFM table renders well in Claude Code's terminal output — columns align,
  borders are visible. The star (★) in the model name column is immediately
  readable at a glance.
- The roster column answers a question that users often have but won't think to
  ask: "will I get historical figures or contemporary advisor personas?"
- The footnote for ★ is below the table, not inline, so it does not clutter the
  primary reading pass.
- The roster legend at the bottom gives meaning to the "historical/practical"
  labels without forcing the user to know the vocabulary up front.

Weaknesses:
- GFM table rendering in terminals is not guaranteed for all Claude Code surfaces.
  If the markdown processor is absent, the pipe-table syntax is noisy.
- The "★ Recommended" footnote pattern is a common convention but requires two
  reading passes: one to note ★, one to find what ★ means. The footnote is only
  3 lines below but the eye does not always track down in a scanned table.
- "continue to accept areopagus" is mildly ambiguous — does "continue" mean
  send nothing, type "yes", or just proceed with the next prompt?
- At ~18 lines, this is the longest variant. Still within a single screen but
  starts to feel reference-doc-adjacent.

---

### Mockup C: Hybrid — Recommended Foregrounded, Alternatives Compressed

This is the recommended design. It combines the clarity of Mockup A's hierarchy
with the roster signal from Mockup B, while staying maximally compact.

```
**Convening model (recommended): areopagus**
Adjudicative review — produces a case record, verdict, and remedy.
Roster: historical reps (archon, juror, power-limiter) + practical advisors.

Alternatives — reply with a name to override:

  **jixia**        everyday counsel           practical advisors
  **seven-sages**  7 angles + counsel         practical advisors
  **junto**        commitment + follow-up     practical advisors
  **parishad**     authority settlement       historical reps
  **yushitai**     audit + corrective action  historical reps

Or specify a roster: `areopagus practical` / `junto historical`
```

**Critique of Mockup C:**

Strengths:
- Hierarchy is aggressive and unambiguous. The recommended model gets three full
  lines: name (bold), gloss, roster. Everything else gets one line each. The visual
  weight matches the information weight.
- The "Alternatives" label with a horizontal separator (em-dashes or blank lines)
  makes the structural split immediately readable: "above the line = what was
  chosen for you; below the line = what else exists."
- Roster signal is embedded in the alternatives table as a second column, not
  relegated to a footnote. The user can see at a glance that jixia/seven-sages/junto
  use practical advisors and the remaining three use historical reps.
- The last line offers the override syntax explicitly, which is self-documenting
  — users don't need to guess "do I type the name? the number? press a key?"
- Total: 14 lines. Compact.

Weaknesses:
- The three-line block for the recommended model slightly breaks the visual rhythm
  of "everything else is one line." This is the intended design, but some users may
  find the asymmetry jarring.
- Column alignment for the alternatives table depends on monospace rendering. In
  a proportional font (unlikely in CLI but possible in web surfaces), the glosses
  and roster labels will not align. Padding with enough spaces to survive
  proportional rendering would require fixed-width columns that look odd in
  markdown source.
- "Or specify a roster" with inline code examples is clean, but the backtick code
  spans may not render in all surfaces. Plain prose ("Or add 'practical' or
  'historical' after the model name") is a safer fallback.

---

### Typography Notes for Terminal GFM

These apply to all three mockups and to any final design:

1. **Bold for the recommendation, not for all model names.** Bold is a semantic
   signal here — reserve it for "the one thing you should look at." If all model
   names are bold, none are.

2. **Gloss punctuation.** Em-dash (—) reads cleaner than colon as a name/gloss
   separator in a compact list. "areopagus — verdict + remedy" scans faster than
   "areopagus: verdict and remedy."

3. **Output field names should be nouns, not verbs.** "case record, verdict,
   remedy" is better than "records a case, issues a verdict, recommends a remedy"
   — the noun form is more scannable and communicates the artifact, not the process.

4. **Roster vocabulary.** "practical advisors" and "historical reps" are the two
   values. These should be stated consistently, not as "practical/historical" bare
   adjectives, which mean nothing to a first-time user.

5. **The "(recommended)" label should be adjacent to the model name, not at the
   end of a line.** Eye-tracking in a left-to-right terminal favors signals near
   the primary anchor (the name). "areopagus (recommended)" is better than
   "areopagus ... recommended ★."

6. **Avoid numbering models (1-6) unless the interaction supports numeric input.**
   Numbers imply "type 1 to select." If the skill awaits a model name, letters or
   the name itself is the right affordance. Numbers create a mismatch between what
   the label implies and what the skill accepts.

---

### Recommendation

**Use Mockup C as the base design.** It is the clearest embodiment of aggressive
hierarchy for small surfaces: one primary block (the recommendation) gets
disproportionate visual space, everything else is compressed. The roster column
in the alternatives is the key addition over Mockup A — it surfaces the practical/
historical distinction where the user can see it, not in a separate legend line.

The one revision to Mockup C before implementation: replace the backtick code
spans in the override syntax with plain prose, to avoid dependency on code-span
rendering. E.g.:

```
To override: reply with a model name — e.g. "yushitai" or "junto practical"
```

This is a terminal-markdown safety measure, not a hierarchy change.
