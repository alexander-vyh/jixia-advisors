"""TDD suite for the registry distinctness validator (advisor-convening-methods-v2, T1b).

Oracle: openspec/changes/advisor-convening-methods-v2/test-oracle-brief.md
Each mutation test tampers an IN-MEMORY deep copy of the real registry, asserts the
validator REJECTS it, and asserts the offending method is NAMED in the error.

Run: python3 -m pytest jixia/ -q
Or:  python3 jixia/test_validate_registry.py   (stdlib unittest fallback, no pytest)
"""

import copy
import json
import os
import unittest

import validate_registry as vr

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(HERE, "registry.json")
REPO_ROOT = os.path.dirname(HERE)


def load_real():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def assert_rejects_naming(testcase, registry, method_name, msg=""):
    """validate() must return at least one error mentioning method_name."""
    errors = vr.validate(registry, repo_root=REPO_ROOT)
    testcase.assertTrue(errors, "expected validation errors but got none: " + msg)
    joined = "\n".join(errors)
    testcase.assertIn(
        method_name, joined,
        "expected error naming %r, got:\n%s" % (method_name, joined),
    )


class TestRealRegistryPasses(unittest.TestCase):
    def test_real_registry_passes(self):
        registry = load_real()
        errors = vr.validate(registry, repo_root=REPO_ROOT)
        self.assertEqual(errors, [], "real registry must pass clean:\n" + "\n".join(errors))


class TestMutations(unittest.TestCase):
    def setUp(self):
        self.registry = load_real()

    def copy(self):
        return copy.deepcopy(self.registry)

    def test_M1_method_count_not_six_missing(self):
        reg = self.copy()
        del reg["methods"]["junto"]
        assert_rejects_naming(self, reg, "junto", "M1 missing")

    def test_M1_method_renamed(self):
        reg = self.copy()
        reg["methods"]["jixia-renamed"] = reg["methods"].pop("jixia")
        assert_rejects_naming(self, reg, "jixia", "M1 renamed")

    def test_M2_unresolved_practical_advisor(self):
        reg = self.copy()
        reg["methods"]["jixia"]["practical_allowlist"] = ["nonexistent-advisor"]
        errors = vr.validate(reg, repo_root=REPO_ROOT)
        joined = "\n".join(errors)
        self.assertIn("jixia", joined)
        self.assertIn("nonexistent-advisor", joined)

    def test_M3_historical_rep_missing_source_metadata(self):
        reg = self.copy()
        rep = reg["methods"]["areopagus"]["historical_roster"][0]
        rep.pop("source_url")
        rep.pop("source_note")
        assert_rejects_naming(self, reg, "areopagus", "M3 missing source")

    def test_M4_rep_cross_method_scope(self):
        reg = self.copy()
        reg["methods"]["yushitai"]["historical_roster"][0]["method"] = "parishad"
        assert_rejects_naming(self, reg, "yushitai", "M4 cross-method")

    def test_M4_load_policy_not_lazy(self):
        reg = self.copy()
        reg["methods"]["seven-sages"]["load_policy"] = "eager"
        assert_rejects_naming(self, reg, "seven-sages", "M4 non-lazy")

    def test_M5_generic_wrapper_all_share_one_contract(self):
        reg = self.copy()
        template = reg["methods"]["jixia"]
        for name in reg["methods"]:
            m = reg["methods"][name]
            m["output_fields"] = list(template["output_fields"])
            m["verb_field"] = template["verb_field"]
            m["entry_gate"] = template["entry_gate"]
            m["refusal"] = template["refusal"]
            m["phases"] = copy.deepcopy(template["phases"])
        errors = vr.validate(reg, repo_root=REPO_ROOT)
        self.assertTrue(errors, "M5 generic wrapper must be rejected")

    def test_M6_historical_default_empty_roster(self):
        reg = self.copy()
        reg["methods"]["parishad"]["historical_roster"] = []
        assert_rejects_naming(self, reg, "parishad", "M6 empty roster")

    def test_M6_historical_default_bodiless_rep(self):
        reg = self.copy()
        reg["methods"]["areopagus"]["historical_roster"][0]["module"] = (
            "jixia/reps/areopagus/does-not-exist.md"
        )
        assert_rejects_naming(self, reg, "areopagus", "M6 bodiless rep")

    def test_M7_copy_paste_drift_identical_triple(self):
        reg = self.copy()
        src = reg["methods"]["seven-sages"]
        dst = reg["methods"]["jixia"]
        dst["output_fields"] = list(src["output_fields"])
        dst["verb_field"] = src["verb_field"]
        dst["entry_gate"] = src["entry_gate"]
        dst["refusal"] = src["refusal"]
        dst["phases"] = copy.deepcopy(src["phases"])
        errors = vr.validate(reg, repo_root=REPO_ROOT)
        self.assertTrue(errors, "M7 identical triple must be rejected")
        joined = "\n".join(errors)
        self.assertIn("jixia", joined)
        self.assertIn("seven-sages", joined)

    def test_M8_missing_verb_field(self):
        reg = self.copy()
        reg["methods"]["junto"]["verb_field"] = "not_an_output_field"
        assert_rejects_naming(self, reg, "junto", "M8 missing verb field")

    def test_M8_verb_field_collision(self):
        reg = self.copy()
        reg["methods"]["yushitai"]["verb_field"] = "verdict"
        reg["methods"]["yushitai"]["output_fields"].append("verdict")
        errors = vr.validate(reg, repo_root=REPO_ROOT)
        self.assertTrue(errors, "M8 verb collision must be rejected")
        joined = "\n".join(errors)
        self.assertTrue(
            "yushitai" in joined or "areopagus" in joined,
            "verb collision must name a colliding method:\n" + joined,
        )

    def test_phase_does_not_cover_output_field(self):
        reg = self.copy()
        reg["methods"]["jixia"]["phases"] = [
            p for p in reg["methods"]["jixia"]["phases"]
            if "next_action" not in p["produces"]
        ]
        assert_rejects_naming(self, reg, "jixia", "uncovered field")


if __name__ == "__main__":
    unittest.main(verbosity=2)
