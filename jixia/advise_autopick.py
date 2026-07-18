"""Auto-pick wiring for /advise (advisor-convening-router, emp.5).

The testable seam behind the ``/advise`` skill. It composes the two upstream
deterministic pieces into the single decision ``/advise`` auto-runs, every time,
with no menu:

  - the routing classifier (``routing_classifier.classify``, emp.3) picks the
    ``(model, roster, confidence)`` — a clear specialist, else the ``jixia``
    adaptive-triage default (never a fake-picked specialist), and
  - the mandated-dissent seating (``dissent.seat_dissenter``, emp.4) resolves WHO
    holds the non-removable dissent seat, so the skill can NAME the dissenter on
    the first turn.

The skill itself (``claude/skills/advise/SKILL.md``) states the pick + dissenter
and dispatches the model on the VERBATIM draft; this module makes the routing
decision, seats the dissenter, and writes ONE ``routed`` record to the counsel log.

Fail-safe (the load-bearing robustness property): if the classifier is ABSENT
(module never installed) or ERRORS, ``/advise`` must still act — it degrades to the
advisor-routing skeleton's fixed org-dynamics pair (``behavioral-psychologist`` +
``manager-tools-advisor``) rather than hard-failing. A classifier error must never
take ``/advise`` down.

The ``routed`` record SHARES ONE schema with the ``/advise-full`` override record
(emp.6). The accept-vs-override routing-quality signal is exactly
``recommended_model == selected_model`` (an auto-pick is an *accept*; an override
sets them differently). Do NOT coin divergent field names — emp.6 joins on these.

Stdlib-only. The classifier + dissent modules are imported LAZILY (inside the
call) so their absence degrades gracefully instead of breaking import here.
"""

import datetime
import hashlib
import json
import os

# --- shared routed-record schema (auto-pick AND override) ------------------------
# See specs/convening-routing/spec.md #routing-decisions-are-logged. These names are
# the cross-bead contract with /advise-full (emp.6): the override record reuses this
# exact shape, differing only in that selected_model != recommended_model. Renaming
# any of these breaks the accept-vs-override join.
ROUTED_KIND = "routed"

# Fixed fallback pair — the advisor-routing skeleton default for an outward message
# with org-dynamics stakes. Used ONLY when the classifier is absent/errors. The
# counter-lens doubles as the named dissenter in that degraded mode.
FALLBACK_MODEL = "jixia"          # the adaptive default floor (a real registry id)
FALLBACK_ROSTER = "practical"
FALLBACK_PRIMARY = "behavioral-psychologist"
FALLBACK_COUNTER_LENS = "manager-tools-advisor"

# The fallback / degraded-seating dissenter still gets a REAL low-sycophancy directive
# — a degraded run must not silently drop the dissent mandate (the seat's whole point),
# leaving a decorative dissenter. Kept inline (not imported from dissent) so it holds
# even when the dissent module is the thing that's absent.
FALLBACK_DISSENT_DIRECTIVE = (
    "You hold the mandated dissent seat. Argue the strongest counter-case against the "
    "emerging consensus, resist agreeing for the sake of consensus, and do not soften "
    "your position in later rounds. You are FOR the user by refusing to be agreeable."
)

DEFAULT_LOG_PATH = os.path.expanduser("~/.claude/jixia/counsel-log.jsonl")


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _draft_hash(draft):
    """sha256 of the VERBATIM draft — evidence the exact artifact was routed.

    ``surrogatepass`` so a draft carrying a lone surrogate (e.g. from a bad paste)
    hashes deterministically instead of raising UnicodeEncodeError out of plan_run —
    the always-returns-a-plan invariant must hold for ANY str.
    """
    return hashlib.sha256((draft or "").encode("utf-8", "surrogatepass")).hexdigest()


def _classify_safe(draft, signals):
    """Return (classifier_result | None, fell_back: bool).

    Imports + calls the classifier lazily so a missing module (never installed) OR a
    raising classifier degrades to the fixed pair instead of hard-failing /advise.
    Any exception — ImportError, or a bug inside classify — is caught: a classifier
    fault must never take /advise down.
    """
    try:
        import routing_classifier
        return routing_classifier.classify(draft, signals), False
    except Exception:
        return None, True


def _seat_safe(model):
    """Seat the dissenter for model, or None if the dissent module is absent/errors.

    Named on the first turn by the skill. A dissent-module fault must not take
    /advise down either — the caller falls back to naming the counter-lens.
    """
    try:
        import dissent
        return dissent.seat_dissenter(model)
    except Exception:
        return None


def build_routed_record(recommended_model, selected_model, roster, dissenter,
                        confidence, draft, session_id, channel_id,
                        fell_back=False, dissent_degraded=False, entry="advise"):
    """Build the shared routing-decision record (auto-pick OR override).

    recommended_model = what the classifier picked; selected_model = what actually
    ran. They are EQUAL for an auto-pick (an accept) and differ for an override
    (emp.6). accept-vs-override is computed from exactly these two fields — BUT joins
    MUST exclude ``fell_back == True`` records: no classifier ran on those, so
    ``recommended_model`` is null and they are neither an accept nor an override.

    dissent_degraded = the classifier ran but dissent seating failed; the run still
    named a real counter-lens with a real directive (never dropped), but the seat is
    NOT the model's native/resolved one. Additive to the schema (default False).
    """
    return {
        "kind": ROUTED_KIND,
        "ts": _now_iso(),
        "session_id": session_id or "",
        "channel_id": channel_id or "adhoc",
        "entry": entry,
        "recommended_model": recommended_model,   # null when no classifier ran (fell_back)
        "selected_model": selected_model,
        "roster": roster,
        "dissenter": dissenter,
        "confidence": int(confidence),
        "draft_hash": _draft_hash(draft),
        "fell_back": bool(fell_back),
        "dissent_degraded": bool(dissent_degraded),
    }


def plan_run(draft, signals=None, session_id=None, channel_id="adhoc"):
    """Compute the full /advise auto-pick plan. ALWAYS returns a dispatchable plan.

    The draft is carried VERBATIM (never summarized/normalized) so the dispatched
    advisors and the record hash the exact artifact — the anti-horoscope guarantee.

    Returns a dict:
      {
        "model":         str,       # the model to run (== selected_model)
        "roster":        str,       # its roster policy
        "confidence":    int,       # classifier margin (0 when fell_back)
        "dissenter":     str,       # WHO holds the dissent seat — named on turn 1
        "dissent_prompt":str|None,  # the low-sycophancy directive set (None if degraded)
        "mandatory":     bool,      # the seat is non-removable
        "fell_back":     bool,      # True iff the classifier was absent/errored
        "dissent_degraded": bool,   # classifier ran but dissent seating failed (seat not native)
        "dispatch_pair": [str,str]|None,  # the fixed pair to dispatch when fell_back
        "draft":         str,       # the VERBATIM draft, byte-for-byte unchanged
        "record":        dict,      # the routed record, ready to append
      }
    """
    result, fell_back = _classify_safe(draft, signals)
    dissent_degraded = False

    if fell_back or not result:
        # Degraded mode: the classifier is absent or errored. Run the skeleton's fixed
        # org-dynamics pair. The record tells the truth about what ran:
        # recommended_model is None (no classifier recommendation happened);
        # selected_model is the jixia practical default the fixed pair implements;
        # fell_back=True is the discriminator (joins exclude these). The fallback
        # dissenter still carries a real counter-case directive — not decorative.
        recommended = None
        model = FALLBACK_MODEL
        roster = FALLBACK_ROSTER
        confidence = 0
        dissenter = FALLBACK_COUNTER_LENS
        dissent_prompt = FALLBACK_DISSENT_DIRECTIVE
        mandatory = True
        dispatch_pair = [FALLBACK_PRIMARY, FALLBACK_COUNTER_LENS]
        fell_back = True
    else:
        recommended = result["model"]
        model = result["model"]
        roster = result["roster"]
        confidence = result["confidence"]
        seat = _seat_safe(model)
        if seat:
            dissenter = seat["occupant"]
            dissent_prompt = seat["prompt"]
            mandatory = seat["mandatory"]
        else:
            # The classifier ran but dissent seating FAILED. This is NOT a classifier
            # fallback (fell_back stays False) — it is a distinct degradation, flagged
            # explicitly so the log does not read as a clean accept with the seat
            # silently dropped. Still name a real counter-lens with a real directive.
            dissenter = FALLBACK_COUNTER_LENS
            dissent_prompt = FALLBACK_DISSENT_DIRECTIVE
            mandatory = True
            dissent_degraded = True
        dispatch_pair = None
        fell_back = False

    record = build_routed_record(
        recommended_model=recommended, selected_model=model, roster=roster,
        dissenter=dissenter, confidence=confidence, draft=draft,
        session_id=session_id, channel_id=channel_id, fell_back=fell_back,
        dissent_degraded=dissent_degraded, entry="advise",
    )

    return {
        "model": model,
        "roster": roster,
        "confidence": int(confidence),
        "dissenter": dissenter,
        "dissent_prompt": dissent_prompt,
        "mandatory": mandatory,
        "fell_back": fell_back,
        "dissent_degraded": dissent_degraded,
        "dispatch_pair": dispatch_pair,
        "draft": draft,
        "record": record,
    }


def append_record(record, log_path=None):
    """Append one routed record as a JSON line to the counsel log (creating the dir).

    Append-only, one object per line — the same JSONL contract the hook + counseled
    record write to. Returns the record for convenience.
    """
    path = log_path or DEFAULT_LOG_PATH
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record
