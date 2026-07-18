"""TDD suite for the /advise auto-run wiring (advisor-convening-router, emp.5).

Brief: .agent/runtime/test-oracle-brief.md
Spec:  openspec/changes/advisor-convening-router/specs/convening-routing/spec.md
       (advise-auto-runs-the-pick, never-guesses-…, routing-decisions-are-logged)
       openspec/changes/advisor-convening-router/specs/mandated-dissent/spec.md
       (dissenter-named-on-entry)

These tests assert the real-world OUTCOMES of the acceptance criteria, not the
module's call structure:

  - the classifier's returned model is what runs (not a hardcoded pair);
  - the VERBATIM draft is carried byte-for-byte and the record hash is over it;
  - a dissenter is always named for turn 1;
  - a classifier ABSENCE and a classifier ERROR both degrade to the fixed pair
    (they must NOT propagate out of /advise);
  - one shared-schema `routed` record is produced, and recommended==selected on an
    auto-pick (the accept-vs-override join key /advise-full/emp.6 reuses).

The shared-schema field names are declared INDEPENDENTLY here (not imported from
the module) so the record contract and the implementation cannot silently drift —
the same discipline test_routing_classifier.py uses for its output contract.
"""

import hashlib
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import advise_autopick as ap  # noqa: E402
import routing_classifier as rc  # noqa: E402  (present in-repo; absence is simulated)

# --- Independently-declared shared-schema contract (NOT imported from the module) ---
# The routed record is the accept-vs-override join surface emp.6 reuses. The two
# load-bearing fields are recommended_model and selected_model; the rest are the
# correlation/evidence carrier. Declared here so a rename in the module fails a test.
ROUTED_REQUIRED_KEYS = {
    "kind", "ts", "session_id", "channel_id", "entry",
    "recommended_model", "selected_model", "roster", "dissenter",
    "confidence", "draft_hash", "fell_back",
}

# Clean per-specialist positive from the classifier brief (§R-M3): a textbook audit.
AUDIT_DRAFT = ("Audit this rollout for failure modes — what broke, what's the root "
               "cause, and who owns it?")
# The native yushitai dissent seat (mandated-dissent, dissent-resolves-to-a-real-occupant).
YUSHITAI_NATIVE_DISSENTER = "discipline-impeachment-censor"

# Ambiguous everyday ask → the jixia default floor (brief §R-M7).
EVERYDAY_DRAFT = "Thoughts on how I framed this? Just want a sanity check."


def _sha(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


class AutoPickTestCase(unittest.TestCase):
    """Base: isolates the counsel log to a temp file and restores sys.modules."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(self._tmp.name, "counsel-log.jsonl")
        self._saved_rc = sys.modules.get("routing_classifier")
        self._saved_classify = getattr(rc, "classify", None)

    def tearDown(self):
        # Restore the classifier module + its classify to a pristine state.
        if self._saved_rc is not None:
            sys.modules["routing_classifier"] = self._saved_rc
        if self._saved_classify is not None:
            rc.classify = self._saved_classify
        self._tmp.cleanup()


class TestClassifierIsCalledAndItsPickRuns(AutoPickTestCase):
    """advise-auto-runs-the-pick: the classifier's model is what runs (not a fixed pair)."""

    def test_classify_is_invoked_with_the_draft(self):
        seen = {}
        original = rc.classify

        def spy(draft, signals=None):
            seen["draft"] = draft
            return original(draft, signals)

        rc.classify = spy
        plan = ap.plan_run(AUDIT_DRAFT)
        self.assertEqual(seen.get("draft"), AUDIT_DRAFT,
                         "classify() must be called with the draft")
        self.assertFalse(plan["fell_back"])

    def test_clean_specialist_draft_runs_that_specialist(self):
        # FRAGILE "always the fixed pair": an audit must route to yushitai, both in
        # the plan and in the record — not to a hardcoded behavioral/manager pair.
        plan = ap.plan_run(AUDIT_DRAFT)
        self.assertEqual(plan["model"], "yushitai")
        self.assertEqual(plan["roster"], "historical")
        self.assertEqual(plan["record"]["recommended_model"], "yushitai")
        self.assertEqual(plan["record"]["selected_model"], "yushitai")

    def test_ambiguous_draft_falls_to_jixia_and_still_acts(self):
        plan = ap.plan_run(EVERYDAY_DRAFT)
        self.assertEqual(plan["model"], "jixia")
        self.assertEqual(plan["roster"], "practical")
        self.assertFalse(plan["fell_back"], "jixia default is not a fallback — it acted")


class TestVerbatimDraftPassthrough(AutoPickTestCase):
    """counsel-grounding / anti-horoscope: the exact draft is carried, and hashed."""

    def test_draft_is_byte_for_byte_unchanged(self):
        draft = "  Leading + trailing space, emoji 🙂, and\na newline.  "
        plan = ap.plan_run(draft)
        self.assertEqual(plan["draft"], draft,
                         "the draft must pass through verbatim (no strip/normalize)")

    def test_record_hash_is_over_the_verbatim_draft(self):
        draft = "  Leading + trailing space, emoji 🙂, and\na newline.  "
        plan = ap.plan_run(draft)
        self.assertEqual(plan["record"]["draft_hash"], _sha(draft),
                         "draft_hash must be sha256 of the exact input, not a summary")


class TestDissenterNamedOnEntry(AutoPickTestCase):
    """dissenter-named-on-entry: every run names a real dissenter for turn 1."""

    def test_specialist_uses_its_native_dissenter(self):
        plan = ap.plan_run(AUDIT_DRAFT)
        self.assertEqual(plan["dissenter"], YUSHITAI_NATIVE_DISSENTER)
        self.assertTrue(plan["mandatory"])
        self.assertEqual(plan["record"]["dissenter"], YUSHITAI_NATIVE_DISSENTER)

    def test_dissenter_is_never_empty(self):
        for draft in (AUDIT_DRAFT, EVERYDAY_DRAFT, "", "   "):
            with self.subTest(draft=draft[:24]):
                plan = ap.plan_run(draft)
                self.assertTrue(plan["dissenter"],
                                "a dissenter must always be named on turn 1")


class TestClassifierAbsenceDegrades(AutoPickTestCase):
    """never hard-fail: an ABSENT classifier degrades to the fixed pair."""

    def test_absent_classifier_falls_back_without_crashing(self):
        # sys.modules[name] = None makes `import name` raise ImportError — the exact
        # runtime shape of "the classifier was never installed".
        sys.modules["routing_classifier"] = None
        plan = ap.plan_run(AUDIT_DRAFT)  # must NOT raise
        self.assertTrue(plan["fell_back"])
        self.assertEqual(plan["model"], ap.FALLBACK_MODEL)
        self.assertEqual(
            plan["dispatch_pair"],
            [ap.FALLBACK_PRIMARY, ap.FALLBACK_COUNTER_LENS],
            "an absent classifier must dispatch the skeleton's fixed pair",
        )
        self.assertEqual(plan["dissenter"], ap.FALLBACK_COUNTER_LENS)


class TestClassifierErrorDegrades(AutoPickTestCase):
    """never hard-fail: a classifier that RAISES degrades to the fixed pair."""

    def test_raising_classifier_falls_back_without_crashing(self):
        def boom(draft, signals=None):
            raise RuntimeError("classifier is broken")

        rc.classify = boom
        plan = ap.plan_run(AUDIT_DRAFT)  # must NOT raise
        self.assertTrue(plan["fell_back"])
        self.assertEqual(plan["model"], ap.FALLBACK_MODEL)
        self.assertEqual(plan["record"]["fell_back"], True)


class TestRoutedRecordSchema(AutoPickTestCase):
    """routing-decisions-are-logged: one shared-schema record, accept semantics."""

    def test_record_has_exactly_the_shared_schema_keys(self):
        rec = ap.plan_run(AUDIT_DRAFT)["record"]
        self.assertEqual(set(rec), ROUTED_REQUIRED_KEYS,
                         "routed record keys must be exactly the shared schema")
        self.assertEqual(rec["kind"], "routed")
        self.assertEqual(rec["entry"], "advise")

    def test_autopick_is_an_accept_recommended_equals_selected(self):
        # The accept-vs-override join key: an auto-pick records recommended==selected.
        rec = ap.plan_run(AUDIT_DRAFT)["record"]
        self.assertEqual(rec["recommended_model"], rec["selected_model"],
                         "an auto-pick must record recommended==selected (an accept)")

    def test_confidence_is_an_int(self):
        rec = ap.plan_run(AUDIT_DRAFT)["record"]
        self.assertIsInstance(rec["confidence"], int)

    def test_session_id_recorded_from_argument_and_empty_is_allowed(self):
        rec = ap.plan_run(AUDIT_DRAFT, session_id="sess-xyz", channel_id="C1")["record"]
        self.assertEqual(rec["session_id"], "sess-xyz")
        self.assertEqual(rec["channel_id"], "C1")
        rec2 = ap.plan_run(AUDIT_DRAFT)["record"]
        self.assertEqual(rec2["session_id"], "")  # empty is allowed, not a refusal
        self.assertEqual(rec2["channel_id"], "adhoc")


class TestAppendRecordRoundTrips(AutoPickTestCase):
    """The record actually lands on disk as one parseable JSONL line."""

    def test_append_writes_one_parseable_line(self):
        plan = ap.plan_run(AUDIT_DRAFT, session_id="S1", channel_id="C1")
        ap.append_record(plan["record"], log_path=self.log_path)
        ap.append_record(plan["record"], log_path=self.log_path)  # append-only
        with open(self.log_path, encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        self.assertEqual(len(lines), 2)
        back = json.loads(lines[0])
        self.assertEqual(back["kind"], "routed")
        self.assertEqual(back["selected_model"], "yushitai")

    def test_append_creates_missing_dir(self):
        nested = os.path.join(self._tmp.name, "a", "b", "counsel-log.jsonl")
        ap.append_record(ap.plan_run(EVERYDAY_DRAFT)["record"], log_path=nested)
        self.assertTrue(os.path.exists(nested))


class TestRoutedRecordIgnoredByCounselReport(AutoPickTestCase):
    """The new `routed` kind must not pollute the keep/kill report's join, which only
    consumes bounced/counseled/restaged — routed is a separate (routing-quality) signal."""

    def test_report_does_not_count_routed_as_bounce_or_counsel(self):
        import importlib.machinery
        import importlib.util
        repo = os.path.dirname(HERE)
        loader = importlib.machinery.SourceFileLoader(
            "jixia_counsel_report", os.path.join(repo, "bin", "jixia-counsel-report"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        rep = importlib.util.module_from_spec(spec)
        loader.exec_module(rep)

        rec = ap.plan_run(AUDIT_DRAFT, session_id="S1", channel_id="C1")["record"]
        report = rep.compute_report([rec])
        self.assertEqual(report["bounces"], 0)
        self.assertEqual(report["counseled_pairs"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
