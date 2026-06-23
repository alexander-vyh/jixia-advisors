"""Deterministic routing classifier for the convening-router (advisor-convening-router, emp.3).

Maps a draft (+ optional signals) to a convening model per the Test Oracle Brief
(openspec/changes/advisor-convening-router/test-oracle-brief.md):

  - ``/advise`` ALWAYS acts: ``classify`` returns a dispatchable model for EVERY input —
    never None, never a raise, never a menu (the menu lives in ``/advise-full``).
  - A SPECIALIST (seven-sages/areopagus/junto/parishad/yushitai) is returned iff it
    CLEARLY wins the margin gate; otherwise the ``jixia`` adaptive-triage default.
  - "Fail closed" = fall to the ``jixia`` default, never fake-pick a specialist on weak or
    tied signal. ``jixia`` is the universal floor, registry-resolved — never fabricated.
  - PURE-DETERMINISTIC: no model-judgment layer (deferred). Same input -> same output.

The model id and its roster are resolved against ``jixia/registry.json`` (the canonical
registry), so the classifier can never emit a non-registry model or an invalid roster.
Stdlib-only; the registry is resolved relative to this file so it works wherever run.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_REGISTRY_PATH = os.path.join(HERE, "registry.json")

# Registry-resolved: ids + roster policies come from the canonical registry, not local
# constants. A missing/unparseable registry is a deploy error and fails LOUD at import
# (never silently substitute a fabricated model) — see never-suppress.
with open(_REGISTRY_PATH, encoding="utf-8") as _f:
    _METHODS = json.load(_f)["methods"]

_ROSTER_BY_MODEL = {m: _METHODS[m]["default_roster_policy"] for m in _METHODS}

DEFAULT_MODEL = "jixia"  # the adaptive-triage floor; must exist in the registry
assert DEFAULT_MODEL in _METHODS, "registry is missing the jixia default model"

# Brief §0.3 — load-bearing thresholds (the gate), pinned.
MARKER_MIN = 1   # a specialist needs >= this many distinct markers to be a candidate
MARGIN_MIN = 1   # the top specialist must lead the runner-up by >= this to be chosen

# Brief §0.2 — per-specialist marker lexicon, derived from each method's registry
# entry_gate + verb_field. The WORDS are craft pins (owner-tunable); the scoring +
# margin gate are the load-bearing mechanism. jixia is intentionally absent: it is the
# default floor, not a score-gated specialist.
SPECIALIST_MARKERS = {
    "seven-sages": [
        "brainstorm", "options", "different angles", "perspectives", "explore",
        "what are the ways", "ideas for", "not sure how to approach", "where do i start",
        "open-ended",
    ],
    "areopagus": [
        "should i", "go or no", "go/no-go", "decide whether", "before i commit",
        "before we ship", "approve", "sign off", "final call", "is this the right call",
        "green-light",
    ],
    "junto": [
        "improve", "habit", "routine", "cadence", "get better at", "practice",
        "commit to", "experiment", "process improvement", "retro", "system for",
    ],
    "parishad": [
        "stakeholder", "two teams", "competing", "whose call", "authority", "jurisdiction",
        "role conflict", "obligation", "tradeoff between", "reconcile", "ownership dispute",
    ],
    "yushitai": [
        "audit", "what's wrong with", "failure", "post-mortem", "postmortem", "root cause",
        "accountab", "who owns", "what broke", "red team", "red-team", "blind spot",
        "what am i missing", "inspect",
    ],
}

# Brief §0.4 — registry-native dissent seats the classifier populates deterministically.
# Non-removability / low-sycophancy enforcement and the remaining seats are owned by the
# mandated-dissent bead; not decided here. Models absent from this map get None.
_NATIVE_DISSENT_SEAT = {
    "areopagus": "ephialtean-power-limiter",
    "yushitai": "discipline-impeachment-censor",
}


def _score(draft_lower, markers):
    """Count distinct markers from one lexicon present in the (lowercased) draft."""
    return sum(1 for marker in markers if marker in draft_lower)


def classify(draft, signals=None):
    """Route a draft to a convening model. Always returns a dispatchable result.

    Returns a dict ``{model, roster, confidence, dissent_seat}`` where ``model`` is always
    a registry id, ``roster`` is that model's registry ``default_roster_policy``,
    ``confidence`` is the integer margin (top specialist score minus runner-up), and
    ``dissent_seat`` is the registry-native seat for the chosen model (or None).
    """
    text = (draft or "").lower()
    scores = {model: _score(text, markers) for model, markers in SPECIALIST_MARKERS.items()}

    # Rank specialists by score; ties are broken arbitrarily but a tie can never win the
    # margin gate (margin 0 < MARGIN_MIN), so it always falls to the default — no coin flip.
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_model, top_score = ranked[0]
    second_score = ranked[1][1]
    margin = top_score - second_score

    if top_score >= MARKER_MIN and margin >= MARGIN_MIN:
        model = top_model
    else:
        model = DEFAULT_MODEL  # fail closed to the adaptive default — never guess a specialist

    return {
        "model": model,
        "roster": _ROSTER_BY_MODEL[model],
        "confidence": margin,
        "dissent_seat": _NATIVE_DISSENT_SEAT.get(model),
    }
