# Problem Framing — advisor-convening-router

Confirmed with the user (alexander-vyh), 2026-06-22 (inline confirmation across the
design conversation: two-entry-point split, dissent framing, and "new change" all
explicitly approved).

## Problem

`/advise` applies ONE convening shape — a fixed advisor pair
{behavioral-psychologist, manager-tools-advisor} — to every draft, and ignores the six
convening methods already built in `advisor-convening-methods-v2` (jixia, seven-sages,
areopagus, junto, parishad, yushitai). Observable: the methods are callable as their own
commands but are never reachable *through* the front door; a draft needing an audit
(yushitai) or a pre-action verdict (areopagus) gets the same everyday pair as a routine
question. Separately, no convening shape currently guarantees a dissenting voice.

## Why now

The skeleton (`advisor-routing`) is built, and a verified research pass
(`docs/research/convening-models-2026-06/`) established that an LLM council's dominant
failure mode is **sycophantic agreement-collapse** — agents abandon correct positions to
agree — mitigated by a mandated low-sycophancy dissenter and short interaction. The six
convening structures already exist on disk but are siloed from `/advise`. Honest caveat
(recorded deliberately): this builds ATOP the still-unvalidated skeleton (0 real bounces;
the `advisor-routing` human skeleton-validated gate is open). Proceeding is a deliberate,
eyes-open craft choice — NOT a claim the skeleton's value premise is confirmed.

## Decision authority

The user (alexander-vyh). Solo personal repo; the user owns the what and why.

## Behavioral population

Primary: Claude sessions — they must classify a draft/decision and convene the right
convening *model* with a roster and a seated dissenter, instead of always firing one
pair. Secondary: the user — who reaches for `/advise-full` to override the auto-pick when
they want control, and who reads/acts on the counsel.

## Riskiest Assumption

Betting: automatic routing picks the right convening model often enough that the user
accepts it — i.e. the auto-pick is right enough to be worth not asking. Wrong when: users
routinely override the auto-pick in `/advise-full`, or re-run with a different model.
Measurable via the accept-vs-override signal logged on every `/advise` / `/advise-full`
invocation (no calendar window needed — it is event-count driven, like the parent).

## Success criteria

Three mechanical checks, all required:
1. **Routing correctness** — the classifier passes a labeled-fixture suite: positive
   cases per mapped draft-type → expected model, AND negative controls (ambiguous /
   out-of-scope → no-confident-match, NEVER a guessed model). Fragile impls rejected:
   "always returns the everyday default" and "keyword-anywhere → match".
2. **Mandated-dissent invariant** — every default convening structure seats a
   non-removable, low-sycophancy dissent role; a test proves it cannot be dropped (only
   swapped).
3. **Measurability** — the auto-pick and any override are logged, so the routing-quality
   (accept-vs-override) rate is computable. `/advise-full` legibility (the human is the
   oracle) is the bar there, not routing accuracy.
(The deeper "does counsel change the next action" remains the parent `advisor-routing`
oracle; this change does not re-prove it.)
