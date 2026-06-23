# Test Oracle Brief — advisor-convening-router (the routing classifier)

**Form:** rapid 3-section (craft tool; consistent with the sibling
`advisor-convening-methods-v2` brief) **with** the mandatory
named-fragile-implementation challenge retained, preceded by a **§0 pinned-decisions**
block (where this brief earns its keep — it resolves the design's three Open Questions)
and followed by a **mutation enumeration** for the fixture suite
(`jixia-advisors-emp.2`) to encode.

**Locked design (2026-06-22, owner-driven via the questions tool):**
1. **`/advise` (no flags) ALWAYS acts** — it never shows a menu and never declines. It
   runs a clear specialist if one wins, else the **jixia adaptive-triage default**.
2. **jixia is the universal default floor** (adaptive triage, not a generic lens — see
   §0.2). The menu lives **only** in `/advise-full`; a wrong auto-pick is a cheap,
   *logged* `/advise-full` re-run (the accept-vs-override routing-quality signal).
3. **The classifier is pure-deterministic** (model-judgment fallback deferred).

This locks an amendment to `specs/convening-routing/spec.md`'s
`no-confident-match-offers-never-guesses` requirement (see "Spec amendment" below):
the "offer the menu / dispatch nothing" behavior for `/advise` is replaced by
"always dispatch — a clear specialist or the jixia default — and never fake-pick a
specialist below confidence." "Never guess" survives, narrowed to *specialists*.

**Scope of what this brief constrains:** the ONE behavioral artifact in this skeleton
batch — the **routing classifier** (implemented in `jixia-advisors-emp.3`). The
`/advise` / `/advise-full` skill surfaces, the menu UX, the mandated-dissent invariant,
the logging wiring, and install are **out of scope** (later beads; see "Explicitly out
of scope" below). Authored *before* the classifier exists so the fixtures (`emp.2`) have
a fixed target the implementation cannot be bent to match.

**Independent source of truth for the classifier:**
- `specs/convening-routing/spec.md` (as amended below), and
- `jixia/registry.json` — **canonical** for the six method ids, each method's
  `entry_gate`, `verb_field`, and `default_roster_policy`. The routing table in §0 is
  *derived from the registry's entry gates*; the registry stays the source of truth, so
  if an `entry_gate` changes, the lexicon for that model is re-derived here, not invented.

Where the spec/design underspecify a load-bearing constant (the table, the margin), this
brief **PINS** it in §0; the classifier inherits whatever this brief fixes, and the
`emp.2` tests encode it **independently** so test and implementation cannot drift.

---

## §0. Pinned decisions (resolving the design's three Open Questions)

### §0.1 — The classifier output contract

For `/advise`, the classifier **always** returns a dispatchable tuple — there is no
"dispatch nothing" terminal:

```
{model, roster, confidence, dissent_seat}     # /advise auto-runs this, every time
```

- `model` ∈ the six registry ids `{jixia, seven-sages, areopagus, junto, parishad, yushitai}` — **never** a fabricated or non-registry name. It is a **clear-winning specialist** if one exists (§0.3), otherwise **`jixia`** (the adaptive default).
- `roster` = that model's registry `default_roster_policy` (jixia/seven-sages/junto → `practical`; areopagus/parishad/yushitai → `historical`). Override is `/advise-full`'s job (deferred).
- `confidence` = the integer **margin** (§0.3). It is still returned even though `/advise` never blocks on it, because **`/advise-full` reads it** to decide whether to auto-expand the roster axis (low confidence → show roster as a visible choice; design-input `03-ux-structure` §5).
- `dissent_seat` = the model's registry-native dissent default (§0.4). **The skeleton classifier merely populates this slot deterministically; the non-removability + low-sycophancy *invariant* and its tests belong to the `mandated-dissent` spec — out of scope here.**

`/advise-full` reuses the same classifier output but, instead of auto-running, presents it
as the pre-selected default in a menu — that surface is a later bead.

### §0.2 — The routing table (draft-type → model), derived from registry entry gates

**The default floor is `jixia` — and that is correct here, not a defect, because the
"offer the menu" path lives in `/advise-full`, not in `/advise`.** `jixia` is NOT a
generic catch-all lens: per the registry its job is *"question-driven triage: select the
smallest useful mix of advisors from `claude/agents/` by relevance, adding a counter-lens
only when it materially improves the answer."* It is an **adaptive router** — running it
on an unclear ask is the anti-horoscope move (it right-sizes the lenses to whatever was
actually written) rather than fake-picking a specialist.

A **specialist** is chosen over the default only when it *clearly wins* (§0.3). The
deterministic core is a **per-model marker lexicon** (the send-bounce hook's
`QUALIFY_MARKERS` idiom): each specialist scores `= count of distinct markers from its
lexicon found (case-insensitive substring) in the draft`. Markers are *derived from each
method's registry `entry_gate` + `verb_field`*:

| Model | Registry entry_gate (source of truth) | verb_field | Role in routing | Initial marker lexicon (craft pin) |
|---|---|---|---|---|
| `jixia` | everyday counsel / a right-sized set of lenses | `next_action` | **DEFAULT FLOOR** (adaptive triage) | — (default; not score-gated. Everyday-counsel phrasing — "thoughts on", "what do you think", "advice on", "sanity check" — also resolves here, but jixia wins by *being the floor* whenever no specialist clears the margin) |
| `seven-sages` | bounded breadth on an ambiguous planning question | `distilled_counsel` | specialist | "brainstorm", "options", "different angles", "perspectives", "explore", "what are the ways", "ideas for", "not sure how to approach", "where do i start", "open-ended" |
| `areopagus` | a consequential decision reviewed before action | `verdict` | specialist | "should i", "go or no", "go/no-go", "decide whether", "before i commit", "before we ship", "approve", "sign off", "final call", "is this the right call", "green-light" |
| `junto` | self-improvement, operating cadence, or civic/practical improvement | `experiment_or_commitment` | specialist | "improve", "habit", "routine", "cadence", "get better at", "practice", "commit to", "experiment", "process improvement", "retro", "system for" |
| `parishad` | tradeoffs resolved across roles, duties, sources of authority, or stakeholders | `settlement` | specialist | "stakeholder", "two teams", "competing", "whose call", "authority", "jurisdiction", "role conflict", "obligation", "tradeoff between", "reconcile", "ownership dispute" |
| `yushitai` | accountability, audit, remonstrance, or failure-mode detection | `corrective_action` | specialist | "audit", "what's wrong with", "failure", "post-mortem", "postmortem", "root cause", "accountab", "who owns", "what broke", "red team", "red-team", "blind spot", "what am i missing", "inspect" |

**What is load-bearing vs. a craft pin:**
- **Load-bearing** (the fixtures pin these, MUST NOT drift): the *mechanism*
  (specialist marker-scoring + margin gate, else jixia default), the *jixia-is-the-floor*
  decision, the *registry-derivation* of each specialist lexicon, and *one clean positive
  per specialist* (each of the five specialists has at least one draft that resolves to
  it and only it — so the table is not accidentally collapsed).
- **Craft pin** (NOT load-bearing; owner may tune): the *exact marker strings*. The
  `emp.2` tests assert *boundary behavior* (a clean per-specialist positive resolves to
  that specialist; an unclear/contended draft falls to jixia), **not** the specific
  words. An echo test that hard-codes the lexicon is **rejected** (§2, FRAGILE-D).

### §0.3 — The specialist-vs-default margin gate (pinned)

Among the five **specialists**, let `top` = highest-scoring, `second` = runner-up.

```
MARKER_MIN = 1      # a specialist needs ≥1 distinct marker to be a candidate at all
MARGIN_MIN = 1      # the top specialist must lead the runner-up by ≥ this many markers to be chosen

confidence := top.score - second.score                      # the integer returned as `confidence`
model := top-specialist   if  top.score >= MARKER_MIN AND confidence >= MARGIN_MIN
         jixia            otherwise                          # no clear specialist → adaptive default
```

So jixia is chosen when **no specialist scores** (`top.score == 0`, e.g.
off-distribution input) **OR** when **specialists tie** (`confidence == 0`, ambiguous
between two specialists). In both cases `/advise` still acts — it runs the adaptive
default — and never fake-picks among tied specialists.

**Rationale for `MARGIN_MIN = 1` (lenient; pinned as the recommended default, owner-tunable):**
both error directions are now **cheap, logged, one-reply overrides** via `/advise-full`
(D7's accept-vs-override metric). A thin specialist lead auto-running, or a fall-to-jixia
when a specialist would have been marginally better, both surface in the override log
rather than costing the user anything irreversible. The gate is therefore biased lenient
to keep `/advise` frictionless (D2). The `emp.2` tests assert the *boundary* (margin 0 →
jixia; margin 1 → specialist; top 0 → jixia), **not** the number — so the owner may
tighten `MARGIN_MIN` later without invalidating the oracle. *(I pinned this rather than
re-asking, because under the always-act design no choice here can produce an
irreversible/expensive outcome — only a logged override. Flag it at the gate if you want
it stricter.)*

### §0.4 — Deterministic core only; model-judgment fallback DEFERRED

`design.md` D4 floated a "deterministic core + model-judgment fail-closed fallback."
**Decision: the skeleton classifier is PURE-DETERMINISTIC. The model-judgment layer is
DEFERRED.** Rationale: the auto path needs a *mechanical* oracle the fixtures can pin
exactly; a model-judgment layer is non-deterministic and would reintroduce a floating
oracle. Under the always-act design this costs nothing: "I can't confidently pick a
specialist" resolves to the **jixia adaptive default**, whose own job is to right-size
the lenses — so the fuzzy middle is handled by jixia at *runtime*, not by a
non-deterministic *routing* layer. (Native `dissent_seat` defaults, §0.1: areopagus →
`ephialtean-power-limiter`, yushitai → `discipline-impeachment-censor` per the registry
`historical_roster`; jixia → its native counter-lens; the other seats are owned by the
`mandated-dissent` bead, not pinned here.)

---

## 1. Business invariant

`/advise` **always** dispatches exactly one registry model: a specialist when one
*clearly wins* the margin gate, otherwise the **jixia adaptive default**. The classifier
**never** fabricates a model or lens, **never** fake-picks a specialist on weak or tied
signal (it falls to jixia instead), and **never** lets jixia swallow a draft that a
specialist *clearly* won. The menu / decline behavior belongs to `/advise-full`, not
`/advise`.

**Independent source of truth:** `specs/convening-routing/spec.md` (as amended) —
`classifier-resolves-to-a-real-model` + the amended
`no-confident-match-offers-never-guesses` — plus the §0 pins, with `jixia/registry.json`
canonical for the id/roster/verb sets. Correctness is the `(model, roster, confidence)`
tuple **returned** — observable output, not internal call structure.

## 2. Negative controls + the named fragile-implementation challenge

**NC-1 — off-distribution input → jixia (default), still acts.** A draft with zero
specialist signal ("what's the weather tomorrow?", or a bare code snippet) → `top.score
== 0` → `model == jixia`, dispatched. Proves `/advise` always acts and the default floor
catches no-signal input.

**NC-2 — contended-specialists input → jixia (not a coin flip).** A draft that is *both*
an audit *and* a stakeholder conflict (yushitai and parishad tie, margin 0) → `model ==
jixia`. Proves a specialist tie falls to the adaptive default rather than silently
picking the arbitrarily-first specialist.

### Named fragile implementations the `emp.2` tests MUST reject

**FRAGILE-A (the headline) — "trigger-happy specialist."** A classifier that returns the
top-scoring specialist whenever `top.score >= 1`, ignoring the margin / tie. It *looks*
right on clean inputs but fake-picks a specialist on weak or tied signal — exactly the
"guess a specialist" the spec forbids. **Caught by NC-2** (a tie MUST resolve to jixia,
not the arbitrarily-top specialist) and by R-M9 (margin-0 boundary).

**FRAGILE-B — "jixia swallows clear specialist signal."** The mirror error: a classifier
that returns jixia even when a specialist *clearly* wins (e.g. routes a textbook audit to
jixia). **Caught by the five per-specialist positives** (R-M2…R-M6): each clean
specialist draft MUST resolve to its specialist, proving the default floor does not
starve confident specialist routing.

**FRAGILE-C — "fabricated / aliased model."** Returns a model id outside the six, or a
roster/lens not resolvable in `jixia/registry.json`. **Caught by a contract test:**
returned `model` ∈ the six registry ids AND `roster` resolves to the registry policy for
that model.

**FRAGILE-D — "echo test" (a test smell, rejected at authoring).** A fixture that
hard-codes the §0.2 lexicon and asserts the classifier returns that same dict recomputes
the implementation. **Rejected:** `emp.2` fixtures assert *resolved model* for
hand-labeled drafts, with the expected model written from this brief's *registry-derived
intent*, never copied from `emp.3`'s marker constants.

## 3. Final outcome verification

```
python3 -m pytest jixia/test_routing_classifier.py -q     # emp.2 suite, green against emp.3
python3 -m pytest jixia/ -q                                # whole suite stays green
```

Plus the **skeleton acceptance** (the outcome the unit suite stands in for): a real
`/advise <draft>` on one clean per-specialist draft auto-runs the *correct* registry
specialist; a deliberately ambiguous `/advise <draft>` auto-runs **jixia** and states the
pick (never a menu, never nothing) — the two behaviors the amended routing requirement
names. (The end-to-end log/record assertion is owned by the logging bead, out of scope.)

---

## Mutation enumeration (one Mn per requirement scenario + control — for `emp.2`)

Modeled on the sibling suites: a positive fixture that resolves clean, plus mutations
asserting the wrong behavior is rejected and the offending model/decision is named.

| Mn | Fixture (hand-labeled draft) | Asserts |
|---|---|---|
| **R-M1** (NC-1, FRAGILE-A) | off-distribution ("what's the weather?") | → `model == jixia`, dispatched (always acts; default floor catches no-signal) |
| **R-M2** (FRAGILE-B) | clean go/no-go ("should I ship this before the deadline — final call?") | → `model == areopagus`, `roster == historical` |
| **R-M3** (FRAGILE-B) | clean audit ("audit this rollout for failure modes — what broke and who owns it?") | → `model == yushitai`, `roster == historical`. (`dissent_seat` *key* present per the output contract; its *value/seating* is asserted by the `mandated-dissent` bead, not `emp.2` — dissent-seating tests are out of scope for the fixture corpus.) |
| **R-M4** (FRAGILE-B) | clean stakeholder conflict ("two teams both claim ownership — whose call is this?") | → `model == parishad` |
| **R-M5** (FRAGILE-B) | clean improvement ("help me build a weekly review habit / cadence") | → `model == junto` |
| **R-M6** (FRAGILE-B) | clean open-planning ("not sure how to approach this — brainstorm the different angles") | → `model == seven-sages` |
| **R-M7** | clean everyday counsel ("thoughts on how I framed this?") | → `model == jixia`, `roster == practical` (the default floor on a genuine right-sizing ask) |
| **R-M8** (NC-2, FRAGILE-A) | contended specialists (audit **and** stakeholder conflict, margin 0) | → `model == jixia` (tie falls to default, not a coin flip) |
| **R-M9** | margin boundary | 2-marker-vs-1 specialist → that specialist (margin 1 wins); 1-vs-1 → jixia (margin 0) — the threshold exercised both sides |
| **R-M10** (FRAGILE-C) | any input | returned `model` ∈ the six registry ids; `roster` resolves to that model's registry `default_roster_policy`; no fabricated lens |
| **R-M11** | confidence field | `confidence == top.score - second.score` (integer), exposed so `/advise-full` can auto-expand the roster axis on low confidence |

---

**Explicitly out of scope (owned by later beads — do NOT pin here):** the `/advise`
auto-run wiring and `/advise-full` menu UX (incl. where the menu/decline lives) →
entry-point beads; the mandated-dissent *invariant* (non-removable, low-sycophancy
prompt) → `specs/mandated-dissent`; the counsel-log routing records → logging bead;
`INSTALL.sh` → install bead. This brief pins **only** the classifier's table, margin
gate, and determinism decision.

## Spec amendment (locked here, owed to `specs/convening-routing/spec.md`)

The `no-confident-match-offers-never-guesses` requirement is amended to match the locked
always-act design: `/advise` **always dispatches** — a clear specialist or the jixia
adaptive default — and **never fake-picks a specialist below the margin** (it falls to
jixia). The "offer the menu / dispatch nothing" behavior is **relocated to `/advise-full`**
(always reachable as the override). "Never guess" survives, narrowed: never dispatch a
*specialist* the classifier is not confident in — running the declared, logged jixia
default is not a guess. (Amendment applied alongside this brief.)

**Open for owner correction:** the §0.2 marker strings, `MARKER_MIN`/`MARGIN_MIN`
(§0.3), and the deterministic-only decision (§0.4) are craft pins justified above — the
tests assert each *boundary*, not the specific value. Correct any **HERE** first; the
classifier (`emp.3`) and fixtures (`emp.2`) inherit whatever this brief fixes.
