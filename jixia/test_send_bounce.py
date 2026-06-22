"""TDD suite for the send-bounce hook (advisor-routing, Component A).

Oracle: openspec/changes/advisor-routing/test-oracle-brief.md  (COMPONENT A)
Spec:   openspec/changes/advisor-routing/specs/send-bounce.md

Tests import the hook by ABSOLUTE PATH via importlib (the SHARED idiom) — the
hook is symlinked into ~/.claude/hooks/ and must be importable with NO sys.path
manipulation and NO third-party module present. Fixtures are synthetic fake
hook payload dicts; the log + bounce-state files are written to a per-test tmp
dir. Assertions are on OUTCOMES (records that appear, the deny decision, named
entities) — never on internal call structure.

Run: python3 -m pytest jixia/test_send_bounce.py -q
Or:  python3 jixia/test_send_bounce.py   (stdlib unittest fallback, no pytest)
"""

import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


sb = _load("claude/hooks/jixia_send_bounce.py", "jixia_send_bounce")

# Real deployed primary agent the denial must name (file exists in claude/agents/).
PRIMARY_AGENT = "behavioral-psychologist"

# Constants encoded INDEPENDENTLY of the implementation (per the brief §0b).
QUALIFY_MIN_LEN = 280

DRAFT_TOOL_PLUGIN = "mcp__plugin_slack_slack__slack_send_message_draft"
DRAFT_TOOL_CLAUDE = "mcp__claude_ai_Slack__slack_send_message_draft"
SEND_TOOL_PLUGIN = "mcp__plugin_slack_slack__slack_send_message"
SEND_TOOL_CLAUDE = "mcp__claude_ai_Slack__slack_send_message"

# A long, disagreement-shaped staged message — qualifies by BOTH length and marker.
DISAGREE_TEXT = (
    "I respectfully disagree with the proposed reorg. " * 8
)  # >280 chars and carries 'respectfully', 'disagree', 'reorg'

# A short message with a marker but UNDER the length threshold.
SHORT_MARKERED = "Quick heads up: reorg next week."
# A short benign message with NO marker and UNDER the length threshold.
SHORT_BENIGN = "ok thanks, sounds good"


def make_payload(tool_name, channel_id, text, session_id="S1", event="PreToolUse"):
    """A synthetic hook payload dict shaped like a Slack staging call."""
    return {
        "hook_event_name": event,
        "session_id": session_id,
        "tool_name": tool_name,
        "tool_input": {"channel_id": channel_id, "text": text},
    }


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def records_of_kind(records, kind):
    return [r for r in records if r.get("kind") == kind]


class _HookCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(self.tmp.name, "counsel-log.jsonl")
        self.state_path = os.path.join(self.tmp.name, "bounce-state.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def pre(self, payload):
        return sb.handle_pre_tool_use(
            payload, log_path=self.log_path, state_path=self.state_path
        )

    def post(self, payload):
        return sb.handle_post_tool_use(
            payload, log_path=self.log_path, state_path=self.state_path
        )

    def log(self):
        return read_jsonl(self.log_path)

    def state(self):
        return read_jsonl(self.state_path)


class TestSendBounce(_HookCase):

    # --- A-M1: routine-dm-passes (negative control) -----------------------
    def test_AM1_routine_dm_passes(self):
        decision = self.pre(make_payload(DRAFT_TOOL_PLUGIN, "D0123", SHORT_BENIGN))
        self.assertNotEqual(
            decision.get("decision"), "deny",
            "DM staging must never be bounced",
        )
        records = self.log()
        hb = records_of_kind(records, "floor_evaluated")
        self.assertEqual(len(hb), 1, "exactly one floor_evaluated heartbeat for the staging")
        self.assertEqual(hb[0]["prefix_class"], "D")
        self.assertEqual(hb[0]["qualified"], False)
        self.assertEqual(records_of_kind(records, "bounced"), [], "no bounce on a DM")
        self.assertEqual(self.state(), [], "no bounce-state line on a DM")

    # --- A-M2: short-unmarked-U (qualification negative control) -----------
    def test_AM2_short_unmarked_U_passes(self):
        decision = self.pre(make_payload(DRAFT_TOOL_PLUGIN, "U1", SHORT_BENIGN))
        self.assertNotEqual(decision.get("decision"), "deny")
        records = self.log()
        hb = records_of_kind(records, "floor_evaluated")
        self.assertEqual(len(hb), 1)
        self.assertEqual(hb[0]["prefix_class"], "U")
        self.assertEqual(hb[0]["qualified"], False,
                         "a short unmarked U message must NOT qualify")
        self.assertEqual(records_of_kind(records, "bounced"), [],
                         "qualification is not 'any U bounces'")

    # --- A-M3: group-send-bounces (POSITIVE control) -----------------------
    def test_AM3_group_send_bounces(self):
        decision = self.pre(
            make_payload(DRAFT_TOOL_PLUGIN, "U1,U2", DISAGREE_TEXT)
        )
        self.assertEqual(decision.get("decision"), "deny",
                         "first qualifying U-staging must bounce")
        reason = decision.get("reason") or ""
        # deny NAMES the real routed primary advisor (anti-horoscope, substring)
        self.assertIn(PRIMARY_AGENT, reason,
                      "denial must name the real deployed agent %r" % PRIMARY_AGENT)
        # instructs relay-to-human-and-stop; no autonomous retry affordance.
        low = reason.lower()
        self.assertTrue(
            ("relay" in low) or ("surface" in low) or ("tell the" in low)
            or ("await" in low),
            "denial must instruct the model to surface the suggestion to the human",
        )
        self.assertNotIn("retry", low,
                         "denial must NOT offer an autonomous retry path")

        records = self.log()
        bounced = records_of_kind(records, "bounced")
        self.assertEqual(len(bounced), 1, "exactly one bounced record")
        b = bounced[0]
        self.assertEqual(b["text"], DISAGREE_TEXT)
        self.assertEqual(b["hash"], sb.text_hash(DISAGREE_TEXT),
                         "hash must be sha256(text)")
        self.assertEqual(b["session_id"], "S1")
        self.assertEqual(b["channel_id"], "U1,U2")
        # heartbeat for the same staging
        hb = records_of_kind(records, "floor_evaluated")
        self.assertEqual(len(hb), 1)
        self.assertEqual(hb[0]["prefix_class"], "U")
        self.assertEqual(hb[0]["qualified"], True)
        # bounce-state line for (session, channel)
        st = self.state()
        self.assertTrue(
            any(s["session_id"] == "S1" and s["channel_id"] == "U1,U2" for s in st),
            "a bounce-state line must record (S1, U1,U2)",
        )

    # --- SHOULD-2: denial surfaces channel_id verbatim (join-key protection) --
    def test_denial_surfaces_channel_id_verbatim(self):
        """The advised-bounce join is (session_id, channel_id). The SKILL's
        counseled record must carry a channel_id matching the bounced record;
        the model can only do that reliably if the denial it relays SHOWS the
        exact channel_id. A comma-joined group id (U1,U2) is the easy-to-mistype
        case that, if paraphrased, lands the counseled record on the wrong
        channel and poisons the baseline (the brief's worst error class). So the
        deny reason MUST contain the channel verbatim.

        Negative-control intent: a denial that names only the advisor (the prior
        behavior) but omits the channel passes every other deny assertion yet
        fails THIS one — that is exactly the fragile implementation SHOULD-2 names."""
        chan = "U1,U2"
        decision = self.pre(make_payload(DRAFT_TOOL_PLUGIN, chan, DISAGREE_TEXT))
        self.assertEqual(decision.get("decision"), "deny")
        reason = decision.get("reason") or ""
        self.assertIn(
            chan, reason,
            "denial must surface the exact channel_id %r so it can be copied "
            "verbatim into the counseled record's (session,channel) join key — "
            "paraphrasing a comma-joined id poisons the report join" % chan,
        )

    # --- A-M4: second-channel-still-eligible (refutes global-session cap) --
    def test_AM4_second_channel_still_eligible(self):
        d1 = self.pre(make_payload(DRAFT_TOOL_PLUGIN, "U1", DISAGREE_TEXT))
        self.assertEqual(d1.get("decision"), "deny")
        d2 = self.pre(make_payload(DRAFT_TOOL_PLUGIN, "U2", DISAGREE_TEXT))
        self.assertEqual(d2.get("decision"), "deny",
                         "a DIFFERENT channel in the same session gets its own bounce")
        bounced = records_of_kind(self.log(), "bounced")
        self.assertEqual(len(bounced), 2, "one bounce per channel — not a global session cap")
        channels = {b["channel_id"] for b in bounced}
        self.assertEqual(channels, {"U1", "U2"})

    # --- A-M5: retry-proceeds (one-bounce invariant) ----------------------
    def test_AM5_retry_proceeds_no_second_bounce(self):
        d1 = self.pre(make_payload(DRAFT_TOOL_PLUGIN, "U1", DISAGREE_TEXT))
        self.assertEqual(d1.get("decision"), "deny")
        # re-stage (revised text) to the SAME (session, channel)
        revised = DISAGREE_TEXT + " (revised after thought)"
        d2 = self.pre(make_payload(DRAFT_TOOL_PLUGIN, "U1", revised))
        self.assertNotEqual(d2.get("decision"), "deny",
                            "a retry to an already-bounced channel must proceed")
        bounced = records_of_kind(self.log(), "bounced")
        self.assertEqual(len(bounced), 1, "never bounce the same (session,channel) twice")

    # --- A-M6: C-channel-not-bounced (refutes 'bounce-everything-non-D') --
    def test_AM6_C_channel_not_bounced(self):
        decision = self.pre(make_payload(DRAFT_TOOL_PLUGIN, "C9", DISAGREE_TEXT))
        self.assertNotEqual(
            decision.get("decision"), "deny",
            "C-channel/mpdm is deferred scope — must pass with heartbeat only",
        )
        records = self.log()
        hb = records_of_kind(records, "floor_evaluated")
        self.assertEqual(len(hb), 1)
        self.assertEqual(hb[0]["prefix_class"], "C")
        self.assertEqual(hb[0]["qualified"], True,
                         "C text still qualifies on content, but is NOT bounced")
        self.assertEqual(records_of_kind(records, "bounced"), [],
                         "a C-channel qualifying staging must NOT produce a bounced record")
        self.assertEqual(self.state(), [], "no bounce-state line for a C channel")

    # --- A-M7: heartbeat-visibility (writer side) -------------------------
    def test_AM7_heartbeat_for_every_staging(self):
        self.pre(make_payload(SEND_TOOL_PLUGIN, "D1", SHORT_BENIGN))
        self.pre(make_payload(SEND_TOOL_PLUGIN, "U1", SHORT_BENIGN))
        self.pre(make_payload(SEND_TOOL_PLUGIN, "C1", SHORT_BENIGN))
        hb = records_of_kind(self.log(), "floor_evaluated")
        self.assertEqual(len(hb), 3, "one floor_evaluated per staging the hook sees")
        for r in hb:
            self.assertIn("tool", r)
            self.assertIn("prefix_class", r)
            self.assertIn("qualified", r)
            self.assertIn("ts", r)
            self.assertIn("session_id", r)
            self.assertIn("channel_id", r)
        self.assertEqual([r["prefix_class"] for r in hb], ["D", "U", "C"])

    # --- A-M8: restage-recorded (PostToolUse) -----------------------------
    def test_AM8_restage_recorded_post(self):
        # bounce first so (S1, U1) is a bounced channel
        self.pre(make_payload(DRAFT_TOOL_PLUGIN, "U1", DISAGREE_TEXT))
        revised = DISAGREE_TEXT + " (toned down)"
        self.post(make_payload(DRAFT_TOOL_PLUGIN, "U1", revised, event="PostToolUse"))
        restaged = records_of_kind(self.log(), "restaged")
        self.assertEqual(len(restaged), 1, "a subsequent staging to a bounced (S,C) is restaged")
        r = restaged[0]
        self.assertEqual(r["text"], revised)
        self.assertEqual(r["hash"], sb.text_hash(revised), "restaged hash is sha256(new text)")
        self.assertEqual(r["session_id"], "S1")
        self.assertEqual(r["channel_id"], "U1")

    def test_AM8_no_restage_for_unbounced_channel(self):
        # No bounce on this channel → a later staging should NOT be a restaged record
        self.post(make_payload(DRAFT_TOOL_PLUGIN, "U7", DISAGREE_TEXT, event="PostToolUse"))
        self.assertEqual(records_of_kind(self.log(), "restaged"), [],
                         "restaged only for already-bounced (session,channel)")

    # --- A-M9: log-unwritable / fail-open ---------------------------------
    def test_AM9_fail_open_unwritable_log(self):
        bad_dir = os.path.join(self.tmp.name, "does", "not", "exist")
        bad_log = os.path.join(bad_dir, "nope", "counsel-log.jsonl")
        bad_state = os.path.join(bad_dir, "nope", "bounce-state.jsonl")
        # Point at an unwritable/non-creatable path. A qualifying U staging.
        try:
            decision = sb.handle_pre_tool_use(
                make_payload(DRAFT_TOOL_PLUGIN, "U1", DISAGREE_TEXT),
                log_path=bad_log, state_path=bad_state,
            )
        except Exception as e:  # pragma: no cover - this is the failure we forbid
            self.fail("fail-open violated: hook raised %r on unwritable paths" % e)
        self.assertNotEqual(
            decision.get("decision"), "deny",
            "fail-open: an unwritable log/state must ALLOW the staging, never block",
        )

    def test_AM9_fail_open_bad_payload(self):
        try:
            decision = sb.handle_pre_tool_use(
                {"garbage": True}, log_path=self.log_path, state_path=self.state_path
            )
        except Exception as e:  # pragma: no cover
            self.fail("fail-open violated: hook raised %r on a bad payload" % e)
        self.assertNotEqual(decision.get("decision"), "deny",
                            "an unparseable/odd payload must not block the staging")

    # --- A-M10: hash / qualify contract -----------------------------------
    def test_AM10_hash_is_sha256(self):
        self.pre(make_payload(DRAFT_TOOL_PLUGIN, "U1", DISAGREE_TEXT))
        b = records_of_kind(self.log(), "bounced")[0]
        self.assertEqual(b["hash"], sb.text_hash(DISAGREE_TEXT))

    def test_AM10_marker_only_short_qualifies(self):
        self.assertLessEqual(len(SHORT_MARKERED), QUALIFY_MIN_LEN,
                             "fixture must be short to prove the OR branch")
        self.assertTrue(sb.qualifies(SHORT_MARKERED),
                        "a SHORT message bearing a marker must qualify (OR branch)")

    def test_AM10_length_only_unmarked_qualifies(self):
        # Long but contains NO marker substring.
        long_unmarked = "lorem ipsum dolor sit amet " * 12
        self.assertGreater(len(long_unmarked), QUALIFY_MIN_LEN)
        # sanity: ensure no marker accidentally present
        low = long_unmarked.lower()
        self.assertFalse(any(m in low for m in sb.QUALIFY_MARKERS),
                         "fixture must contain no marker to isolate the length branch")
        self.assertTrue(sb.qualifies(long_unmarked),
                        "a long unmarked message must qualify on length alone")

    def test_AM10_short_unmarked_does_not_qualify(self):
        self.assertFalse(sb.qualifies(SHORT_BENIGN),
                         "short + no marker must NOT qualify (negative control)")

    # --- A-M11: tool-matcher drift-tolerance ------------------------------
    def test_AM11_both_prefixes_matched(self):
        for name in (DRAFT_TOOL_PLUGIN, DRAFT_TOOL_CLAUDE,
                     SEND_TOOL_PLUGIN, SEND_TOOL_CLAUDE):
            self.assertTrue(sb.is_tool_matched(name),
                            "matcher must accept %r (drift-tolerance)" % name)

    def test_AM11_suffix_drives_draft_vs_send(self):
        self.assertTrue(sb.is_draft_tool(DRAFT_TOOL_PLUGIN))
        self.assertTrue(sb.is_draft_tool(DRAFT_TOOL_CLAUDE))
        self.assertFalse(sb.is_draft_tool(SEND_TOOL_PLUGIN),
                         "a direct-send tool is not a draft tool")
        self.assertFalse(sb.is_draft_tool(SEND_TOOL_CLAUDE))

    def test_AM11_drift_prefix_bounces_too(self):
        # The claude_ai prefix (this user's live env) must bounce identically.
        decision = self.pre(make_payload(DRAFT_TOOL_CLAUDE, "U1", DISAGREE_TEXT))
        self.assertEqual(decision.get("decision"), "deny",
                         "the claude_ai_Slack draft tool must bounce like the plugin one")

    # --- classify_prefix unit (the pre-exec signal) -----------------------
    def test_classify_prefix(self):
        self.assertEqual(sb.classify_prefix("D0123"), "D")
        self.assertEqual(sb.classify_prefix("U1"), "U")
        self.assertEqual(sb.classify_prefix("U1,U2"), "U")
        self.assertEqual(sb.classify_prefix("C9"), "C")
        self.assertEqual(sb.classify_prefix("X"), "other")


if __name__ == "__main__":
    unittest.main(verbosity=2)
