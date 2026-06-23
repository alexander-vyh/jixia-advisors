"""TDD suite for the mandated-dissent invariant (advisor-convening-router, emp.4).

Oracle: openspec/changes/advisor-convening-router/test-oracle-brief.md
Spec:   openspec/changes/advisor-convening-router/specs/mandated-dissent/spec.md

Authored BEFORE jixia/dissent.py exists — MUST fail red, then pass once emp.4 lands.
Run:
    python3 -m pytest jixia/test_dissent.py -q
    python3 jixia/test_dissent.py

------------------------------------------------------------------------------------
CONTRACT emp.4 MUST satisfy (mandated-dissent spec, encoded independently here)
------------------------------------------------------------------------------------
Module:   jixia/dissent.py
Function: seat_dissenter(model: str, customization: dict | None = None) -> dict

Returns, for EVERY model, ALWAYS exactly one dissenter:
    {
      "model":       <the model id>,
      "occupant":    <a REAL rep id (historical) or claude/agents/ advisor (practical)>,
      "kind":        "native" | "counter-lens" | "custom",
      "prompt":      <str — the low-sycophancy directives>,
      "mandatory":   True,                # the seat can never be removed
      "reinstated":  <bool>,              # True iff a removal/invalid-swap was overridden
    }

Invariants (mandated-dissent spec):
  - dissent-seated-by-default: every model seats exactly one dissenter.
  - dissent-is-non-removable: a removal attempt re-seats the default (reinstated=True).
  - dissent-prompt-is-low-sycophancy: the prompt mandates counter-argument, resisting
    agreement, and not softening in later rounds.
  - dissent-resolves-to-a-real-occupant: historical -> the method's native rep (a real
    jixia/reps/.../*.md); practical -> a real claude/agents/*.md. NEVER a placeholder.
    An invalid swap target re-seats the default rather than seating a fake.
"""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
REGISTRY_PATH = os.path.join(HERE, "registry.json")
AGENTS_DIR = os.path.join(REPO_ROOT, "claude", "agents")

# --- Independent source of truth: registry + agent files on disk, NOT dissent.py ---
with open(REGISTRY_PATH, encoding="utf-8") as _f:
    _METHODS = json.load(_f)["methods"]

MODELS = set(_METHODS)
HISTORICAL = {m for m in _METHODS if _METHODS[m]["default_roster_policy"] == "historical"}
PRACTICAL = MODELS - HISTORICAL

# Real rep ids per method whose module file actually exists on disk.
REAL_REP_IDS = {
    m: {r["id"] for r in _METHODS[m].get("historical_roster", [])
        if os.path.exists(os.path.join(REPO_ROOT, r["module"]))}
    for m in _METHODS
}
# Real practical advisor names = claude/agents/*.md stems.
REAL_AGENTS = {f[:-3] for f in os.listdir(AGENTS_DIR) if f.endswith(".md")}

PLACEHOLDER_TOKENS = {"", "tbd", "n/a", "placeholder", "dissenter", "none", "todo"}

try:
    import dissent as ds  # created by emp.4
except ImportError:  # pragma: no cover - expected until emp.4 lands
    ds = None


def occupant_is_real(model, occupant):
    """A dissent occupant must be a real source-backed rep or a real advisor file."""
    if not occupant or occupant.lower() in PLACEHOLDER_TOKENS:
        return False
    # real rep of ANY method (a swap may pull a rep), or a real practical advisor
    if any(occupant in REAL_REP_IDS[m] for m in REAL_REP_IDS):
        return True
    return occupant in REAL_AGENTS


class DissentTestCase(unittest.TestCase):
    """setUp guard fires outside any subTest -> clean method-level RED when unimplemented."""

    def setUp(self):
        if ds is None:
            self.fail("jixia/dissent.py is not implemented yet (emp.4) — RED as expected")
        self.assertTrue(hasattr(ds, "seat_dissenter"),
                        "dissent must expose seat_dissenter(model, customization=None)")

    def seat(self, model, customization=None):
        return ds.seat_dissenter(model, customization)


class TestSeatedByDefault(DissentTestCase):
    """dissent-seated-by-default: every model seats exactly one dissenter."""

    def test_every_model_seats_exactly_one_real_dissenter(self):
        for model in MODELS:
            with self.subTest(model=model):
                r = self.seat(model)
                self.assertIsInstance(r, dict)
                self.assertTrue(r.get("mandatory") is True, "seat must be marked mandatory")
                self.assertEqual(r.get("model"), model)
                self.assertTrue(
                    occupant_is_real(model, r.get("occupant")),
                    "occupant %r must resolve to a real rep/agent for %s" % (r.get("occupant"), model),
                )


class TestResolvesToRealOccupant(DissentTestCase):
    """dissent-resolves-to-a-real-occupant."""

    def test_pinned_historical_natives(self):
        # The two spec-named native dissenters (the others stay owner-tunable).
        self.assertEqual(self.seat("areopagus")["occupant"], "ephialtean-power-limiter")
        self.assertEqual(self.seat("yushitai")["occupant"], "discipline-impeachment-censor")

    def test_historical_default_is_a_native_rep_of_that_method(self):
        for model in HISTORICAL:
            with self.subTest(model=model):
                r = self.seat(model)
                self.assertEqual(r.get("kind"), "native")
                self.assertIn(
                    r["occupant"], REAL_REP_IDS[model],
                    "%s native dissenter must be one of its own real reps" % model,
                )

    def test_practical_default_is_a_real_counter_lens_agent(self):
        for model in PRACTICAL:
            with self.subTest(model=model):
                r = self.seat(model)
                self.assertEqual(r.get("kind"), "counter-lens")
                self.assertIn(
                    r["occupant"], REAL_AGENTS,
                    "%s counter-lens must be a real claude/agents/ advisor" % model,
                )


class TestNonRemovable(DissentTestCase):
    """dissent-is-non-removable: a removal attempt re-seats the default."""

    def test_removal_attempt_reseats_default(self):
        for model in MODELS:
            with self.subTest(model=model):
                default = self.seat(model)["occupant"]
                r = self.seat(model, {"remove": True})
                self.assertTrue(occupant_is_real(model, r.get("occupant")),
                                "removal must still seat a real dissenter")
                self.assertEqual(r["occupant"], default, "removal must reinstate the default")
                self.assertTrue(r.get("reinstated") is True)
                self.assertTrue(r.get("mandatory") is True)


class TestSwap(DissentTestCase):
    """swap WHO (to a real occupant) is allowed; swap to a fake re-seats the default."""

    def test_swap_to_real_agent_is_honored(self):
        target = "ceo-advisor"
        self.assertIn(target, REAL_AGENTS, "fixture precondition: ceo-advisor must exist")
        r = self.seat("jixia", {"occupant": target})
        self.assertEqual(r["occupant"], target)
        self.assertFalse(r.get("reinstated", False), "a valid swap is not a reinstatement")
        self.assertTrue(r.get("mandatory") is True)

    def test_swap_to_fake_occupant_reseats_default(self):
        default = self.seat("areopagus")["occupant"]
        r = self.seat("areopagus", {"occupant": "council-of-elrond"})
        self.assertNotEqual(r["occupant"], "council-of-elrond", "must never seat a fake occupant")
        self.assertEqual(r["occupant"], default, "invalid swap must reinstate the default")
        self.assertTrue(r.get("reinstated") is True)


class TestLowSycophancyPrompt(DissentTestCase):
    """dissent-prompt-is-low-sycophancy: prompt mandates opposition, no easy agreement,
    no softening across rounds."""

    def test_prompt_contains_the_three_directives(self):
        for model in MODELS:
            with self.subTest(model=model):
                prompt = (self.seat(model).get("prompt") or "").lower()
                self.assertTrue(prompt.strip(), "dissent prompt must be non-empty")
                self.assertIn("counter", prompt, "must direct arguing the counter-case")
                self.assertIn("agree", prompt, "must direct resisting easy agreement")
                self.assertIn("soften", prompt, "must direct not softening in later rounds")


if __name__ == "__main__":
    unittest.main(verbosity=2)
