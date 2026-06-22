# /advise-full menu — synthesized design (2026-06-22)

## Findings

Synthesis of three independent UX lenses (01-ux-flow, 02-ux-surface, 03-ux-structure).
They converged — no contradictions — on the architecture below.

### Convergent architecture (all three agreed)

1. **Classifier short-circuit is the default.** Turn 1 shows the *conclusion* of the
   menu (what was auto-picked), never the menu itself. A user who trusts it reaches GO
   in ONE reply. (flow §Turn-1; structure §Layer-0; surface §recommended-prominent)
2. **Model-first; roster collapsed to the registry default; agents hidden.** Never show
   the 6×2×N grid. Roster is a one-line toggle defaulting to the model's
   `default_roster_policy`; specific-agent selection is a third layer behind an explicit
   "customize". Orthogonality stays *exploitable* (any model + either roster) via an
   explicit override, never a forced grid. (structure §1–2,6)
3. **The dissenter is surfaced by name on Turn 1** — structural, not optional, not a
   knob the user can remove (can swap who, not whether). This is the single biggest
   trust move and it costs one line. (flow Risk-2; research: dissenter is load-bearing)
4. **Round count / synthesis method are NOT exposed.** The research cautions hardest
   against multi-round debate; a "rounds: 2/3/4" knob trains the harmful topology.
   Hard-cap at 2, never shown. (flow §Defaults, Anti-patterns; surface)
5. **Glosses describe OUTPUT SHAPE, not cultural name.** "areopagus" means nothing cold;
   "case record, verdict, remedy" does. Each model gets a ~5-word artifact gloss pulled
   from the registry's entry_gate/verb_field. (surface §gloss-requirement)
6. **Vague user ("just pick something") = go, no menu.** Treat it as a release. (flow)

### Model ordering (light → heavy; practical before historical)

jixia → seven-sages → junto → areopagus → parishad → yushitai. Practical-roster
everyday models first; historical councils reachable but not front-loaded (matches the
research caution against front-loading judge/verdict modes). (structure §3)

### Recommended rendered surface (Mockup C, refined)

Turn 1 — default accept path:
```
I'll convene **areopagus** with **historical reps** (archon, juror, power-limiter)
plus relevant advisors.
Dissenter: the Ephialtean power-limiter holds the counter-lens.
Adjudicative review — you'll get a case record, verdict, and remedy.

Enter to go — or change: model / roster / advisors
```

Override → model menu:
```
**Convening model (recommended): areopagus** — case record, verdict, remedy
Roster: historical reps + practical advisors

Alternatives — reply with a name:
  jixia         everyday counsel — diagnosis, dissent, next action   practical
  seven-sages   breadth on ambiguity — 7 angles + counsel            practical
  junto         improvement — commitment + follow-up                 practical
  parishad      authority conflict — obligation map + settlement     historical
  yushitai      audit — findings, owner, severity, fix               historical

To also change roster: e.g. "junto historical"
```

Typography (surface §): bold ONLY the recommendation; em-dash name/gloss separator;
noun output fields; no 1-6 numbering unless numeric input is accepted; roster auto-
expands as a visible axis ONLY when the classifier is low-confidence (structure §5).

### How this reshapes the increment

- `/advise` = the classifier acting on its own pick (Turn-1 conclusion, auto-run).
- `/advise-full` = the same pick shown as the pre-selected default in this menu.
- The classifier is the SHARED engine; the accept-vs-override signal is the passive
  routing-correctness metric (counsel-log).
- This is a SELECTION-UX problem, not a routing-accuracy problem — the human is the
  oracle, so the system must be legible, not right.

### Open dependency

The model glosses/ordering assume the existing six. If the verification pass (running)
confirms a NEW structure worth adding (the structured agreement/divergence aggregation
layer, single-source 2602.09341), it slots in as a 7th option in the same menu. If that
source is fabricated/unsupported, the menu is unchanged. Do not finalize gloss copy
until verification lands.
