## Why

`/advise` today hardcodes ONE convening shape — a fixed advisor pair — and ignores the six convening methods already built in `advisor-convening-methods-v2` (jixia, seven-sages, areopagus, junto, parishad, yushitai). A draft that needs an audit (yushitai) or a pre-action verdict (areopagus) gets the same everyday pair as a routine question. This change makes `/advise` a front door that **routes** a draft/decision to an appropriate convening *model* (deliberation structure) plus a roster — and bakes in a non-removable dissent role, because the verified research (`docs/research/convening-models-2026-06/`) shows an LLM council's dominant failure mode is sycophantic agreement-collapse.

## What Changes

- **Two entry points over one shared classifier:**
  - `/advise` — **automatic**: the classifier picks `(convening model, roster)` and runs it; no menu (it may state its pick in one line, but requires no selection).
  - `/advise-full` — **menu**: the user picks model + roster + (optionally) specific agents, with the classifier's pick pre-selected as the default and accepted in one reply.
- **A routing classifier** mapping draft text + signals (audience, channel, stakes) → `(convening model, roster, confidence, recommended dissent seat)`.
- **Mandated dissent**: every default convening structure seats a **non-removable, low-sycophancy** dissent role (the "devil's advocate"). The user may swap *who* holds it, never *whether* it exists.
- **No-confident-match → the `/advise-full` offer**, never a guessed model (carries forward the skeleton's anti-horoscope rule).
- **Passive routing-correctness signal**: the auto-pick is logged; an override (or re-run) in `/advise-full` is the implicit "auto pick was wrong" signal — so `/advise-full` is a *selection-UX* problem (the human is the oracle), not a routing-accuracy problem.
- Round-count and synthesis method are **not** exposed as user knobs (multi-round debate is research-contraindicated).

## Capabilities

### New Capabilities
- `convening-routing`: the shared classifier and the two entry points (`/advise` auto-run, `/advise-full` menu), the no-confident-match fallback, and the auto-pick / override logging.
- `mandated-dissent`: the cross-cutting invariant that every default convening structure includes a non-removable, low-sycophancy dissent seat, mapped to each method's native instance (areopagus Ephialtean power-limiter; yushitai remonstrance/impeachment censor; everyday jixia counter-lens).

### Modified Capabilities
<!-- None at the canonical-spec level: openspec/specs/ has no established capabilities yet. The prior single-pair advise behavior lives in the advisor-routing change; this change supersedes it via the new convening-routing capability rather than editing a canonical spec. -->

## Impact

- **Depends on** `advisor-routing` (the `/advise` skeleton, counsel-log, send-bounce) and `advisor-convening-methods-v2` (the six methods + the method registry, with structure/roster treated as orthogonal axes).
- **Builds atop an unvalidated skeleton** (0 real bounces; the advisor-routing human skeleton-validated gate is still open) — a deliberate, eyes-open craft choice, not a claim of validation.
- New code: a routing classifier + a `/advise-full` skill surface; modifications to the `/advise` skill to call the classifier and run the selected model.
- New runtime data: auto-pick + override records appended to the existing `~/.claude/jixia/counsel-log.jsonl`.
- **Out of scope / deferred**: full 16-agent taxonomy routing; multi-round debate as a mode (research-contraindicated); single-agent self-refine as a mode (research-contraindicated); a structured agreement/divergence aggregation model ("AgentAuditor", arXiv 2602.09341) as a 7th model (experimental future candidate, single-preprint evidence); cadence convening (separate increment).
