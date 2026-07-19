"""Menu + override seam for /advise-full (advisor-convening-router, emp.6).

The testable seam behind the ``/advise-full`` skill. Where ``/advise`` auto-runs the
classifier's pick with no menu (see ``advise_autopick``), ``/advise-full`` presents that
same pick as a PRE-SELECTED default the user can accept in one reply or override.

Two layers, deliberately thin over the emp.5 plumbing (this module does NOT fork
``classify`` or ``seat_dissenter`` — it composes them):

  - ``build_menu(draft)`` computes the pre-selected menu. Model-first: a light->heavy
    ``models`` layer with output-shape glosses and the classifier pick marked
    ``is_default``; the roster is COLLAPSED to the selected model's registry default (a
    single scalar); the specific-agent pool is HIDDEN (a third layer, reachable via
    ``agent_options`` only when the user explicitly expands it). The full
    model×roster×agent grid is never emitted at once. NO round-count / synthesis knob is
    exposed (``round-count-and-synthesis-not-exposed``). build_menu writes NO record —
    rendering the menu is not yet a routing decision.

  - ``resolve_selection(draft, ...)`` turns an accept OR an override into the ONE shared
    ``routed`` record (``entry="advise-full"``) and a dispatch plan. It reuses
    ``advise_autopick.build_routed_record`` — same schema, same field names — so the
    accept-vs-override join emp.5 defined keeps working:

        accept   -> recommended_model == selected_model
        override -> recommended_model != selected_model (model overridden), and/or the
                    recorded roster / dissenter differs from the selected model's registry
                    default (roster / agent override). ``is_override`` decodes all three.

    The dissent seat is NON-REMOVABLE: an agent override routes through
    ``dissent.seat_dissenter``, so a removal or an invalid swap re-seats a real default —
    an override can never produce a dissenter-less convening.

``fell_back`` records (classifier absent/errored) carry a null ``recommended_model`` and
are EXCLUDED from accept-vs-override, exactly as in ``/advise``.

Stdlib-only. The registry is resolved relative to this file; the classifier + dissent
modules are imported lazily (via ``advise_autopick``) so their absence degrades instead
of breaking import here.
"""

import json
import os

import advise_autopick as _ap
from advise_autopick import append_record  # re-exported: same JSONL append as /advise

HERE = os.path.dirname(os.path.abspath(__file__))
_REGISTRY_PATH = os.path.join(HERE, "registry.json")

with open(_REGISTRY_PATH, encoding="utf-8") as _f:
    _METHODS = json.load(_f)["methods"]

MENU_ENTRY = "advise-full"

# Light -> heavy convening order for the model layer. Ceremony/formality ascends: the
# jixia adaptive floor, then bounded breadth, improvement practice, stakeholder treaty,
# consequential adjudication, and the heaviest audit/accountability inspection. The WORDS
# the menu shows come from the registry (display_name + output_fields); this list only
# fixes the ORDER, and is craft-tunable by the owner.
MODEL_ORDER = ["jixia", "seven-sages", "junto", "parishad", "areopagus", "yushitai"]

# Guard: the menu must present every registry method — a new method must not silently
# vanish from /advise-full because MODEL_ORDER wasn't updated.
assert set(MODEL_ORDER) == set(_METHODS), (
    "MODEL_ORDER must cover exactly the registry methods; drift: %r vs %r"
    % (sorted(MODEL_ORDER), sorted(_METHODS))
)


# Alias -> canonical model id, built from each method's registry `aliases`, so a
# user-supplied override like "sages" resolves to "seven-sages" (and "censorate" ->
# "yushitai"). Canonical ids map to themselves.
_ALIAS_TO_MODEL = {}
for _mid, _info in _METHODS.items():
    _ALIAS_TO_MODEL[_mid] = _mid
    for _alias in _info.get("aliases", []):
        _ALIAS_TO_MODEL[_alias] = _mid


def _canonical_model(name):
    """Resolve a model name or registry alias to its canonical id, or None if unknown.

    Tolerant of garbage (non-str, empty, whitespace, or a name absent from the CURRENT
    registry) so both the override path and the decoder never raise on a user typo or a
    legacy/hand-edited/cross-version record."""
    if not name or not isinstance(name, str):
        return None
    return _ALIAS_TO_MODEL.get(name) or _ALIAS_TO_MODEL.get(name.strip().lower())


def _default_roster(model):
    return _METHODS[model]["default_roster_policy"]


def _gloss(model):
    """The output-shape gloss for a model, derived from its registry output_fields.

    Derived (not hand-written) so the menu can never advertise a shape the method does
    not actually produce.
    """
    fields = _METHODS[model].get("output_fields", [])
    return ", ".join(f.replace("_", " ") for f in fields)


def _model_layer(default_model):
    """The model layer: every registry method, light->heavy, glossed, default marked."""
    layer = []
    for mid in MODEL_ORDER:
        info = _METHODS[mid]
        layer.append({
            "id": mid,
            "display_name": info["display_name"],
            "roster": info["default_roster_policy"],
            "gloss": _gloss(mid),
            "is_default": mid == default_model,
        })
    return layer


def _default_dissenter(model):
    """The default dissent occupant for a model (native rep or counter-lens), or None if
    the dissent module is unavailable. Used to decode roster/agent overrides."""
    try:
        import dissent
        occupant, _kind = dissent.default_occupant(model)
        return occupant
    except Exception:
        return None


def _seat_safe(model, customization=None):
    """Seat the dissenter for model with an optional customization, or None on failure.

    A dissent-module fault must not take /advise-full down — the caller then names the
    fixed counter-lens and flags dissent_degraded, mirroring advise_autopick.
    """
    try:
        import dissent
        return dissent.seat_dissenter(model, customization)
    except Exception:
        return None


def build_menu(draft, signals=None, session_id=None, channel_id="adhoc"):
    """Compute the pre-selected /advise-full menu. Writes NO record.

    Reuses ``advise_autopick.plan_run`` for the classifier pick + dissent seating (no
    forked logic), then wraps it in the menu shape. The returned payload is model-first
    with the roster COLLAPSED (a scalar) and the agent pool HIDDEN (absent from the
    payload; reach it via ``agent_options``). It contains NO round/synthesis knob.

    Returns a dict:
      {
        "recommended_model": str|None,  # classifier pick; None when fell_back
        "selected_model":    str,       # the PRE-SELECTED default (== recommended, or the
                                        #   jixia fixed-pair floor on fallback)
        "roster":            str,       # COLLAPSED to selected_model's registry default
        "dissenter":         str,       # named up front (dissenter-named-on-entry)
        "dissent_prompt":    str|None,
        "mandatory":         True,
        "confidence":        int,       # classifier margin (0 on fallback)
        "fell_back":         bool,
        "dissent_degraded":  bool,
        "models":            list,      # the light->heavy model layer (glossed)
        "draft":             str,       # verbatim, byte-for-byte
        "session_id":        str,
        "channel_id":        str,
      }
    """
    plan = _ap.plan_run(draft, signals=signals, session_id=session_id,
                        channel_id=channel_id)
    return {
        "recommended_model": plan["record"]["recommended_model"],  # None iff fell_back
        "selected_model": plan["model"],
        "roster": plan["roster"],
        "dissenter": plan["dissenter"],
        "dissent_prompt": plan["dissent_prompt"],
        "mandatory": plan["mandatory"],
        "confidence": int(plan["confidence"]),
        "fell_back": plan["fell_back"],
        "dissent_degraded": plan["dissent_degraded"],
        "models": _model_layer(plan["model"]),
        "draft": draft,
        "session_id": session_id or "",
        "channel_id": channel_id or "adhoc",
    }


def roster_options(model):
    """The roster layer for a model, COLLAPSED by default and expanded on demand.

    The model's registry default first, then the orthogonal alternative when it is
    structurally available (a historical-default method can also be run practically;
    a practical-default method can be run historically only if it HAS historical reps).
    This is what makes the grid's orthogonality reachable via explicit override without
    ever showing the whole grid at once.
    """
    info = _METHODS[model]
    default = info["default_roster_policy"]
    opts = [default]
    if default == "historical":
        opts.append("practical")  # every method supports a question-driven practical mix
    elif info.get("historical_roster"):
        opts.append("historical")
    return opts


def agent_options(model, roster=None):
    """The HIDDEN third layer: the specific advisors selectable for a model+roster.

    Deliberately NOT part of ``build_menu`` — the skill surfaces this only when the user
    explicitly expands agent selection. Historical rosters expose the method's native
    reps plus the practical pool (a practical lens may be added); practical rosters
    expose the pool.
    """
    info = _METHODS[model]
    roster = roster or info["default_roster_policy"]
    reps = ([r["id"] for r in info.get("historical_roster", [])]
            if roster == "historical" else [])
    pool = sorted(_ap_real_agents())
    return {"historical_reps": reps, "practical_pool": pool}


def _ap_real_agents():
    """The advisor pool, via dissent's (layout-aware) resolver; empty if unavailable."""
    try:
        import dissent
        return dissent._real_agents()
    except Exception:
        return set()


def resolve_selection(draft, model=None, roster=None, agents=None,
                      dissent_occupant=None, remove_dissent=False,
                      signals=None, session_id=None, channel_id="adhoc"):
    """Resolve an accept OR an override into a dispatch plan + one ``routed`` record.

    All override args are optional; omitting them all is an ACCEPT of the pre-selected
    pick. The classifier is re-run (pure-deterministic, so the recommendation is stable)
    to recover ``recommended_model`` — the accept-vs-override anchor — then overrides are
    layered on:

      model            -> selected_model (differs from recommended => a model override);
                          resolved through registry aliases ("sages" -> "seven-sages"); a
                          truly unknown model degrades to the menu default and is surfaced
                          on the plan as ``model_override_unresolved`` (never a crash)
      roster           -> the roster that ran (defaults to selected model's registry policy)
      dissent_occupant -> swap WHO holds the dissent seat (routed through seat_dissenter)
      remove_dissent   -> a removal ATTEMPT; the seat is re-imposed (non-removable)
      agents           -> the specific advisors chosen (carried on the plan for dispatch)

    The record reuses ``advise_autopick.build_routed_record(entry="advise-full")`` — no
    new schema, no new field names. ``recommended_model`` stays null on a fell_back menu
    (excluded from accept-vs-override, same as /advise).

    Returns the menu-derived plan plus ``record`` (ready to append), ``agents`` (the
    specific advisors to dispatch, or None), and ``is_override``.
    """
    menu = build_menu(draft, signals=signals, session_id=session_id,
                      channel_id=channel_id)
    recommended = menu["recommended_model"]
    fell_back = menu["fell_back"]

    # Normalize a user-supplied model override through the registry aliases ("sages" ->
    # "seven-sages"). A truly unknown/typo'd model must NEVER crash the resolve snippet:
    # degrade to the menu's pre-selected default and flag the unresolved string so the
    # surface can tell the user it ran the default instead.
    model_override_unresolved = None
    if model:
        canonical = _canonical_model(model)
        if canonical is None:
            model_override_unresolved = model
            selected = menu["selected_model"]
        else:
            selected = canonical
    else:
        selected = menu["selected_model"]
    sel_roster = roster or _default_roster(selected)

    customization = {}
    if remove_dissent:
        customization["remove"] = True
    if dissent_occupant:
        customization["occupant"] = dissent_occupant

    dissent_degraded = menu["dissent_degraded"]
    seat = _seat_safe(selected, customization or None)
    if seat:
        dissenter = seat["occupant"]
        dissent_prompt = seat["prompt"]
        mandatory = seat["mandatory"]
        reinstated = seat.get("reinstated", False)
    else:
        # Dissent module absent/errored: never a decorative/empty seat. Name the fixed
        # counter-lens with the real directive and flag the degradation (mirrors /advise).
        dissenter = _ap.FALLBACK_COUNTER_LENS
        dissent_prompt = _ap.FALLBACK_DISSENT_DIRECTIVE
        mandatory = True
        reinstated = bool(remove_dissent or dissent_occupant)
        dissent_degraded = True

    record = _ap.build_routed_record(
        recommended_model=recommended, selected_model=selected, roster=sel_roster,
        dissenter=dissenter, confidence=menu["confidence"], draft=draft,
        session_id=session_id, channel_id=channel_id, fell_back=fell_back,
        dissent_degraded=dissent_degraded, entry=MENU_ENTRY,
    )

    plan = {
        "model": selected,
        "roster": sel_roster,
        "confidence": menu["confidence"],
        "dissenter": dissenter,
        "dissent_prompt": dissent_prompt,
        "mandatory": mandatory,
        "reinstated": reinstated,
        "fell_back": fell_back,
        "dissent_degraded": dissent_degraded,
        # On a fell_back menu the classifier stack was unavailable; carry the fixed pair
        # so the surface can still dispatch (identical to /advise's degraded path).
        "dispatch_pair": ([_ap.FALLBACK_PRIMARY, _ap.FALLBACK_COUNTER_LENS]
                          if fell_back else None),
        "agents": list(agents) if agents else None,
        "model_override_unresolved": model_override_unresolved,
        "draft": draft,
        "record": record,
    }
    plan["is_override"] = is_override(record)
    return plan


def is_override(record):
    """Decode a ``routed`` record's accept-vs-override status.

    Returns True (override), False (accept), or None (EXCLUDED from the rate). An override
    is EITHER a different model than the classifier recommended, OR the same model run with
    a non-default roster or a swapped dissenter — all three are visible against the selected
    model's registry defaults, so no new schema field is needed to tell them apart.

    This is the decoder emp.7's tally runs over an append-only, cross-version log, so it
    must NEVER raise and must not silently miscount legacy/hand-edited records. It returns
    None (excluded) rather than guessing whenever it cannot decide:
      - a non-dict / structurally invalid record;
      - a fell_back record (no classifier ran);
      - a null ``recommended_model`` (no classifier recommendation — not an override);
      - a ``selected_model`` absent or unknown to the CURRENT registry (cannot resolve its
        defaults, so roster/seat comparison is undefined).
    """
    if not isinstance(record, dict):
        return None
    if record.get("fell_back"):
        return None
    recommended = record.get("recommended_model")
    if recommended is None:
        # A null recommendation means no classifier ran — neither an accept nor an
        # override, whether or not fell_back was recorded (legacy/hand-edited records).
        return None
    selected = record.get("selected_model")
    sel_canon = _canonical_model(selected)
    if sel_canon is None:
        # selected_model missing, garbage, or from a different registry version — we
        # cannot resolve its default roster/seat, so we cannot classify it.
        return None
    # Model override: the classifier's pick differs from what ran. Compare canonically so
    # an alias vs its canonical id does not read as an override; an unresolvable
    # recommended model that differs from the resolvable selected one still counts.
    rec_canon = _canonical_model(recommended)
    if rec_canon is None or rec_canon != sel_canon:
        return True
    # Model accepted — check roster + dissent seat against the SELECTED model's defaults.
    if record.get("roster") != _default_roster(sel_canon):
        return True
    # A degraded seat (dissent seating FAILED — a system fault) names the fixed
    # counter-lens instead of the model's native/default seat; that is NOT a user
    # agent-override, so skip the seat comparison when dissent_degraded is set. Likewise
    # only compare when a dissenter is actually present — a missing/null dissenter in a
    # legacy record must not read as a phantom agent-override.
    if not record.get("dissent_degraded"):
        dissenter = record.get("dissenter")
        if dissenter is not None:
            default_seat = _default_dissenter(sel_canon)
            if default_seat is not None and dissenter != default_seat:
                return True
    return False
