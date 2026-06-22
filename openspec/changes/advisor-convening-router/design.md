## Context

`/advise` (from `advisor-routing`) is a working front door that always convenes one fixed
advisor pair. Separately, `advisor-convening-methods-v2` shipped six structurally-distinct
convening methods (jixia, seven-sages, areopagus, junto, parishad, yushitai) with a
registry that treats deliberation **structure** and **roster** as orthogonal axes. The two
bodies of work are disconnected: nothing routes a draft to the *right* structure.

This change connects them, and adds a research-driven invariant. The verified research
(`docs/research/convening-models-2026-06/01-verified-synthesis.md`) found that an LLM
council's dominant failure mode is **sycophantic agreement-collapse** (debater sycophancy
↔ abandoning-correct r=0.902; naive multi-round debate often loses to majority vote), and
that the load-bearing mitigation is a **low-sycophancy dissent role + short interaction**.
The `/advise-full` UX is specified by three converged design lenses in `design-inputs/`.

Constraint: this is a Claude Code CLI skill (conversational markdown surface, no GUI) in a
solo personal repo; the user (alexander-vyh) is the decision authority.

## Goals / Non-Goals

**Goals:**
- One shared classifier that maps a draft + signals → `(convening model, roster, confidence, dissent seat)`.
- Two entry points: `/advise` (auto-run the pick) and `/advise-full` (menu, pick pre-selected).
- A non-removable, low-sycophancy dissent seat in every default structure.
- No-confident-match → the `/advise-full` offer, never a guessed model.
- A passive routing-quality signal: log the auto-pick and any override.

**Non-Goals:**
- Full 16-agent taxonomy routing.
- Multi-round debate as a convening mode (research-contraindicated).
- Single-agent self-refine as a convening mode (research-contraindicated).
- A structured agreement/divergence aggregation model ("AgentAuditor", arXiv 2602.09341) — experimental future candidate only.
- Cadence convening (separate increment).
- Re-proving the parent `advisor-routing` value oracle (does counsel change the next action).

## Decisions

**D1 — Route among convening MODELS, not advisor pairs.**
The original framing ("2-3-type routing table" → advisor pairs) is superseded: the routing
target is one of the six convening *structures*, staffed by a roster. Rationale: the
methods already exist and are mechanically distinct (each emits a method-verb field —
areopagus `verdict`, yushitai `corrective_action`, junto `experiment_or_commitment`);
routing among structures is what makes `/advise` worth more than the fixed pair. *Alt
considered:* routing among advisor pairs only — rejected; it ignores the built methods and
duplicates the convening layer.

**D2 — Two entry points over one classifier.**
`/advise` auto-runs the classifier's pick; `/advise-full` shows the pick as a pre-selected
default in a menu. Rationale: the everyday path must stay frictionless (or the bounce-habit
risk from the parent design bites), while deliberate users get full control. Crucially this
**dissolves the routing-accuracy oracle problem**: with a menu, the human is the oracle, so
the system must be *legible*, not provably *correct*. *Alts considered:* always-auto
(no user control, hard oracle); always-menu (taxes the common case). Rejected both.

**D3 — Mandated dissent, non-removable, low-sycophancy.**
Every default structure seats a "devil's advocate" (advocatus diaboli) the user can
re-assign but not remove. Its prompt must argue the strongest counter-case, resist
agreeing, and not soften in later rounds. Rationale: directly operationalizes the verified
dominant-failure finding. Each method has a native instance to map to (areopagus Ephialtean
power-limiter; yushitai remonstrance/impeachment censor; everyday jixia counter-lens). *Alt
considered:* optional dissenter — rejected; making it opt-in trains users to skip the one
element the research says is load-bearing.

**D4 — Classifier is testable-first; fails CLOSED to no-confident-match.**
The classifier must be exercisable by a labeled fixture suite (positive per mapped
draft-type; negative controls → no-confident-match). Prefer a deterministic signal core
(audience/channel/stakes/artifact-shape → model) with an explicit confidence threshold;
model-judgment may fill the fuzzy middle but must fall back to no-confident-match rather
than guess. Rationale: the auto path needs a mechanical oracle, and "never guess a lens" is
inherited from the skeleton's anti-horoscope rule. *Alt considered:* pure model-judgment
routing — rejected as the sole mechanism (soft, non-deterministic oracle); allowed only as a
fail-closed fallback layer.

**D5 — Do not expose round-count or synthesis method as knobs.**
Hard-cap interaction at 2-3 exchanges; never surface a "rounds" control. Rationale: research
shows added rounds increase sycophancy, not accuracy — a rounds knob trains the harmful
topology.

**D6 — `/advise-full` menu structure (distilled from `design-inputs/`).**
Model-first; roster collapsed to each model's registry `default_roster_policy`;
specific-agent selection in a hidden third layer; the classifier pick short-circuits to a
one-line confirm; the dissenter is NAMED on the first turn as a feature; glosses describe
OUTPUT SHAPE not cultural name; models ordered light→heavy (practical-roster everyday models
first, historical councils reachable but not front-loaded). The full 6×roster×N grid is
never shown; orthogonality stays reachable via explicit override. *Source:* `design-inputs/00-synthesis.md` (+ the three lens files).

**D7 — Passive routing-quality metric via the existing counsel-log.**
Log the auto-pick on every `/advise`; log an override / re-run on `/advise-full`. The
accept-vs-override rate is the routing-quality signal — no new store, same counsel-log
JSONL pattern.

## Risks / Trade-offs

- **Building atop the unvalidated skeleton (0 bounces).** → Mitigation: stated as a
  deliberate craft choice; the override metric gives early routing signal independent of
  the parent value oracle; nothing here claims the skeleton's premise is confirmed.
- **Classifier mis-routes.** → Mitigation: `/advise-full` override + no-confident-match
  fallback + the logged override signal surfaces systematic mis-routes.
- **Sycophancy survives even with a seated dissenter.** → Mitigation: low-sycophancy
  dissenter prompt + 2-3 round cap + no rounds knob (D3, D5).
- **Menu overwhelm (two orthogonal axes + agents).** → Mitigation: progressive disclosure
  per D6 (model-first, roster collapsed, agents hidden, classifier short-circuit).
- **Temptation to add the "AgentAuditor" 7th model on thin evidence.** → Mitigation:
  explicitly deferred as experimental (single non-peer-reviewed preprint).

## Migration Plan

Additive and fail-safe. New: a routing classifier module + a `/advise-full` skill surface.
Modified: the `/advise` skill calls the classifier and runs the selected model. Reuses the
existing `~/.claude/jixia/counsel-log.jsonl` and the `convening-methods-v2` registry.
Install via the existing `INSTALL.sh` symlink+merge pattern. **Rollback:** if the classifier
is absent or errors, `/advise` falls back to the current fixed-pair behavior (fail-safe — no
worse than today).

## Open Questions

- The initial routing table: which draft-types map to which of the six models (to be pinned
  with fixtures in `specs/` + `test-oracle-brief.md`).
- The confidence threshold below which the classifier yields no-confident-match.
- Whether the classifier core is pure-deterministic or a deterministic+model-judgment hybrid
  (lean: deterministic core, model-judgment fail-closed fallback).
- How a draft's "type" is detected at bounce-time (send-bounce hook) vs at `/advise`-time —
  and whether the send-bounce hook's hardcoded `behavioral-psychologist` becomes a classifier
  call.
