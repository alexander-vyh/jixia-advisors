"""TDD suite for the /advise-full menu + override seam (advisor-convening-router, emp.6).

Brief: .agent/runtime/test-oracle-brief.md
Spec:  openspec/changes/advisor-convening-router/specs/convening-routing/spec.md
       (advise-full-presents-a-pick-preselected-menu, round-count-and-synthesis-not-exposed,
        routing-decisions-are-logged — override scenario)
       openspec/changes/advisor-convening-router/specs/mandated-dissent/spec.md
       (dissenter-named-on-entry, dissent-is-non-removable)

These tests assert the real-world OUTCOMES of the acceptance criteria, not call shape:

  - the menu pre-selects the classifier's pick, names the dissenter, orders models
    light->heavy with output-shape glosses, and exposes NO round/synthesis knob;
  - the roster is collapsed to the model's registry default and the agent pool is NOT
    embedded in the menu payload (the grid is never shown at once);
  - an ACCEPT logs recommended==selected (entry advise-full);
  - a model OVERRIDE logs recommended!=selected with the overridden model;
  - a roster/agent override is STILL distinguishable from an accept (is_override);
  - an agent-swap/removal override keeps a real, mandatory dissenter (non-removable seat).

The shared-schema field names are declared INDEPENDENTLY here (not imported from the
module) so the record contract and the implementation cannot silently drift.
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

import advise_full as af  # noqa: E402
import advise_autopick as ap  # noqa: E402
import routing_classifier as rc  # noqa: E402  (absence/error simulated)
import dissent as ds  # noqa: E402

# Independently-declared shared-schema contract — a rename in the module fails a test.
ROUTED_REQUIRED_KEYS = {
    "kind", "ts", "session_id", "channel_id", "entry",
    "recommended_model", "selected_model", "roster", "dissenter",
    "confidence", "draft_hash", "fell_back", "dissent_degraded",
}

# Clean per-specialist positives (same fixtures the emp.5 suite uses).
AUDIT_DRAFT = ("Audit this rollout for failure modes — what broke, what's the root "
               "cause, and who owns it?")
YUSHITAI_NATIVE_DISSENTER = "discipline-impeachment-censor"
EVERYDAY_DRAFT = "Thoughts on how I framed this? Just want a sanity check."

# Tokens that would betray a leaked round-count / synthesis-method knob.
FORBIDDEN_KNOB_TOKENS = ("round", "synthesis", "synthesize")


def _sha(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


class AdviseFullTestCase(unittest.TestCase):
    """Isolates the counsel log and restores the classifier/dissent modules."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(self._tmp.name, "counsel-log.jsonl")
        self._saved_rc = sys.modules.get("routing_classifier")
        self._saved_classify = getattr(rc, "classify", None)
        self._saved_seat = getattr(ds, "seat_dissenter", None)

    def tearDown(self):
        if self._saved_rc is not None:
            sys.modules["routing_classifier"] = self._saved_rc
        if self._saved_classify is not None:
            rc.classify = self._saved_classify
        if self._saved_seat is not None:
            ds.seat_dissenter = self._saved_seat
        self._tmp.cleanup()


class TestMenuPreselectsThePick(AdviseFullTestCase):
    """advise-full-presents-a-pick-preselected-menu: the classifier pick is the default."""

    def test_menu_preselects_the_classifier_model_and_names_the_dissenter(self):
        menu = af.build_menu(AUDIT_DRAFT)
        self.assertEqual(menu["selected_model"], "yushitai")
        self.assertEqual(menu["recommended_model"], "yushitai")
        self.assertEqual(menu["roster"], "historical")
        # dissenter-named-on-entry: the seat is named in the menu payload.
        self.assertEqual(menu["dissenter"], YUSHITAI_NATIVE_DISSENTER)
        self.assertTrue(menu["mandatory"])

    def test_default_model_is_marked_in_the_model_layer(self):
        menu = af.build_menu(AUDIT_DRAFT)
        defaults = [m["id"] for m in menu["models"] if m["is_default"]]
        self.assertEqual(defaults, ["yushitai"], "exactly the pick is pre-selected")

    def test_ambiguous_draft_preselects_jixia_floor(self):
        menu = af.build_menu(EVERYDAY_DRAFT)
        self.assertEqual(menu["selected_model"], "jixia")
        self.assertFalse(menu["fell_back"], "jixia default is a real pick, not a fallback")


class TestMenuShapeModelFirstCollapsedHidden(AdviseFullTestCase):
    """Model-first; roster collapsed to the registry default; agent pool hidden; the full
    model×roster×agent grid is never emitted at once."""

    def test_all_six_models_present_light_to_heavy_with_glosses(self):
        menu = af.build_menu(AUDIT_DRAFT)
        ids = [m["id"] for m in menu["models"]]
        self.assertEqual(ids, af.MODEL_ORDER, "model layer is the pinned light->heavy order")
        self.assertEqual(set(ids), set(af._METHODS), "every registry method is offered")
        for m in menu["models"]:
            self.assertTrue(m["gloss"].strip(), "each model carries an output-shape gloss")
            # The gloss is derived from the registry output_fields (kept in sync).
            self.assertEqual(m["gloss"], af._gloss(m["id"]))

    def test_roster_is_collapsed_to_a_single_default_scalar(self):
        menu = af.build_menu(AUDIT_DRAFT)
        self.assertEqual(menu["roster"], "historical")
        self.assertIsInstance(menu["roster"], str, "roster is collapsed, not a list/grid")

    def test_agent_pool_is_not_embedded_in_the_menu_payload(self):
        # The agent layer is hidden: the specific-advisor pool must not appear in the
        # pre-expanded menu. Assert no advisor names ride along in the payload.
        menu = af.build_menu(AUDIT_DRAFT)
        blob = json.dumps(menu)
        self.assertNotIn("practical_pool", blob)
        self.assertNotIn("ceo-advisor", blob, "the agent pool must stay a hidden layer")

    def test_no_round_or_synthesis_knob_in_the_menu_payload(self):
        # round-count-and-synthesis-not-exposed: no such SELECTABLE option in the menu.
        # Scan the option-bearing surface (menu keys + the model layer + the roster
        # scalar) — NOT the dissent directive prose, which legitimately says "later
        # rounds" (the debate has internal, capped rounds; that is not a user knob).
        menu = af.build_menu(AUDIT_DRAFT)
        option_surface = json.dumps({
            "keys": sorted(menu.keys()),
            "models": menu["models"],
            "roster": menu["roster"],
        }).lower()
        for tok in FORBIDDEN_KNOB_TOKENS:
            self.assertNotIn(tok, option_surface, "menu must expose no %r knob" % tok)
        # And no top-level menu key is a rounds/synthesis knob.
        for key in menu:
            self.assertNotIn("round", key.lower())
            self.assertNotIn("synth", key.lower())


class TestMenuWritesNoRecord(AdviseFullTestCase):
    """Rendering the menu is not yet a routing decision — no record until the user resolves."""

    def test_build_menu_returns_no_record_key(self):
        menu = af.build_menu(AUDIT_DRAFT)
        self.assertNotIn("record", menu, "build_menu must not fabricate a routed record")


class TestAcceptLogsAnAccept(AdviseFullTestCase):
    """routing-decisions-are-logged: an accept records recommended==selected, entry advise-full."""

    def test_accept_record_is_recommended_equals_selected(self):
        plan = af.resolve_selection(AUDIT_DRAFT)
        rec = plan["record"]
        self.assertEqual(set(rec), ROUTED_REQUIRED_KEYS, "reuses the shared schema exactly")
        self.assertEqual(rec["kind"], "routed")
        self.assertEqual(rec["entry"], "advise-full")
        self.assertEqual(rec["recommended_model"], "yushitai")
        self.assertEqual(rec["selected_model"], "yushitai")
        self.assertEqual(rec["recommended_model"], rec["selected_model"])
        self.assertFalse(plan["is_override"], "an unchanged pick is an accept")
        self.assertEqual(af.is_override(rec), False)

    def test_accept_carries_verbatim_draft_hash(self):
        draft = "  spacey draft, emoji 🙂 and\na newline  "
        rec = af.resolve_selection(draft)["record"]
        self.assertEqual(rec["draft_hash"], _sha(draft))


class TestModelOverrideIsDistinct(AdviseFullTestCase):
    """override the model: recommended!=selected — the primary accept-vs-override signal."""

    def test_model_override_records_recommended_not_equal_selected(self):
        plan = af.resolve_selection(AUDIT_DRAFT, model="areopagus")
        rec = plan["record"]
        self.assertEqual(rec["recommended_model"], "yushitai", "classifier's pick preserved")
        self.assertEqual(rec["selected_model"], "areopagus", "the user's override ran")
        self.assertNotEqual(rec["recommended_model"], rec["selected_model"])
        self.assertTrue(plan["is_override"])
        self.assertEqual(af.is_override(rec), True)

    def test_override_reseats_the_selected_models_native_dissenter(self):
        # Overriding yushitai -> areopagus must seat areopagus's native dissenter, not
        # yushitai's — the seat follows the model that actually runs.
        plan = af.resolve_selection(AUDIT_DRAFT, model="areopagus")
        self.assertEqual(plan["dissenter"], "ephialtean-power-limiter")
        self.assertEqual(plan["roster"], "historical")
        self.assertTrue(plan["mandatory"])

    def test_override_and_accept_land_as_two_distinguishable_log_lines(self):
        # The end-to-end done-bar: accept and override are separable in the log.
        af.append_record(af.resolve_selection(AUDIT_DRAFT)["record"], log_path=self.log_path)
        af.append_record(af.resolve_selection(AUDIT_DRAFT, model="junto")["record"],
                         log_path=self.log_path)
        with open(self.log_path, encoding="utf-8") as f:
            recs = [json.loads(ln) for ln in f if ln.strip()]
        self.assertEqual(len(recs), 2)
        statuses = [af.is_override(r) for r in recs]
        self.assertEqual(statuses, [False, True], "one accept, one override — computable")


class TestRosterOverrideIsDistinct(AdviseFullTestCase):
    """A roster override keeps the model but must NOT read as a clean accept."""

    def test_roster_override_is_detected_though_model_unchanged(self):
        # yushitai's registry default is historical; run it practically instead.
        plan = af.resolve_selection(AUDIT_DRAFT, roster="practical")
        rec = plan["record"]
        self.assertEqual(rec["selected_model"], "yushitai")
        self.assertEqual(rec["recommended_model"], "yushitai")
        self.assertEqual(rec["roster"], "practical", "the overridden roster is recorded")
        self.assertTrue(plan["is_override"], "a roster override is not an accept")
        self.assertEqual(af.is_override(rec), True)


class TestAgentOverrideKeepsADissenter(AdviseFullTestCase):
    """dissent-is-non-removable: swapping/removing the dissent seat via an agent override
    must still yield a real, mandatory dissenter."""

    def test_dissent_swap_to_a_real_agent_is_honored(self):
        plan = af.resolve_selection(EVERYDAY_DRAFT, dissent_occupant="ceo-advisor")
        self.assertEqual(plan["dissenter"], "ceo-advisor")
        self.assertTrue(plan["mandatory"])
        self.assertTrue(plan["is_override"], "a dissent swap is an override")

    def test_removal_attempt_reimposes_a_real_dissenter(self):
        plan = af.resolve_selection(EVERYDAY_DRAFT, remove_dissent=True)
        self.assertTrue(plan["dissenter"], "the seat is non-removable — a dissenter remains")
        self.assertTrue(plan["mandatory"])
        self.assertTrue(plan["reinstated"], "a removal attempt is reinstated")
        # And the record still carries a real dissenter, never an empty seat.
        self.assertTrue(plan["record"]["dissenter"])

    def test_invalid_swap_reseats_the_default(self):
        plan = af.resolve_selection(AUDIT_DRAFT, dissent_occupant="council-of-elrond")
        self.assertNotEqual(plan["dissenter"], "council-of-elrond")
        self.assertEqual(plan["dissenter"], YUSHITAI_NATIVE_DISSENTER,
                         "an unresolvable swap reinstates the native default")


class TestFallbackMenuDegrades(AdviseFullTestCase):
    """Classifier absent -> the menu still renders; an accept of it is excluded from the
    accept-vs-override rate (recommended_model null)."""

    def test_absent_classifier_menu_and_accept(self):
        sys.modules["routing_classifier"] = None
        menu = af.build_menu(AUDIT_DRAFT)  # must NOT raise
        self.assertTrue(menu["fell_back"])
        self.assertIsNone(menu["recommended_model"])
        self.assertEqual(menu["selected_model"], ap.FALLBACK_MODEL)
        rec = af.resolve_selection(AUDIT_DRAFT)["record"]
        self.assertTrue(rec["fell_back"])
        self.assertIsNone(rec["recommended_model"])
        self.assertIsNone(af.is_override(rec), "fell_back is excluded from accept-vs-override")


class TestDissentDegradedFlagged(AdviseFullTestCase):
    """Classifier runs but dissent seating fails: never a decorative seat; degradation flagged."""

    def test_seat_failure_flags_degraded_and_keeps_a_real_dissenter(self):
        def boom(model, customization=None):
            raise RuntimeError("dissent module is broken")

        ds.seat_dissenter = boom
        plan = af.resolve_selection(AUDIT_DRAFT)
        self.assertFalse(plan["fell_back"])
        self.assertEqual(plan["record"]["selected_model"], "yushitai")
        self.assertTrue(plan["dissent_degraded"])
        self.assertTrue(plan["record"]["dissent_degraded"])
        self.assertEqual(plan["dissenter"], ap.FALLBACK_COUNTER_LENS)
        self.assertTrue(plan["dissent_prompt"], "a degraded seat still carries a real directive")
        self.assertTrue(plan["mandatory"])

    def test_degraded_accept_is_not_miscounted_as_an_agent_override(self):
        # The model was accepted; the seat degraded due to a SYSTEM fault (not a user
        # swap). is_override must not read the fallback counter-lens as an override.
        def boom(model, customization=None):
            raise RuntimeError("dissent module is broken")

        ds.seat_dissenter = boom
        plan = af.resolve_selection(AUDIT_DRAFT)  # a plain accept
        self.assertFalse(plan["is_override"], "a degraded-seat accept is still an accept")
        self.assertEqual(af.is_override(plan["record"]), False)


class TestVerbatimDraftPassthrough(AdviseFullTestCase):
    """anti-horoscope: the exact draft is carried through resolve, and hashed over."""

    def test_draft_is_byte_for_byte_unchanged(self):
        draft = "  Leading + trailing, emoji 🙂, and\na newline.  "
        plan = af.resolve_selection(draft, model="junto")
        self.assertEqual(plan["draft"], draft)
        self.assertEqual(plan["record"]["draft_hash"], _sha(draft))

    def test_lone_surrogate_draft_still_resolves_and_hashes(self):
        draft = "bad \ud800 surrogate"
        plan = af.resolve_selection(draft)  # must NOT raise
        h = plan["record"]["draft_hash"]
        self.assertEqual(len(h), 64)
        int(h, 16)


class TestIsOverrideNeverRaisesOnGarbage(AdviseFullTestCase):
    """is_override is the decoder emp.7's tally runs over an append-only, CROSS-VERSION
    log. It must never raise and must exclude (None) records it cannot decide."""

    def test_unknown_selected_model_is_excluded_not_a_crash(self):
        # recommended==selected==bogus reaches the roster/seat lookups — must not KeyError.
        rec = {"recommended_model": "bogus-model", "selected_model": "bogus-model",
               "roster": "practical", "dissenter": "x", "fell_back": False}
        self.assertIsNone(af.is_override(rec))

    def test_empty_dict_is_excluded(self):
        self.assertIsNone(af.is_override({}))

    def test_non_dict_record_is_excluded(self):
        for junk in (None, "routed", 42, ["selected_model"]):
            with self.subTest(junk=junk):
                self.assertIsNone(af.is_override(junk))

    def test_missing_keys_do_not_raise(self):
        self.assertIsNone(af.is_override({"selected_model": "yushitai"}))  # no recommended
        self.assertIsNone(af.is_override({"recommended_model": "yushitai"}))  # no selected


class TestIsOverrideDoesNotMiscountLegacyRecords(AdviseFullTestCase):
    """Finding 2: null recommendation and missing/null dissenter must not read as overrides."""

    def test_null_recommendation_without_fell_back_is_excluded(self):
        # A null recommendation means no classifier ran — NOT an override, even if the
        # fell_back flag is absent (a legacy/hand-edited record).
        rec = {"recommended_model": None, "selected_model": "yushitai",
               "roster": "historical", "dissenter": YUSHITAI_NATIVE_DISSENTER}
        self.assertIsNone(af.is_override(rec))

    def test_missing_or_null_dissenter_is_not_a_phantom_agent_override(self):
        base = {"recommended_model": "yushitai", "selected_model": "yushitai",
                "roster": "historical", "fell_back": False, "dissent_degraded": False}
        # dissenter absent entirely.
        self.assertFalse(af.is_override(dict(base)))
        # dissenter explicitly null.
        self.assertFalse(af.is_override(dict(base, dissenter=None)))

    def test_alias_recommended_vs_canonical_selected_is_an_accept(self):
        # A legacy record storing an alias must not read as a model override.
        rec = {"recommended_model": "sages", "selected_model": "seven-sages",
               "roster": "practical", "dissenter": None, "fell_back": False}
        self.assertFalse(af.is_override(rec))


class TestModelOverrideAliasAndUnknown(AdviseFullTestCase):
    """Finding 3: a model override resolves through registry aliases, and a truly unknown
    model degrades cleanly (no traceback out of resolve_selection)."""

    def test_alias_model_override_resolves_to_canonical(self):
        plan = af.resolve_selection(AUDIT_DRAFT, model="sages")
        self.assertEqual(plan["model"], "seven-sages", "'sages' is a registry alias")
        self.assertEqual(plan["record"]["selected_model"], "seven-sages")
        self.assertIsNone(plan["model_override_unresolved"])
        self.assertTrue(plan["is_override"])

    def test_unknown_model_override_degrades_to_the_menu_default(self):
        plan = af.resolve_selection(AUDIT_DRAFT, model="totally-bogus")  # must NOT raise
        self.assertEqual(plan["model"], "yushitai", "falls back to the pre-selected default")
        self.assertEqual(plan["model_override_unresolved"], "totally-bogus",
                         "the unresolved string is surfaced for the SKILL to report")
        self.assertTrue(plan["record"]["dissenter"], "a real dissenter is still seated")


class TestNoRoundsKnobInTheApiSurface(AdviseFullTestCase):
    """round-count-and-synthesis-not-exposed, enforced at the seam: the user cannot select
    a round count or synthesis method because the API has no parameter to express one."""

    def test_resolve_selection_has_no_rounds_or_synthesis_parameter(self):
        import inspect
        params = set(inspect.signature(af.resolve_selection).parameters)
        for p in params:
            self.assertNotIn("round", p.lower(), "no round-count knob in the override API")
            self.assertNotIn("synth", p.lower(), "no synthesis-method knob in the override API")
        # The override dimensions the seam DOES expose (and nothing more of that kind).
        self.assertTrue({"model", "roster", "agents", "dissent_occupant", "remove_dissent"}
                        <= params)


class TestModelOrderCoversRegistry(AdviseFullTestCase):
    """A new registry method must not silently vanish from the menu."""

    def test_model_order_is_exactly_the_registry_methods(self):
        self.assertEqual(set(af.MODEL_ORDER), set(af._METHODS))


if __name__ == "__main__":
    unittest.main(verbosity=2)
