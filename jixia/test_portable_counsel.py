"""Black-box checks for the read-only skill helper, invoked outside its install dir."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().with_name("counsel.py")
AUDIT = "Audit this rollout for failure modes and root cause."


class PortableCounselTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.work = Path(directory.name)

    def invoke(self, *args, draft=AUDIT):
        return subprocess.run([sys.executable, "-B", str(CLI), *args], input=draft,
                              capture_output=True, text=True, cwd=self.work,
                              env={**os.environ, "HOME": str(self.work)})

    def request(self, *args, **kwargs):
        proc = self.invoke(*args, **kwargs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_menu_preselects_without_leaking_or_writing_the_draft(self):
        draft = AUDIT + '\nPrivate draft: """ $HOME; $(touch injected)\nPY\n'
        menu = self.request("menu", draft=draft)
        self.assertEqual(menu["selected_model"], "yushitai")
        self.assertEqual(menu["roster"], "historical")
        self.assertEqual(menu["dissenter"], "discipline-impeachment-censor")
        self.assertEqual([m["id"] for m in menu["models"] if m["is_default"]], ["yushitai"])
        self.assertNotIn("practical_pool", menu)
        self.assertNotIn("Private draft", json.dumps(menu))
        plan = self.request("run", draft=draft)
        self.assertEqual(plan["model"], menu["selected_model"])
        self.assertEqual(plan["dissenter"], menu["dissenter"])
        self.assertIn(plan["dissenter"], plan["historical_reps"])
        self.assertNotIn("record", plan)
        self.assertNotIn("draft", plan)
        self.assertEqual(list(self.work.iterdir()), [])

    def test_practical_override_reseats_native_dissenter(self):
        plan = self.request("run", "--model", "censorate", "--roster", "practical",
                            "--advisor", "ceo-advisor", "--advisor", "habit-architect")
        self.assertEqual(plan["model"], "yushitai")
        self.assertEqual(plan["roster"], "practical")
        self.assertEqual(plan["advisors"], ["ceo-advisor", "habit-architect"])
        self.assertEqual(plan["historical_reps"], [])
        self.assertEqual(plan["dissenter"], "management-philosophizer")
        self.assertTrue(plan["mandatory"])

    def test_custom_practical_dissenter_on_historical_roster(self):
        plan = self.request("run", "--model", "areopagus", "--dissenter", "ceo-advisor")
        self.assertEqual(plan["roster"], "historical")
        self.assertEqual(plan["dissenter"], "ceo-advisor")
        self.assertIn("ephialtean-power-limiter", plan["historical_reps"])
        self.assertFalse(plan["reinstated"])
        self.assertIn("counter-case", plan["dissent_prompt"])

    def test_ineligible_or_removed_dissent_reinstates_eligible_default(self):
        for roster, change, expected in [
            ("historical", ["--dissenter", "not-a-seat"], "ephialtean-power-limiter"),
            ("historical", ["--dissenter", "investigating-censor"], "ephialtean-power-limiter"),
            ("practical", ["--dissenter", "former-archon-councillor"], "management-philosophizer"),
            ("practical", ["--remove-dissent"], "management-philosophizer"),
        ]:
            with self.subTest(roster=roster, change=change):
                plan = self.request("run", "--model", "areopagus", "--roster", roster, *change)
                self.assertTrue(plan["mandatory"])
                self.assertTrue(plan["reinstated"])
                self.assertEqual(plan["dissenter"], expected)

    def test_layer_expansion_uses_eligible_options_only(self):
        options = self.request("options", "--model", "sages")
        self.assertEqual(options["model"], "seven-sages")
        self.assertEqual(options["roster_options"], ["practical"])
        self.assertEqual(options["historical_reps"], [])
        self.assertIn("manager-tools-advisor", options["practical_pool"])

    def test_unavailable_override_never_silently_runs_a_different_selection(self):
        for args, message in [
            (["--model", "wrong-method"], "Unknown method"),
            (["--model", "jixia", "--roster", "historical"], "does not support"),
            (["--advisor", "../outside-the-bundle"], "Not a bundled practical advisor"),
        ]:
            with self.subTest(args=args):
                proc = self.invoke("run", *args)
                self.assertNotEqual(proc.returncode, 0)
                self.assertEqual(proc.stdout, "")
                self.assertIn(message, proc.stderr)


if __name__ == "__main__":
    unittest.main()
