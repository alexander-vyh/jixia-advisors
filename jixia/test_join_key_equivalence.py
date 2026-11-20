"""Cross-component contract: the bounce<->counsel JOIN-KEY source equivalence.

SHOULD-1 (config-tail adversarial review, 2026-06-21): the report joins
bounce->counsel->restage on the PRIMARY key (session_id, channel_id). But the
two halves of that key's `session_id` are written by DIFFERENT sources:

  - the HOOK writes session_id from its payload (`payload["session_id"]`,
    claude/hooks/jixia_send_bounce.py),
  - the SKILL writes session_id from the environment: `counsel.py record` reads
    `$CLAUDE_CODE_SESSION_ID` (jixia/counsel.py).

The report join is correct ONLY if those two sources resolve to the same value.
The counsel-report suite's other fixtures feed a literal `session_id="S1"` to BOTH
sides, so they never exercise the env-var path and would stay green even if the two
sources diverged. This module closes that gap: it writes the counseled record with
the real `counsel.py record` and feeds it through the report's classifier, with a
negative control that proves divergence breaks the join (the silent
baseline-poisoning SHOULD-1 names).

These tests assert on `classify_pairs(...)` labels — the layer the report actually
acts on — not on intermediate state.
"""

import datetime
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

# --- pinned importlib absolute-path idiom (SHARED BUILD CONTRACT) ------------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def _load(rel, name):
    path = os.path.join(REPO, rel)
    # Extensionless files (bin/jixia-counsel-report) have no inferable loader,
    # so supply a SourceFileLoader explicitly.
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


rep = _load("bin/jixia-counsel-report", "jixia_counsel_report")

# --- minimal fixture helpers (in-memory; no log file needed) -----------------
_BASE = datetime.datetime(2026, 6, 21, 12, 0, 0, tzinfo=datetime.timezone.utc)


def _ts(off):
    return (_BASE + datetime.timedelta(seconds=off)).isoformat()


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _bounced(session, channel, text, off=0):
    return {"kind": "bounced", "ts": _ts(off), "session_id": session,
            "channel_id": channel, "text": text, "hash": _sha(text)}


def _counseled_via_cli(session_env, channel, draft, off):
    """The counseled record exactly as the skill appends it after a bounce."""
    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, "counsel-log.jsonl")
        env = {**os.environ, "JIXIA_COUNSEL_LOG": log, "CLAUDE_CODE_SESSION_ID": session_env}
        subprocess.run([sys.executable, "-B", os.path.join(HERE, "counsel.py"), "record",
                        "--channel", channel, "--lens", "behavioral-psychologist"],
                       input=draft, text=True, env=env, check=True, capture_output=True)
        with open(log, encoding="utf-8") as f:
            (record,) = [json.loads(line) for line in f]
    record["ts"] = _ts(off)  # place it between the fixture bounce and restage
    return record


def _restaged(session, channel, text, off=0):
    return {"kind": "restaged", "ts": _ts(off), "session_id": session,
            "channel_id": channel, "text": text, "hash": _sha(text)}


class TestJoinKeySourceEquivalence(unittest.TestCase):
    """Pins that the hook's payload-sourced session_id and the SKILL's env-sourced
    session_id MUST resolve to the same value for the report join to hold."""

    _DRAFT = ("I respectfully disagree with the proposed reorg and have real "
              "concerns about how this lands with the team. " * 3)

    def _pair_for(self, recs, session, channel):
        pairs = rep.classify_pairs(recs)
        match = [p for p in pairs
                 if p["session"] == session and p["channel"] == channel]
        self.assertEqual(len(match), 1, repr(pairs))
        return match[0], pairs

    def test_env_session_id_joins_payload_sourced_bounce(self):
        """POSITIVE: when $CLAUDE_CODE_SESSION_ID equals the session_id the hook
        wrote into the bounce, the env-sourced counseled record JOINS and the
        bounce classifies COUNSELED."""
        hook_session = "sess-uuid-abc123"            # what the hook wrote (payload)
        chan = "U1,U2"
        recs = [
            _bounced(hook_session, chan, self._DRAFT, off=0),
            _counseled_via_cli(hook_session, chan, self._DRAFT, off=30),
            _restaged(hook_session, chan, self._DRAFT + " (revised)", off=600),
        ]
        pair, pairs = self._pair_for(recs, hook_session, chan)
        self.assertEqual(
            pair["label"], rep.COUNSELED,
            "an env-sourced counseled record must join a payload-sourced bounce "
            "on (session_id, channel_id): %r" % pairs)

    def test_divergent_session_sources_break_the_join(self):
        """NEGATIVE CONTROL: if the SKILL's env session_id differs from the hook's
        payload session_id, the counseled record does NOT join — the bounce is
        misfiled as an un-counseled BASELINE. This is the silent failure SHOULD-1
        names; it also catches a mutation that joined on channel_id alone (which
        would wrongly label this COUNSELED)."""
        hook_session = "sess-uuid-abc123"
        chan = "U1,U2"
        recs = [
            _bounced(hook_session, chan, self._DRAFT, off=0),
            _counseled_via_cli("sess-uuid-DIFFERENT", chan, self._DRAFT, off=30),
            _restaged(hook_session, chan, self._DRAFT + " x", off=600),
        ]
        pair, pairs = self._pair_for(recs, hook_session, chan)
        self.assertEqual(
            pair["label"], rep.BASELINE,
            "divergent session_id sources MUST break the join — a counsel logged "
            "under a different session must not rescue this bounce: %r" % pairs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
