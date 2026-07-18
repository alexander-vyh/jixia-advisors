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

DEFAULT_LOG_PATH = os.path.expanduser("~/.claude/jixia/counsel-log.jsonl")


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _draft_hash(draft):
    """sha256 of the VERBATIM draft — evidence the exact artifact was routed."""
    return hashlib.sha256((draft or "").encode("utf-8")).hexdigest()


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
                        fell_back=False, entry="advise"):
    """Build the shared routing-decision record (auto-pick OR override).

    recommended_model = what the classifier picked; selected_model = what actually
    ran. They are EQUAL for an auto-pick (an accept) and differ for an override
    (emp.6). accept-vs-override is computed from exactly these two fields.
    """
    return {
        "kind": ROUTED_KIND,
        "ts": _now_iso(),
        "session_id": session_id or "",
        "channel_id": channel_id or "adhoc",
        "entry": entry,
        "recommended_model": recommended_model,
        "selected_model": selected_model,
        "roster": roster,
        "dissenter": dissenter,
        "confidence": int(confidence),
        "draft_hash": _draft_hash(draft),
        "fell_back": bool(fell_back),
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
        "dispatch_pair": [str,str]|None,  # the fixed pair to dispatch when fell_back
        "draft":         str,       # the VERBATIM draft, byte-for-byte unchanged
        "record":        dict,      # the routed record, ready to append
      }
    """
    result, fell_back = _classify_safe(draft, signals)

    if fell_back or not result:
        # Degraded mode: the classifier is absent or errored. Run the skeleton's
        # fixed org-dynamics pair; name the counter-lens as the dissenter.
        model = FALLBACK_MODEL
        roster = FALLBACK_ROSTER
        confidence = 0
        dissenter = FALLBACK_COUNTER_LENS
        dissent_prompt = None
        mandatory = True
        dispatch_pair = [FALLBACK_PRIMARY, FALLBACK_COUNTER_LENS]
        fell_back = True
    else:
        model = result["model"]
        roster = result["roster"]
        confidence = result["confidence"]
        seat = _seat_safe(model)
        if seat:
            dissenter = seat["occupant"]
            dissent_prompt = seat["prompt"]
            mandatory = seat["mandatory"]
        else:
            # Classifier worked but dissent seating failed: still name a real seat so
            # the dissenter is present on turn 1 (the invariant must not silently drop).
            dissenter = FALLBACK_COUNTER_LENS
            dissent_prompt = None
            mandatory = True
        dispatch_pair = None
        fell_back = False

    record = build_routed_record(
        recommended_model=model, selected_model=model, roster=roster,
        dissenter=dissenter, confidence=confidence, draft=draft,
        session_id=session_id, channel_id=channel_id, fell_back=fell_back,
        entry="advise",
    )

    return {
        "model": model,
        "roster": roster,
        "confidence": int(confidence),
        "dissenter": dissenter,
        "dissent_prompt": dissent_prompt,
        "mandatory": mandatory,
        "fell_back": fell_back,
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
