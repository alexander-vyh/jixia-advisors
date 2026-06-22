"""TDD suite for the convening-router routing classifier (advisor-convening-router, emp.2).

Oracle: openspec/changes/advisor-convening-router/test-oracle-brief.md
Spec:   openspec/changes/advisor-convening-router/specs/convening-routing/spec.md

This suite is authored BEFORE the classifier exists (emp.3). It MUST fail against no
implementation, then pass once emp.3 lands a correct classifier. Run:

    python3 -m pytest jixia/test_routing_classifier.py -q
    python3 jixia/test_routing_classifier.py            # stdlib unittest fallback

------------------------------------------------------------------------------------
CONTRACT emp.3 MUST satisfy (pinned by the brief; encoded here independently)
------------------------------------------------------------------------------------
Module:   jixia/routing_classifier.py
Function: classify(draft: str, signals: dict | None = None) -> dict

Returns, for EVERY input (it ALWAYS acts — no menu, no None, no raise):
    {
      "model":        <one of the six registry ids>,
      "roster":       <that model's registry default_roster_policy>,
      "confidence":   <int margin = top_specialist_score - second_specialist_score, >= 0>,
      "dissent_seat": <str | None>,     # value/seating is mandated-dissent's job, not tested here
    }

Routing rule (brief §0.2/§0.3):
  - A SPECIALIST (seven-sages/areopagus/junto/parishad/yushitai) is returned iff it
    CLEARLY wins: top_specialist_score >= MARKER_MIN AND margin >= MARGIN_MIN.
  - Otherwise the JIXIA adaptive-triage default is returned (no specialist scores, or a
    specialist tie). jixia is the universal default floor; it is never a "guess".
  - Therefore:  model == jixia  <=>  confidence < MARGIN_MIN.

The lexicon WORDS are craft pins (owner-tunable) — this suite asserts the BOUNDARY
behaviour (clean specialist -> that specialist; ambiguous/no-signal -> jixia), never the
specific marker strings, and never recomputes the implementation's scoring (no echo).
"""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(HERE, "registry.json")

# --- Independent source of truth: the registry, NOT the implementation's constants ---
with open(REGISTRY_PATH, encoding="utf-8") as _f:
    _REGISTRY = json.load(_f)["methods"]

REGISTRY_IDS = set(_REGISTRY)                       # the only legal model ids
ROSTER_BY_MODEL = {m: _REGISTRY[m]["default_roster_policy"] for m in _REGISTRY}
SPECIALISTS = REGISTRY_IDS - {"jixia"}
LEGAL_ROSTERS = {"practical", "historical"}

# Pinned by the brief §0.3, re-declared here independently so test and impl cannot drift.
MARKER_MIN = 1
MARGIN_MIN = 1

REQUIRED_KEYS = {"model", "roster", "confidence", "dissent_seat"}

# The classifier under test does not exist yet (emp.3). Import lazily so the suite stays
# COLLECTABLE and each test fails with a clear, named RED rather than an opaque
# collection error.
try:
    import routing_classifier as rc  # noqa: F401  (created by emp.3)
except ImportError:  # pragma: no cover - expected until emp.3 lands
    rc = None


class ClassifierTestCase(unittest.TestCase):
    """Base for every routing test. The setUp guard fires OUTSIDE any subTest, so an
    unimplemented classifier produces a clean method-level FAIL (not a subTest-masked
    'passed') — keeping the TDD red unambiguous for emp.2's acceptance."""

    def setUp(self):
        if rc is None:
            self.fail(
                "jixia/routing_classifier.py is not implemented yet (emp.3) — RED as expected"
            )
        self.assertTrue(
            hasattr(rc, "classify"),
            "routing_classifier must expose classify(draft, signals=None)",
        )


def classify(testcase, draft, signals=None):
    """Call the classifier (rc is guaranteed non-None by ClassifierTestCase.setUp)."""
    return rc.classify(draft, signals)


def assert_well_formed(testcase, result, draft):
    """Every result, for every input, must obey the output contract."""
    testcase.assertIsInstance(result, dict, "classify must return a dict for: %r" % draft)
    testcase.assertEqual(
        REQUIRED_KEYS, set(result),
        "result keys must be exactly %s, got %s for: %r" % (REQUIRED_KEYS, set(result), draft),
    )
    testcase.assertIn(
        result["model"], REGISTRY_IDS,
        "model %r is not a registry id (fabricated/aliased) for: %r" % (result["model"], draft),
    )
    testcase.assertEqual(
        result["roster"], ROSTER_BY_MODEL[result["model"]],
        "roster %r != registry default_roster_policy %r for model %r"
        % (result["roster"], ROSTER_BY_MODEL[result["model"]], result["model"]),
    )
    testcase.assertIn(result["roster"], LEGAL_ROSTERS)
    testcase.assertIsInstance(result["confidence"], int, "confidence must be an int margin")
    testcase.assertGreaterEqual(result["confidence"], 0, "confidence (margin) must be >= 0")


# ----------------------------------------------------------------------------------
# Hand-labeled fixtures. The expected model is derived from the BRIEF's registry-grounded
# intent (each method's entry_gate), written here independently — never copied from the
# implementation's marker lists (that would be the FRAGILE-D echo test).
# ----------------------------------------------------------------------------------

# R-M2..R-M6 — one CLEAN positive per specialist (catches FRAGILE-B: jixia must NOT
# swallow a draft a specialist clearly wins).
SPECIALIST_POSITIVES = [
    ("areopagus",    "Should I ship this release before the deadline? I need a final call / go or no-go."),
    ("yushitai",     "Audit this rollout for failure modes — what broke, what's the root cause, and who owns it?"),
    ("parishad",     "Two teams both claim this is their call — whose authority settles this role conflict?"),
    ("junto",        "Help me build a sustainable weekly-review habit and a better operating cadence."),
    ("seven-sages",  "I'm not sure how to approach this — brainstorm the different angles and options."),
]

# R-M1 / NC-1 — off-distribution: no specialist signal at all. ALWAYS acts -> jixia.
OFF_DISTRIBUTION = [
    "what's the weather tomorrow?",
    "def add(a, b):\n    return a + b",
    "",                     # empty draft must still resolve, not crash
    "   ",                  # whitespace-only
]

# R-M8 / NC-2 — contended specialists (audit AND stakeholder conflict): a tie must fall
# to the jixia default, NOT a coin-flip pick (catches FRAGILE-A).
CONTENDED = (
    "Audit this for failure modes and root cause — but two teams both claim ownership "
    "and it's unclear whose call it is to settle the role conflict."
)

# R-M7 — a genuine everyday-counsel ask with no specialist signal -> the default floor.
EVERYDAY = "Thoughts on how I framed this? Just want a sanity check on my advice."


class TestClassifierInterface(ClassifierTestCase):
    def test_returns_well_formed_dict(self):
        result = classify(self, EVERYDAY)
        assert_well_formed(self, result, EVERYDAY)


class TestPerSpecialistPositives(ClassifierTestCase):
    """R-M2..R-M6 / FRAGILE-B: a clean specialist draft routes to THAT specialist."""

    def test_each_specialist_positive_routes_to_its_model(self):
        for expected, draft in SPECIALIST_POSITIVES:
            with self.subTest(model=expected):
                result = classify(self, draft)
                assert_well_formed(self, result, draft)
                self.assertEqual(
                    result["model"], expected,
                    "draft should route to %r (clean specialist signal), got %r: %r"
                    % (expected, result["model"], draft),
                )
                # A clearly-won specialist must clear the margin gate.
                self.assertGreaterEqual(
                    result["confidence"], MARGIN_MIN,
                    "a clearly-won specialist must have confidence >= MARGIN_MIN",
                )


class TestEverydayDefault(ClassifierTestCase):
    """R-M7: genuine everyday counsel with no specialist signal -> jixia (practical)."""

    def test_everyday_counsel_routes_to_jixia(self):
        result = classify(self, EVERYDAY)
        assert_well_formed(self, result, EVERYDAY)
        self.assertEqual(result["model"], "jixia")
        self.assertEqual(result["roster"], "practical")


class TestOffDistributionStillActsDefault(ClassifierTestCase):
    """R-M1 / NC-1 / FRAGILE-A: no-signal input -> jixia, never a menu/None/raise."""

    def test_off_distribution_routes_to_jixia_and_acts(self):
        for draft in OFF_DISTRIBUTION:
            with self.subTest(draft=draft):
                result = classify(self, draft)
                assert_well_formed(self, result, draft)
                self.assertEqual(
                    result["model"], "jixia",
                    "off-distribution input must fall to the jixia default, got %r: %r"
                    % (result["model"], draft),
                )


class TestContendedFallsToDefault(ClassifierTestCase):
    """R-M8 / NC-2 / FRAGILE-A: a specialist tie falls to jixia, not the arbitrary top."""

    def test_contended_specialists_route_to_jixia(self):
        result = classify(self, CONTENDED)
        assert_well_formed(self, result, CONTENDED)
        self.assertEqual(
            result["model"], "jixia",
            "contended specialists (tie) must fall to the jixia default, got %r"
            % result["model"],
        )
        self.assertNotIn(
            result["model"], SPECIALISTS,
            "a tie must NOT silently pick a specialist (FRAGILE-A)",
        )


class TestMarginBoundary(ClassifierTestCase):
    """R-M9: the margin gate exercised both sides."""

    def test_clear_specialist_side_is_specialist_with_margin(self):
        expected, draft = SPECIALIST_POSITIVES[0]
        result = classify(self, draft)
        self.assertIn(result["model"], SPECIALISTS)
        self.assertGreaterEqual(result["confidence"], MARGIN_MIN)

    def test_tie_side_is_jixia_below_margin(self):
        result = classify(self, CONTENDED)
        self.assertEqual(result["model"], "jixia")
        self.assertLess(result["confidence"], MARGIN_MIN)


class TestNeverInventsAModel(ClassifierTestCase):
    """R-M10 / FRAGILE-C: across ALL inputs, model is a registry id and roster resolves."""

    def test_model_always_registry_id_and_roster_resolves(self):
        drafts = (
            [d for _, d in SPECIALIST_POSITIVES]
            + list(OFF_DISTRIBUTION)
            + [CONTENDED, EVERYDAY]
            + ["asdkjfh qwoeiu zxcv", "!!!", "1234567890", "🙂🙂🙂"]
        )
        for draft in drafts:
            with self.subTest(draft=draft[:40]):
                result = classify(self, draft)
                assert_well_formed(self, result, draft)  # asserts registry id + roster policy


class TestConfidenceContract(ClassifierTestCase):
    """R-M11: confidence is the integer margin, and model==jixia <=> confidence<MARGIN_MIN."""

    def test_confidence_relationship_holds_everywhere(self):
        drafts = (
            [d for _, d in SPECIALIST_POSITIVES]
            + list(OFF_DISTRIBUTION)
            + [CONTENDED, EVERYDAY]
        )
        for draft in drafts:
            with self.subTest(draft=draft[:40]):
                result = classify(self, draft)
                assert_well_formed(self, result, draft)
                is_jixia = result["model"] == "jixia"
                below_margin = result["confidence"] < MARGIN_MIN
                self.assertEqual(
                    is_jixia, below_margin,
                    "contract: model==jixia <=> confidence<MARGIN_MIN; got model=%r conf=%r"
                    % (result["model"], result["confidence"]),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
