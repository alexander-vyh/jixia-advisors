"""TDD suite for the surfaces/install validator (advisor-convening-methods-v2, T3).

Oracle: openspec/changes/advisor-convening-methods-v2/specs/method-call-surfaces.md

Strategy: the validator resolves everything against a `repo_root` directory. The
"real" tests run it against the actual repo root (must pass clean). The mutation
tests build an ISOLATED copy of the surface tree in a tmp repo_root, TAMPER one
artifact (delete a wrapper, point at a nonexistent advisor, break a rep source),
and assert the validator REJECTS it and NAMES the offending method/source. This is
genuine tamper-and-reject — the tmp tree is real on disk, not a mock.

Run: python3 -m pytest jixia/ -q
Or:  python3 jixia/test_validate_surfaces.py   (stdlib unittest fallback, no pytest)
"""

import copy
import json
import os
import shutil
import tempfile
import unittest

import validate_surfaces as vs

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(HERE, "registry.json")
REPO_ROOT = os.path.dirname(HERE)

# The subtrees the surfaces validator reads. Copied wholesale into each tmp repo_root
# so mutations operate on a real, isolated filesystem.
_SUBTREES = [
    "claude/commands",
    "claude/agents",
    ".agents/skills",
    "jixia/reps",
    "docs/historical-council-sources",
]


def load_real_registry():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def make_tmp_repo():
    """Materialize an isolated copy of the surface subtrees; return its root path."""
    root = tempfile.mkdtemp(prefix="jixia-surfaces-")
    for sub in _SUBTREES:
        src = os.path.join(REPO_ROOT, sub)
        dst = os.path.join(root, sub)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
    return root


def assert_rejects_naming(testcase, registry, repo_root, needle, msg=""):
    errors = vs.validate(registry, repo_root=repo_root)
    testcase.assertTrue(errors, "expected validation errors but got none: " + msg)
    joined = "\n".join(errors)
    testcase.assertIn(
        needle, joined,
        "expected an error naming %r, got:\n%s" % (needle, joined),
    )


class TestRealSurfacesPass(unittest.TestCase):
    def test_real_surfaces_pass(self):
        registry = load_real_registry()
        errors = vs.validate(registry, repo_root=REPO_ROOT)
        self.assertEqual(
            errors, [], "real surfaces must pass clean:\n" + "\n".join(errors)
        )

    def test_resolves_against_repo_not_install(self):
        # Scenario resolves-against-repo-not-install: with no ~/.claude install, the
        # validator still passes by resolving advisors/reps against repo paths. The
        # tmp repo_root has no ~/.claude symlinks at all, proving install state is
        # not required.
        registry = load_real_registry()
        root = make_tmp_repo()
        try:
            errors = vs.validate(registry, repo_root=root)
            self.assertEqual(
                errors, [],
                "fresh checkout (no install) must validate:\n" + "\n".join(errors),
            )
        finally:
            shutil.rmtree(root, ignore_errors=True)


class TestMutations(unittest.TestCase):
    def setUp(self):
        self.registry = load_real_registry()
        self.root = make_tmp_repo()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _path(self, rel):
        return os.path.join(self.root, rel)

    # --- S1: missing Claude wrapper (missing-wrapper-fails) -----------------
    def test_S1_missing_claude_wrapper_fails_naming_method(self):
        os.remove(self._path("claude/commands/parishad.md"))
        assert_rejects_naming(
            self, self.registry, self.root, "parishad", "S1 missing wrapper"
        )

    # --- S2: missing Codex skill (missing-wrapper-fails, Codex side) --------
    def test_S2_missing_codex_skill_fails_naming_method(self):
        shutil.rmtree(self._path(".agents/skills/yushitai"))
        assert_rejects_naming(
            self, self.registry, self.root, "yushitai", "S2 missing skill"
        )

    # --- S3: wrapper that embeds a hand-maintained roster ------------------
    def test_S3_embedded_roster_fails(self):
        # Tamper the junto wrapper to hardcode a roster of real advisors instead of
        # delegating. claude-wrapper-delegates requires this be rejected.
        advisors = sorted(
            fn[:-3]
            for fn in os.listdir(self._path("claude/agents"))
            if fn.endswith(".md")
        )[:4]
        embedded = "\n".join("- claude/agents/%s.md" % a for a in advisors)
        with open(self._path("claude/commands/junto.md"), "a", encoding="utf-8") as f:
            f.write("\n## Roster (hardcoded)\n" + embedded + "\n")
        assert_rejects_naming(
            self, self.registry, self.root, "junto", "S3 embedded roster"
        )

    # --- S3: wrapper that stops delegating to the registry -----------------
    def test_S3_wrapper_not_delegating_fails(self):
        p = self._path("claude/commands/jixia.md")
        text = open(p, encoding="utf-8").read().replace("registry.json", "REMOVED")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        assert_rejects_naming(
            self, self.registry, self.root, "jixia", "S3 no delegation"
        )

    # --- S4: Codex skill that stops delegating -----------------------------
    def test_S4_skill_not_delegating_fails(self):
        p = self._path(".agents/skills/seven-sages/SKILL.md")
        text = open(p, encoding="utf-8").read().replace("registry.json", "REMOVED")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        assert_rejects_naming(
            self, self.registry, self.root, "seven-sages", "S4 no delegation"
        )

    # --- S5: Codex skill frontmatter name drift ----------------------------
    def test_S5_skill_name_mismatch_fails(self):
        p = self._path(".agents/skills/areopagus/SKILL.md")
        text = open(p, encoding="utf-8").read().replace(
            "name: areopagus", "name: not-areopagus", 1
        )
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        assert_rejects_naming(
            self, self.registry, self.root, "areopagus", "S5 name drift"
        )

    # --- S6: surface references a nonexistent advisor ----------------------
    def test_S6_nonexistent_advisor_reference_fails(self):
        # Inject an explicit claude/agents reference to an advisor not in the repo.
        with open(self._path("claude/commands/jixia.md"), "a", encoding="utf-8") as f:
            f.write("\nSee also claude/agents/totally-made-up-advisor.md\n")
        errors = vs.validate(self.registry, repo_root=self.root)
        joined = "\n".join(errors)
        self.assertIn("jixia", joined)
        self.assertIn("totally-made-up-advisor", joined)

    # --- S6: surface references a nonexistent rep module -------------------
    def test_S6_nonexistent_rep_reference_fails(self):
        with open(
            self._path(".agents/skills/areopagus/SKILL.md"), "a", encoding="utf-8"
        ) as f:
            f.write("\nLoad jixia/reps/areopagus/ghost-rep.md\n")
        errors = vs.validate(self.registry, repo_root=self.root)
        joined = "\n".join(errors)
        self.assertIn("areopagus", joined)
        self.assertIn("ghost-rep.md", joined)

    # --- S7: registry rep source absent from README (drift guard) ----------
    def test_S7_rep_source_missing_from_readme_fails(self):
        # registry-rep-without-readme-source-fails: point a rep at a source url that
        # the README does not contain. Tamper the IN-MEMORY registry (the README on
        # disk is unchanged), proving the drift is detected from the registry side.
        reg = copy.deepcopy(self.registry)
        rep = reg["methods"]["yushitai"]["historical_roster"][0]
        rep["source_url"] = "https://example.invalid/not-in-the-readme"
        errors = vs.validate(reg, repo_root=self.root)
        joined = "\n".join(errors)
        self.assertTrue(errors, "S7 must reject a rep source absent from the README")
        self.assertIn("yushitai", joined)
        self.assertIn("example.invalid", joined)

    # Positive control for S7: the unmodified registry must NOT trip the drift guard
    # (guards against a check that fails everything / passes everything).
    def test_S7_real_registry_has_no_provenance_drift(self):
        errors = vs.validate(self.registry, repo_root=self.root)
        s7 = [e for e in errors if e.startswith("S7")]
        self.assertEqual(s7, [], "real registry must have no S7 drift:\n" + "\n".join(s7))


if __name__ == "__main__":
    unittest.main(verbosity=2)
