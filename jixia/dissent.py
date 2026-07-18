"""Mandated-dissent seating for the convening-router (advisor-convening-router, emp.4).

Implements the cross-cutting invariant from
openspec/changes/advisor-convening-router/specs/mandated-dissent/spec.md:

  - Every default convening run seats exactly ONE dissenter (the "devil's advocate").
  - The seat is NON-REMOVABLE: a removal attempt re-seats the default; the user may swap
    WHO holds it, never WHETHER it exists.
  - The seat's PROMPT is low-sycophancy — it is the load-bearing part of the seat
    (research: a council's dominant failure is sycophantic agreement-collapse). Any real
    occupant becomes a dissenter by holding this prompt.
  - The occupant resolves to a REAL source-backed rep (historical) or a real
    claude/agents/ advisor (practical) — never a placeholder. An invalid swap target
    re-seats the default rather than seating a fake.

Stdlib-only; resolves the registry + agent files relative to this file.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
_REGISTRY_PATH = os.path.join(HERE, "registry.json")
_AGENTS_DIR = os.path.join(REPO_ROOT, "claude", "agents")

with open(_REGISTRY_PATH, encoding="utf-8") as _f:
    _METHODS = json.load(_f)["methods"]

# The low-sycophancy directive set — the seat's defining content. It MUST instruct the
# occupant to argue the counter-case, resist agreement, and not soften in later rounds.
DISSENT_DIRECTIVES = (
    "You hold the mandated dissent seat (the devil's advocate / advocatus diaboli) — a "
    "required, non-removable role. Argue the STRONGEST counter-case against the emerging "
    "consensus. Resist agreeing for the sake of consensus: do not concede a point unless "
    "it is genuinely refuted by evidence, not by social pressure. Do NOT soften your "
    "position in later rounds — if anything, sharpen it. Name the risk, the failure mode, "
    "and the option no one else is defending. You are FOR the user precisely by refusing "
    "to be agreeable."
)

# Historical methods -> their native dissent instance (a rep id in the method's
# registry historical_roster). areopagus + yushitai are spec-pinned; parishad has no
# spec-named native dissenter — narada-procedure-exemplar is a FLAGGED default (pleading
# is the most adversarial of parishad's reps). Owner-correctable; see the brief.
NATIVE_DISSENTER = {
    "areopagus": "ephialtean-power-limiter",          # spec-pinned (Ephialtean power-limiter)
    "yushitai": "discipline-impeachment-censor",      # spec-pinned (remonstrance/impeachment)
    "parishad": "narada-procedure-exemplar",          # FLAGGED default — owner-correctable
}

# Practical methods -> default counter-lens advisor (a real claude/agents/ file). The
# low-sycophancy prompt is what enforces dissent, so the holder is swappable; this is a
# FLAGGED default. The per-question counter-lens selection is the method's runtime job.
DEFAULT_COUNTER_LENS = "management-philosophizer"


def _real_rep_ids():
    """Rep ids across all methods whose module file actually exists on disk."""
    ids = set()
    for info in _METHODS.values():
        for rep in info.get("historical_roster", []):
            if os.path.exists(os.path.join(REPO_ROOT, rep["module"])):
                ids.add(rep["id"])
    return ids


def _real_agents():
    return {f[:-3] for f in os.listdir(_AGENTS_DIR) if f.endswith(".md")}


def occupant_resolves(occupant):
    """True iff occupant is a real source-backed rep or a real advisor file."""
    if not occupant or not isinstance(occupant, str):
        return False
    return occupant in _real_rep_ids() or occupant in _real_agents()


def default_occupant(model):
    """The default dissenter for a model: native rep (historical) or counter-lens (practical)."""
    if _METHODS[model]["default_roster_policy"] == "historical":
        return NATIVE_DISSENTER[model], "native"
    return DEFAULT_COUNTER_LENS, "counter-lens"


def seat_dissenter(model, customization=None):
    """Seat exactly one dissenter for a convening run. Always returns a real dissenter.

    customization (optional dict):
      {"remove": True}          -> ignored; the default is re-seated (reinstated=True)
      {"occupant": "<name>"}    -> swap WHO, if it resolves to a real rep/agent; an
                                   unresolvable target re-seats the default (reinstated=True)
    """
    if model not in _METHODS:
        raise ValueError("unknown convening model: %r" % (model,))

    default, default_kind = default_occupant(model)
    occupant, kind, reinstated = default, default_kind, False

    if customization:
        requested = customization.get("occupant")
        wants_removal = customization.get("remove")
        if requested and not wants_removal:
            if occupant_resolves(requested):
                occupant, kind = requested, "custom"
            else:
                # never seat a fake — fall back to the mandatory default
                reinstated = True
        elif wants_removal:
            # the seat is non-removable: re-seat the default
            reinstated = True

    return {
        "model": model,
        "occupant": occupant,
        "kind": kind,
        "prompt": DISSENT_DIRECTIVES,
        "mandatory": True,
        "reinstated": reinstated,
    }
