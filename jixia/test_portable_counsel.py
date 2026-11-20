"""Black-box checks for the skill's planner CLI, invoked outside its install dir."""

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

    def invoke(self, *args, draft=AUDIT, **env):
        # Never inherit a real counsel log or session from the developer's shell.
        inherited = {key: value for key, value in os.environ.items()
                     if key not in ("JIXIA_COUNSEL_LOG", "CLAUDE_CODE_SESSION_ID")}
        return subprocess.run([sys.executable, "-B", str(CLI), *args], input=draft,
                              capture_output=True, text=True, cwd=self.work,
                              env={**inherited, "HOME": str(self.work), **env})

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


    def test_configured_log_records_auto_and_menu_routing_decisions(self):
        log = self.work / "jixia" / "counsel-log.jsonl"
        logged = {"JIXIA_COUNSEL_LOG": str(log), "CLAUDE_CODE_SESSION_ID": "S1"}
        self.request("run", **logged)
        self.request("run", "--model", "areopagus", "--from-menu", "--channel", "U1,U2", **logged)
        self.request("menu", **logged)  # showing the menu is not a routing decision
        auto, chosen = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual((auto["kind"], auto["entry"], auto["session_id"], auto["channel_id"]),
                         ("routed", "advise", "S1", "adhoc"))
        self.assertEqual(auto["recommended_model"], auto["selected_model"])
        self.assertEqual((chosen["entry"], chosen["channel_id"], chosen["selected_model"]),
                         ("advise-full", "U1,U2", "areopagus"))
        self.assertEqual(chosen["recommended_model"], "yushitai")

    def test_record_refuses_without_a_configured_log_or_session(self):
        log = self.work / "counsel-log.jsonl"
        for env, missing in [({}, "JIXIA_COUNSEL_LOG"),
                             ({"JIXIA_COUNSEL_LOG": str(log)}, "CLAUDE_CODE_SESSION_ID")]:
            proc = self.invoke("record", "--channel", "U1", "--lens", "ceo-advisor", **env)
            self.assertEqual(proc.returncode, 2)
            self.assertIn(missing, proc.stderr)
        self.assertFalse(log.exists())

if __name__ == "__main__":
    unittest.main()
