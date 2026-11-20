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
    jixia/advisors/ advisor (practical) — never a placeholder. An invalid swap target
    re-seats the default rather than seating a fake.

Stdlib-only; resolves the registry + agent files relative to this file.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
_REGISTRY_PATH = os.path.join(HERE, "registry.json")
_AGENTS_DIR = os.path.join(HERE, "advisors")

with open(_REGISTRY_PATH, encoding="utf-8") as _f:
    _registry = json.load(_f)
_METHODS = _registry["methods"]
DEFAULT_COUNTER_LENS = _registry["practical_dissenter"]

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


def _real_agents():
    try:
        with os.scandir(_AGENTS_DIR) as files:
            return {f.name[:-3] for f in files if f.name.endswith(".md") and f.is_file()}
    except FileNotFoundError:
        # No bundled pool is visible; never substitute the host's personal collection.
        return set()


def occupant_resolves(occupant, model, roster):
    """Bundled advisors can sit on any roster; reps only on their own historical roster."""
    if not isinstance(occupant, str) or not occupant:
        return False
    if roster == "historical":
        for rep in _METHODS[model]["historical_roster"]:
            if rep["id"] == occupant:
                return os.path.isfile(os.path.join(REPO_ROOT, rep["module"]))
    return occupant in _real_agents()


def default_occupant(model, roster):
    """Return the default seat for the selected roster."""
    if roster == "historical":
        return _METHODS[model]["historical_dissenter"], "native"
    return DEFAULT_COUNTER_LENS, "counter-lens"


def seat_dissenter(model, customization=None, *, roster=None):
    """Seat exactly one dissenter for a convening run. Always returns a real dissenter.

    customization (optional dict):
      {"remove": True}          -> ignored; the default is re-seated (reinstated=True)
      {"occupant": "<name>"}    -> swap WHO, if eligible for this roster; otherwise
                                   re-seat the roster default (reinstated=True)
    """
    if model not in _METHODS:
        raise ValueError("unknown convening model: %r" % (model,))

    roster = roster or _METHODS[model]["default_roster_policy"]
    occupant, kind = default_occupant(model, roster)
    change = customization or {}
    requested = change.get("occupant")
    reinstated = bool(change.get("remove") or requested)
    if requested and not change.get("remove") and occupant_resolves(requested, model, roster):
        occupant, kind, reinstated = requested, "custom", False
    elif not occupant_resolves(occupant, model, roster):
        raise ValueError(f"Missing dissent lens {occupant!r} in the installed {roster} roster.")

    return {
        "model": model,
        "occupant": occupant,
        "kind": kind,
        "prompt": DISSENT_DIRECTIVES,
        "mandatory": True,
        "reinstated": reinstated,
    }
