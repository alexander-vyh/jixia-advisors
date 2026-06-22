"""TDD suite for jixia-counsel-report (advisor-routing, Component B).

Oracle: openspec/changes/advisor-routing/test-oracle-brief.md (Component B + §0/§0b)
Spec:   openspec/changes/advisor-routing/specs/counsel-log.md

The report is loaded by the pinned importlib ABSOLUTE-PATH idiom (the file has no
.py extension). Each test builds a synthetic JSONL log in a tmp dir whose
ground-truth classification is known by construction, runs the report over it
(both compute_report() and main()->stdout), and asserts OUTCOMES + that the
offending record/group is NAMED in the printed output — never implementation
details.

Run: python3 -m pytest jixia/test_counsel_report.py -q
Or:  python3 jixia/test_counsel_report.py   (stdlib unittest fallback, no pytest)
"""

import datetime
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

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


# --- fixture helpers --------------------------------------------------------

_BASE = datetime.datetime(2026, 6, 21, 12, 0, 0, tzinfo=datetime.timezone.utc)


def _ts(offset_seconds):
    """ISO-8601 timestamp at BASE + offset_seconds."""
    return (_BASE + datetime.timedelta(seconds=offset_seconds)).isoformat()


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _floor(session, channel, off=0, prefix_class="U", qualified=True, tool="t"):
    return {"kind": "floor_evaluated", "ts": _ts(off), "session_id": session,
            "channel_id": channel, "tool": tool, "prefix_class": prefix_class,
            "qualified": qualified}


def _bounced(session, channel, text, off=0):
    return {"kind": "bounced", "ts": _ts(off), "session_id": session,
            "channel_id": channel, "text": text, "hash": _sha(text)}


def _counseled(session, channel, draft_hash, off=0,
               lenses=("behavioral-psychologist", "manager-tools-advisor")):
    return {"kind": "counseled", "ts": _ts(off), "session_id": session,
            "channel_id": channel, "lenses": list(lenses),
            "draft_hash": draft_hash}


def _restaged(session, channel, text, off=0):
    return {"kind": "restaged", "ts": _ts(off), "session_id": session,
            "channel_id": channel, "text": text, "hash": _sha(text)}


def _write_log(records, raw_extra_lines=None):
    """Write records (dicts) as JSONL to a fresh temp file; return its path.

    raw_extra_lines: optional list of raw strings appended verbatim (for
    malformed-line fixtures). Caller owns cleanup via addCleanup.
    """
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        for line in (raw_extra_lines or []):
            f.write(line)
    return path


def _run_main(path):
    """Run main(['--log', path]); return (exit_code, stdout_text)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = rep.main(["--log", path])
    return code, buf.getvalue()


class _CleanupMixin(unittest.TestCase):
    def _log(self, records, raw_extra_lines=None):
        path = _write_log(records, raw_extra_lines)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        return path


# A reusable "decidable" log builder: N counseled pairs (rewritten restage) and
# M baseline pairs (slow no-counsel restage), each on its own channel/session.
def _build_decidable_records(n_counseled=2, n_baseline=2, n_extra_bounce=2):
    recs = []
    total = 0
    # counseled pairs: bounce -> counseled -> rewritten restage (different hash)
    for i in range(n_counseled):
        s, c = "S%d" % total, "C%d" % total
        orig = ("I respectfully disagree with the proposed reorg and have "
                "concerns about how it lands. " * 4)  # >280, marker-bearing
        revised = orig + " (revised after counsel %d)" % i
        recs.append(_bounced(s, c, orig, off=total * 1000))
        recs.append(_counseled(s, c, _sha(orig), off=total * 1000 + 30))
        recs.append(_restaged(s, c, revised, off=total * 1000 + 600))  # slow ok
        total += 1
    # baseline pairs: bounce -> slow no-counsel restage (>90s, no counsel)
    for i in range(n_baseline):
        s, c = "S%d" % total, "C%d" % total
        orig = "Heads up team, going forward we are restructuring. " * 6
        recs.append(_bounced(s, c, orig, off=total * 1000))
        recs.append(_restaged(s, c, orig, off=total * 1000 + 300))  # 300s > 90s
        total += 1
    # extra bounces with no restage (to push bounce count up)
    for i in range(n_extra_bounce):
        s, c = "S%d" % total, "C%d" % total
        recs.append(_bounced(s, c, "blocker: I object. " * 20, off=total * 1000))
        total += 1
    return recs


# ===========================================================================
# B-M1 — underpowered-report-says-so (negative control)
# ===========================================================================
class TestBM1Underpowered(_CleanupMixin):
    def test_three_bounces_not_yet_decidable_with_remaining_counts(self):
        recs = []
        for i in range(3):
            recs.append(_bounced("S%d" % i, "C%d" % i, "I object. " * 30,
                                 off=i * 1000))
        path = self._log(recs)
        code, out = _run_main(path)
        self.assertEqual(code, 0)
        self.assertIn("NOT YET DECIDABLE", out)
        # remaining count must be surfaced: needs 3 more bounces (6 - 3)
        self.assertIn("3", out,
                      "must surface remaining bounce count in:\n" + out)
        self.assertNotIn("DECIDABLE\n", out.replace("NOT YET DECIDABLE", ""))


# ===========================================================================
# B-M2 — revised-draft-still-joined (FRAGILE-IMPL REFUTE: hash-join)
# ===========================================================================
class TestBM2RevisedDraftJoined(_CleanupMixin):
    def test_counsel_rewrite_counts_as_one_counseled_pair_difflib_lt_one(self):
        s, c = "Sx", "Cx"
        orig = "I respectfully disagree with the proposed reorg. " * 8
        revised = orig + " I have reconsidered the framing entirely after advice."
        # different hash by construction (the hash-join trap)
        self.assertNotEqual(_sha(orig), _sha(revised))
        recs = [
            _bounced(s, c, orig, off=0),
            _counseled(s, c, _sha(orig), off=30),
            _restaged(s, c, revised, off=600),  # slow, so not auto_retry
        ]
        path = self._log(recs)
        report = rep.compute_report(rep.read_log(path))
        self.assertEqual(report["counseled_pairs"], 1,
                         "rewritten restage must join on (session,channel), "
                         "NOT hash; report=%r" % report)
        self.assertEqual(report["baseline_pairs"], 0)
        self.assertEqual(report["auto_retry_pairs"], 0)
        # text changed -> difflib ratio strictly below 1.0 (evidence-of-change)
        self.assertLess(report["counseled_mean_ratio"], 1.0,
                        "rewritten draft must yield difflib<1.0: %r" % report)

    def test_difflib_ratio_metric_is_sequencematcher(self):
        a, b = "the quick brown fox", "the quick red fox"
        import difflib
        expected = difflib.SequenceMatcher(None, a, b).ratio()
        self.assertAlmostEqual(rep.difflib_ratio(a, b), expected)
        self.assertLess(rep.difflib_ratio(a, b), 1.0)
        self.assertEqual(rep.difflib_ratio(a, a), 1.0)


# ===========================================================================
# B-M3 — auto-retry-excluded
# ===========================================================================
class TestBM3AutoRetryExcluded(_CleanupMixin):
    def test_fast_no_counsel_restage_is_auto_retry_in_neither_group(self):
        s, c = "Sa", "Ca"
        text = "I object to this. " * 30
        recs = [
            _bounced(s, c, text, off=0),
            _restaged(s, c, text, off=10),  # 10s < 90s, no counsel -> auto_retry
        ]
        path = self._log(recs)
        report = rep.compute_report(rep.read_log(path))
        self.assertEqual(report["auto_retry_pairs"], 1,
                         "fast no-counsel restage must be auto_retry: %r" % report)
        self.assertEqual(report["counseled_pairs"], 0,
                         "auto_retry must NOT be counted as counseled: %r" % report)
        self.assertEqual(report["baseline_pairs"], 0,
                         "auto_retry must NOT poison the baseline: %r" % report)


# ===========================================================================
# B-M4 — zero-bounce-interpretable (positive control a)
# ===========================================================================
class TestBM4ZeroBounceInterpretable(_CleanupMixin):
    def test_only_heartbeats_prints_total_and_not_yet_decidable(self):
        n = 7
        recs = [_floor("S0", "U1", off=i, qualified=(i % 2 == 0))
                for i in range(n)]
        path = self._log(recs)
        report = rep.compute_report(rep.read_log(path))
        self.assertEqual(report["heartbeats"], n)
        self.assertEqual(report["bounces"], 0)
        code, out = _run_main(path)
        self.assertEqual(code, 0)
        # heartbeat total printed (proves hook was live, not "never fired")
        self.assertIn(str(n), out, "heartbeat total %d must appear:\n%s" % (n, out))
        self.assertIn("NOT YET DECIDABLE", out)


# ===========================================================================
# B-M5 — decidable path (positive control b)
# ===========================================================================
class TestBM5DecidablePath(_CleanupMixin):
    def test_six_bounces_two_each_group_prints_decidable_with_rates_and_ratios(self):
        recs = _build_decidable_records(n_counseled=2, n_baseline=2,
                                        n_extra_bounce=2)
        path = self._log(recs)
        report = rep.compute_report(rep.read_log(path))
        self.assertGreaterEqual(report["bounces"], 6, report)
        self.assertGreaterEqual(report["counseled_pairs"], 2, report)
        self.assertGreaterEqual(report["baseline_pairs"], 2, report)
        self.assertTrue(report["decidable"],
                        "gate met (>=6 bounces, >=2/group) must be decidable: %r"
                        % report)
        code, out = _run_main(path)
        self.assertEqual(code, 0)
        self.assertIn("DECIDABLE", out)
        self.assertNotIn("NOT YET DECIDABLE", out)
        # both rates present (non-empty numeric surface) — assert the group
        # labels appear so a reader can read each rate.
        self.assertIn("counseled", out.lower())
        self.assertIn("baseline", out.lower())


# ===========================================================================
# B-M6 — six-bounces-no-counsel-group (FRAGILE-IMPL REFUTE: count-only gate)
# ===========================================================================
class TestBM6SixBouncesNoCounselGroup(_CleanupMixin):
    def test_six_bounces_zero_counseled_pairs_not_yet_decidable_names_group(self):
        # 6 bounces, all baseline-eligible (slow no-counsel restages), 0 counseled
        recs = _build_decidable_records(n_counseled=0, n_baseline=2,
                                        n_extra_bounce=4)
        path = self._log(recs)
        report = rep.compute_report(rep.read_log(path))
        self.assertGreaterEqual(report["bounces"], 6, report)
        self.assertEqual(report["counseled_pairs"], 0, report)
        self.assertFalse(report["decidable"],
                         "count-only gate must NOT fire decidable with 0 "
                         "counseled pairs: %r" % report)
        code, out = _run_main(path)
        self.assertIn("NOT YET DECIDABLE", out)
        # the missing group MUST be named so the reader knows what to collect
        self.assertIn("counseled", out.lower(),
                      "missing 'counseled' group must be named:\n" + out)


# ===========================================================================
# B-M7 — session-channel join primacy
# ===========================================================================
class TestBM7JoinPrimacy(_CleanupMixin):
    def test_same_text_two_channels_stays_two_pairs(self):
        # Identical text (identical hash) bounced+restaged on two distinct
        # channels. A hash-keyed join would collapse/cross-link these; a
        # (session,channel) join keeps them as two independent pairs.
        text = "I respectfully disagree. " * 20
        recs = [
            _bounced("S1", "Cone", text, off=0),
            _restaged("S1", "Cone", text, off=300),       # baseline (slow)
            _bounced("S1", "Ctwo", text, off=1000),
            _counseled("S1", "Ctwo", _sha(text), off=1030),
            _restaged("S1", "Ctwo", text, off=1600),      # counseled
        ]
        path = self._log(recs)
        report = rep.compute_report(rep.read_log(path))
        self.assertEqual(report["counseled_pairs"], 1,
                         "Ctwo (counseled) must be its own pair: %r" % report)
        self.assertEqual(report["baseline_pairs"], 1,
                         "Cone (baseline) must be its own pair: %r" % report)
        self.assertEqual(report["bounces"], 2, report)

    def test_orphan_restage_no_bounce_does_not_crash_or_count(self):
        recs = [
            _restaged("Sorphan", "Corphan", "some text " * 30, off=0),
            _counseled("Sorphan", "Corphan", _sha("x"), off=5),
        ]
        path = self._log(recs)
        code, out = _run_main(path)
        self.assertEqual(code, 0)
        report = rep.compute_report(rep.read_log(path))
        self.assertEqual(report["counseled_pairs"], 0, report)
        self.assertEqual(report["baseline_pairs"], 0, report)
        self.assertEqual(report["bounces"], 0, report)


# ===========================================================================
# B-M8 — baseline-integrity (the T=90s boundary exercised BOTH sides)
# ===========================================================================
class TestBM8BaselineIntegrityBoundary(_CleanupMixin):
    def test_slow_no_counsel_restage_is_baseline(self):
        s, c = "Sb", "Cb"
        text = "Heads up, going forward. " * 30
        recs = [
            _bounced(s, c, text, off=0),
            _restaged(s, c, text, off=120),  # 120s > 90s, no counsel -> baseline
        ]
        path = self._log(recs)
        report = rep.compute_report(rep.read_log(path))
        self.assertEqual(report["baseline_pairs"], 1,
                         "slow no-counsel restage must be baseline: %r" % report)
        self.assertEqual(report["auto_retry_pairs"], 0, report)

    def test_fast_no_counsel_restage_is_auto_retry(self):
        s, c = "Sc", "Cc"
        text = "Heads up, going forward. " * 30
        recs = [
            _bounced(s, c, text, off=0),
            _restaged(s, c, text, off=89),  # 89s <= 90s, no counsel -> auto_retry
        ]
        path = self._log(recs)
        report = rep.compute_report(rep.read_log(path))
        self.assertEqual(report["auto_retry_pairs"], 1,
                         "fast no-counsel restage must be auto_retry: %r" % report)
        self.assertEqual(report["baseline_pairs"], 0,
                         "fast restage must NOT count as baseline: %r" % report)

    def test_fast_restage_WITH_counsel_is_counseled_not_auto_retry(self):
        # auto_retry requires NO intervening counsel; a fast restage that DID
        # follow a counsel pass is counseled, not auto_retry.
        s, c = "Sd", "Cd"
        text = "I respectfully disagree. " * 20
        revised = text + " revised"
        recs = [
            _bounced(s, c, text, off=0),
            _counseled(s, c, _sha(text), off=5),
            _restaged(s, c, revised, off=20),  # fast, but counsel intervened
        ]
        path = self._log(recs)
        report = rep.compute_report(rep.read_log(path))
        self.assertEqual(report["counseled_pairs"], 1,
                         "fast restage after counsel is counseled: %r" % report)
        self.assertEqual(report["auto_retry_pairs"], 0, report)


# ===========================================================================
# B-M9 — malformed-line-tolerated / missing-log
# ===========================================================================
class TestBM9Robustness(_CleanupMixin):
    def test_truncated_final_line_skipped_report_completes(self):
        recs = [_bounced("S%d" % i, "C%d" % i, "I object. " * 30, off=i * 1000)
                for i in range(3)]
        # append a truncated/garbage final JSON line
        path = self._log(recs, raw_extra_lines=['{"kind": "bounced", "ts": '])
        code, out = _run_main(path)
        self.assertEqual(code, 0, "must not crash on truncated line")
        self.assertIn("NOT YET DECIDABLE", out)
        report = rep.compute_report(rep.read_log(path))
        # the 3 valid bounces survive; the bad line is skipped, not counted
        self.assertEqual(report["bounces"], 3,
                         "valid records survive, bad line skipped: %r" % report)

    def test_missing_log_path_zero_everything_exit_zero(self):
        missing = os.path.join(tempfile.gettempdir(),
                               "jixia-no-such-log-%d.jsonl" % os.getpid())
        if os.path.exists(missing):
            os.remove(missing)
        code, out = _run_main(missing)
        self.assertEqual(code, 0, "missing log must not crash:\n" + out)
        self.assertIn("NOT YET DECIDABLE", out)
        report = rep.compute_report(rep.read_log(missing))
        self.assertEqual(report["heartbeats"], 0, report)
        self.assertEqual(report["bounces"], 0, report)


class TestRestageRatePerGroupDenominator(unittest.TestCase):
    """The design's proof-of-delivery compares the counseled vs baseline RESTAGE
    RATE. The rate of a group MUST be (restaged bounces in group) / (bounces in
    group) — NOT (restaged bounces in group) / (TOTAL bounces). A shared
    total-bounces denominator silently degrades the rate comparison into a pair-
    COUNT comparison, which can invert the keep/kill conclusion. These tests pin
    the per-group denominator and the no-inversion property.
    """

    def test_rate_uses_per_group_denominator_including_non_restaged(self):
        # Counseled group: 2 bounces, only 1 restaged -> rate 1/2 = 0.5.
        # Baseline group:  2 bounces, both restaged (slow) -> rate 2/2 = 1.0.
        recs = [
            _bounced("s", "Uc1", "draft c1", off=0),
            _counseled("s", "Uc1", _sha("draft c1"), off=30),
            _restaged("s", "Uc1", "REWORKED c1 entirely", off=60),
            _bounced("s", "Uc2", "draft c2", off=0),
            _counseled("s", "Uc2", _sha("draft c2"), off=30),  # advised, NOT restaged
            _bounced("s", "Ub1", "draft b1", off=0),
            _restaged("s", "Ub1", "resend b1 as is-ish", off=200),  # slow -> baseline
            _bounced("s", "Ub2", "draft b2", off=0),
            _restaged("s", "Ub2", "resend b2 as is-ish", off=300),  # slow -> baseline
        ]
        r = rep.compute_report(recs)
        self.assertAlmostEqual(
            r["counseled_rate"], 0.5, places=6,
            msg="counseled rate must be 1 restaged / 2 counseled bounces = 0.5, "
                "not restaged/total-bounces: %r" % r)
        self.assertAlmostEqual(
            r["baseline_rate"], 1.0, places=6,
            msg="baseline rate must be 2 restaged / 2 baseline bounces = 1.0: %r" % r)

    def test_rate_comparison_not_inverted_by_pair_counts(self):
        # Counseled: 1 bounce, restaged -> rate 1.0.
        # Baseline:  3 bounces, 2 restaged -> rate 0.667.
        # Pair COUNTS say baseline (2) > counseled (1); RATES say counseled wins.
        # A total-bounces denominator would print baseline > counseled (inverted).
        recs = [
            _bounced("s", "Uc1", "draft c1", off=0),
            _counseled("s", "Uc1", _sha("draft c1"), off=30),
            _restaged("s", "Uc1", "REWORKED c1", off=60),
            _bounced("s", "Ub1", "draft b1", off=0),
            _restaged("s", "Ub1", "resend b1", off=200),
            _bounced("s", "Ub2", "draft b2", off=0),
            _restaged("s", "Ub2", "resend b2", off=300),
            _bounced("s", "Ub3", "draft b3", off=0),  # baseline, NOT restaged
        ]
        r = rep.compute_report(recs)
        self.assertAlmostEqual(r["counseled_rate"], 1.0, places=6, msg=repr(r))
        self.assertAlmostEqual(r["baseline_rate"], 2.0 / 3.0, places=6, msg=repr(r))
        self.assertGreater(
            r["counseled_rate"], r["baseline_rate"],
            "rate comparison must reflect per-group propensity, not pair counts "
            "(counts: counseled<baseline; rates: counseled>baseline): %r" % r)

    def test_auto_retry_bounce_excluded_from_rate_denominators(self):
        # An auto_retry (fast, no counsel) bounce is in NEITHER group's denominator.
        recs = [
            _bounced("s", "Uar", "draft ar", off=0),
            _restaged("s", "Uar", "reflex resend ar", off=10),   # <90s, no counsel
            _bounced("s", "Ub1", "draft b1", off=0),
            _restaged("s", "Ub1", "slow resend b1", off=200),     # baseline
        ]
        r = rep.compute_report(recs)
        self.assertEqual(r["auto_retry_pairs"], 1, repr(r))
        self.assertEqual(r["counseled_denom"], 0,
                         "no counseled bounces: %r" % r)
        self.assertEqual(r["baseline_denom"], 1,
                         "the auto_retry bounce must NOT inflate the baseline "
                         "denominator: %r" % r)
        self.assertAlmostEqual(r["baseline_rate"], 1.0, places=6, msg=repr(r))
        self.assertAlmostEqual(r["counseled_rate"], 0.0, places=6, msg=repr(r))


if __name__ == "__main__":
    unittest.main(verbosity=2)
