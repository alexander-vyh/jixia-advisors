# Test Oracle Brief — advisor-routing (send-bounce hook + counsel-report)

**Form:** full 9-section, authored **per component** (the two behavioral Python
artifacts), with the mandatory named-fragile-implementation challenge in both.
There are two distinct behavioral artifacts in this change, and they share a
byte-for-byte cross-component contract (the counsel log), so the brief pins that
contract once (§0) and then constrains each artifact against it. Authored
*before* the hook and report exist so neither can be bent to match its own code.

**Scope of what this brief constrains:** ONLY the two stdlib Python artifacts —
`claude/hooks/jixia_send_bounce.py` (the PreToolUse/PostToolUse hook) and
`bin/jixia-counsel-report` (the tally). The `/advise` skill, the advisor agent
prose, and the synthesized counsel are prose/config judged by use; they get no
unit oracle here (the one mechanical obligation the skill carries — emit exactly
one well-formed `counseled` record — is asserted by the report suite's join
tests and the §0 schema, since that record is the skill's only contract with the
measured pipeline).

**Independent source of truth for both artifacts:** the three specs
(`specs/send-bounce.md`, `specs/counsel-log.md`, `design.md`) plus the SHARED
BUILD CONTRACT. Where those underspecify a load-bearing constant, this brief
PINS it below; the implementations inherit whatever this brief fixes, and the
tests encode it independently so test and dev cannot silently drift.

---

## §0. The cross-component log contract (pinned once; both artifacts obey it)

The counsel log is the only wire between the hook (writer) and the report
(reader). It MUST agree byte-for-byte. Pinned field names (echoing the SHARED
BUILD CONTRACT — any deviation in either artifact is a defect the suites catch):

**Path:** `~/.claude/jixia/counsel-log.jsonl` — user-level, append-only JSONL,
one JSON object per line. Tests override via `--log` (report) and the
`JIXIA_LOG` / explicit-path seam (hook; see §hook-3 constraint).

**Every record** carries: `kind` ∈ {`floor_evaluated`, `bounced`, `counseled`,
`restaged`}, `ts` (ISO-8601 string), `session_id` (string), `channel_id` (string).

| kind | additional REQUIRED fields |
|---|---|
| `floor_evaluated` | `tool` (str), `prefix_class` (`D`\|`U`\|`C`\|`other`), `qualified` (bool) |
| `bounced` | `text` (str, the staged message), `hash` (sha256 hex of `text`) |
| `restaged` | `text` (str), `hash` (sha256 hex of `text`) |
| `counseled` | `lenses` (list[str] of agent names), `draft_hash` (str hash counseled on) |

**`hash` definition (pinned, both artifacts):** `hashlib.sha256(text.encode("utf-8")).hexdigest()`.
This is *evidence-of-change only* — NEVER a join key (see report §R-2).

**`session_id` source equivalence (pinned, both writers).** The report's PRIMARY
join key is `(session_id, channel_id)`. The two writers source `session_id` from
*different* places, and the join is correct **only because these resolve to the
same value**:

- the **hook** writes `session_id` from its PreToolUse/PostToolUse **payload**
  (`payload["session_id"]`), and
- the **`/advise` skill** writes `session_id` from the **environment**
  (`$CLAUDE_CODE_SESSION_ID`).

Claude Code populates both from the one canonical session UUID, so they are equal
at runtime. This equivalence is **load-bearing and must hold**: if the two sources
ever diverge, *every* bounce→counsel join silently returns zero counseled pairs and
the report misfiles real counsel as un-counseled baseline (baseline poisoning — the
worst error class, §R-2). It is pinned here (not left implicit) and enforced by
`jixia/test_join_key_equivalence.py` — a positive test (env value == payload value
⇒ COUNSELED) and a negative control (divergent sources ⇒ join breaks ⇒ BASELINE).
The skill additionally **fails closed** (refuses to write the counseled record) when
`$CLAUDE_CODE_SESSION_ID` is empty, since a record that cannot join is worse than no
record.

---

## §0b. PINNED load-bearing constants (currently underspecified — fixed here)

These are the numbers/lists the specs leave open. The tests encode them
independently of the implementation.

1. **Qualification length threshold:** `QUALIFY_MIN_LEN = 280` characters. A
   staged `text` qualifies on length when `len(text) > 280`. (Justification: a
   tweet-length cap — short DMs/acks and one-line status notes fall below; the
   org-dynamics-sensitive messages the review measured are multi-sentence. The
   exact value is a craft pin, not load-bearing to causation; tests assert the
   boundary, not the wisdom of 280.)

2. **Qualification markers (case-insensitive substring match on `text`):**
   ```
   QUALIFY_MARKERS = [
     # disagreement
     "disagree", "pushback", "push back", "i don't think", "i dont think",
     "concern", "concerned", "object", "blocker", "blocking", "not convinced",
     "respectfully", "to be honest", "frankly",
     # feedback
     "feedback", "critique", "you should", "you need to", "underperform",
     "missed the", "dropped the ball", "performance",
     # announcement
     "announce", "announcing", "heads up", "fyi all", "reorg", "restructur",
     "effective immediately", "going forward", "as of",
   ]
   ```
   A `text` qualifies if `len(text) > QUALIFY_MIN_LEN` **OR** any marker is a
   case-insensitive substring of `text`. (The marker list is a craft pin; tests
   assert that a *short* message containing a marker qualifies and a *short*
   message with none does not — proving the OR branch, not the specific words.)

3. **Per-(session,channel) bounce-state file:**
   `~/.claude/jixia/bounce-state.jsonl` — append-only JSONL, **separate from the
   counsel log** (per SHARED CONTRACT: "separate from the log"). Each line:
   `{"session_id": "...", "channel_id": "...", "ts": "..."}`. A (session,channel)
   is "already bounced" iff a line with that exact pair exists. Fail-open: if the
   file cannot be read, treat as not-yet-bounced and proceed (worst case a second
   bounce — never a block); if it cannot be written after a bounce decision, the
   bounce still fires but the state is best-effort (accepted: re-bounce risk on
   the next call is bounded by fail-open, never a hang).

4. **`auto_retry` mechanical proxy (report):** `AUTO_RETRY_WINDOW_T = 90`
   seconds. A `restaged` record is an `auto_retry` — excluded from BOTH
   comparison groups — iff ALL of:
   (a) it follows its matching `bounced` (same session+channel) with **no
   intervening `counseled` record** for that (session, channel), AND
   (b) `restaged.ts - bounced.ts <= 90 seconds`.
   (Justification for T=90s: the log has no explicit human-turn marker, so we
   proxy "no human intervened" by speed. A human reading a relayed lens
   suggestion, deciding, and re-drafting cannot realistically complete in under
   90s; a model-reflexive retry happens in seconds. T is deliberately generous
   toward *excluding* fast restages — a false-exclusion costs one baseline
   sample, whereas a false-*inclusion* of a model auto-retry as a "human
   dismissal" poisons the baseline, which review SHOULD-2 names as the worse
   error. So we bias the threshold to over-exclude.) A `restaged` that is slower
   than 90s with no counsel is an **un-counseled baseline** restage (a human who
   chose to re-send without advising).

---

# COMPONENT A — send-bounce hook (`claude/hooks/jixia_send_bounce.py`)

## A-1. Business invariant

At most ONE bounce per (session_id, channel_id) per session, fired only on a
qualifying outward (`U…`) staging; the bounce's denial names a real deployed
advisor and instructs the model to relay the suggestion to the human and stop;
every staging the PreToolUse hook sees leaves a `floor_evaluated` heartbeat; and
NO hook error ever blocks a staging beyond that single designed bounce
(fail-open). DMs (`D…`) and channel/mpdm (`C…`) stagings are never bounced in
the skeleton.

## A-2. Independent source of truth

`specs/send-bounce.md` requirements (target-tools, sensitivity-floor-taxonomy,
one-bounce-per-channel-per-session, human-surfacing-denial, recreate-capture,
heartbeat-visibility, fail-open) + the §0 log contract + the §0b pinned
constants. Correctness is defined by the records that appear in the log/state
files and the allow/deny decision returned — observable outputs, not internal
call structure.

## A-3. Solution constraints

- **Self-contained, stdlib-only.** No repo-local imports (the file is symlinked
  into `~/.claude/hooks/`). Only the Python 3.14 stdlib (`json`, `os`, `sys`,
  `hashlib`, `datetime`, `pathlib`). A test that imports it by absolute path via
  `importlib` (the pinned idiom) MUST succeed with NO `sys.path` manipulation and
  NO third-party module present.
- **Symlink-safe:** resolves its state/log paths from `~` / `$HOME` (or an
  explicit override seam for tests), NOT from `__file__`'s directory — because
  `__file__` under the symlink is `~/.claude/hooks/...`, not the repo.
- **Tool-name matching is suffix-based and centralized.** One module-level
  constant lists the matcher tool names; classification checks
  `endswith("slack_send_message_draft")` FIRST, then
  `endswith("slack_send_message")`. (Drift-tolerance per SHARED CONTRACT: both
  the `mcp__plugin_slack_slack__` and `mcp__claude_ai_Slack__` prefixes resolve.)
- **Pure functions + `main()` guard.** Decision logic (classify prefix, qualify
  text, decide-bounce) lives in importable pure functions; `if __name__ ==
  "__main__": main()` does stdin/stdout/exit only. Tests exercise the pure
  functions directly AND drive `main()` over a fixture payload.

## A-4. Invalid solution classes (disallowed even if output looks right)

- **Wrong-layer or post-exec classification:** using `is_dm` / `name` from a
  tool *result* instead of the `channel_id` prefix from `tool_input` (those
  fields do not exist pre-execution — a hook that depends on them is dead code).
- **Hash-keyed or message-keyed cooldown:** keying the one-bounce cap on text
  hash (re-fires on revised drafts) or on session alone (starves the sample).
  MUST key on (session_id, channel_id).
- **Fail-CLOSED on error:** any path that blocks, raises, or hangs on a bad
  payload / unwritable file is forbidden — fail-open is mandatory.
- **Heartbeat omission:** classifying/qualifying without appending
  `floor_evaluated` for that staging.
- **Generic denial:** a deny reason that says "consider a relevant lens" instead
  of naming a real `claude/agents/` file, or that offers a model-satisfiable
  retry path.

## A-5. Named fragile implementation the tests MUST reject

**"Prefix-startswith bounce-everything-non-D":** an implementation that bounces
any `channel_id` not starting with `D` (i.e. lumps `C…` in with `U…`). It passes
routine-dm-passes and group-send-bounces, but it bounces a `C…` channel staging
— which the skeleton scope forbids (C/mpdm is a deferred increment, pass with
heartbeat only). **Catching test:** a `C…`-channel qualifying staging MUST be
allowed with only a `floor_evaluated` record (`prefix_class == "C"`,
`qualified == true`) and NO `bounced` record and NO `bounce-state` line.

Second fragile impl (challenge for the cap): **"global per-session cap"** — caps
at one bounce per session regardless of channel. Caught by
`second-channel-still-eligible`: after a bounce on channel A, a qualifying
staging to channel B in the same session MUST produce its own `bounced` record.

## A-6. Negative control fixtures

- **routine-dm-passes:** payload with `channel_id` `"D0123"`, short benign text
  → allowed, exactly one `floor_evaluated` (`prefix_class=="D"`,
  `qualified==false`), zero `bounced`.
- **short-unmarked-U-passes (qualification negative control):** `channel_id`
  `"U1"`, text length ≤ 280 with NO marker → allowed, `floor_evaluated`
  (`prefix_class=="U"`, `qualified==false`), zero `bounced`. (Proves
  qualification is not "any U bounces".)
- **C-channel-not-bounced:** `channel_id` `"C9"`, long qualifying text → allowed,
  `floor_evaluated` (`prefix_class=="C"`, `qualified==true`), zero `bounced`.
- **log-unwritable (fail-open):** state/log dir pointed at an unwritable path; a
  qualifying `U…` staging → hook exits 0, allows the staging, raises nothing.

## A-7. Positive control

**group-send-bounces:** first qualifying staging this session to a `U1,U2`
multi-user target with disagreement-shaped text ("I respectfully disagree with
the proposed reorg…", >280 chars or marker-bearing) →
- exactly one `bounced` record (text + correct sha256 hash, session+channel
  set), AND
- a `floor_evaluated` heartbeat for the same staging
  (`prefix_class=="U"`, `qualified==true`), AND
- a `bounce-state` line for (session, channel), AND
- the deny decision text NAMES `behavioral-psychologist` (the routed primary for
  the org-dynamics-sensitive outward-message type) — asserted by substring — and
  instructs relay-to-human-and-stop with no autonomous-retry affordance.

Proves the happy path actually fires and the deny is specific (anti-horoscope).

## A-8. Missing / unresolved handling

**Fail-open, always.** Unparseable stdin, missing `channel_id`, unexpected tool
shape, unwritable log or state file → allow the staging, exit 0, write nothing
that would block. A second observable consequence is acceptable (e.g. a missing
heartbeat when the payload was unparseable) but a block/raise/hang is not. The
one-bounce cap fails open: if bounce-state can't be read, proceed as
not-yet-bounced (re-bounce risk bounded; never a block).

## A-9. Final outcome verification

```
python3 -m pytest jixia/test_jixia_send_bounce.py -q
```
plus the cross-component end-to-end assertion: a hook fixture run that writes a
`bounced` record, fed to the report fixture (§B-9), is joined correctly. The
design's done-bar additionally requires one OBSERVED real fire (real qualifying
`U…` staging → real `bounced` line in `~/.claude/jixia/counsel-log.jsonl`) — that
live check is the install/skeleton acceptance, recorded here as the outcome the
unit suite stands in for pre-deploy.

---

# COMPONENT B — counsel report (`bin/jixia-counsel-report`)

## B-1. Business invariant

From the log ALONE, the report joins bounce→counsel→restage by
(session_id, channel_id), classifies each bounce→restage pair as **counseled**,
**un-counseled baseline**, or **auto_retry** (excluded from both), computes
heartbeat totals / bounces fired / per-group restage rate + mean difflib
SequenceMatcher ratio, and prints **DECIDABLE** iff ≥6 bounces exist AND ≥2 pairs
in EACH comparison group — else **NOT YET DECIDABLE** with the counts still
needed. The decision gate is an event count, never a calendar date.

## B-2. Independent source of truth

`specs/counsel-log.md` (log-format, session-channel-correlation,
baseline-integrity, event-count-decision) + §0 contract + §0b auto_retry proxy.
Correctness = the printed tallies and the decision line over synthetic fixtures
whose ground-truth classification is known by construction.

## B-3. Solution constraints

- **Self-contained, stdlib-only**, shebang `#!/usr/bin/env python3`, `chmod +x`,
  no repo-local imports (it too may be symlinked / run from anywhere). Uses only
  `json`, `argparse`/`sys`, `difflib`, `hashlib` if needed, `datetime`.
- **`--log <path>`** with default `~/.claude/jixia/counsel-log.jsonl` so tests
  point it at a fixture JSONL.
- Importable by the pinned `importlib` absolute-path idiom (file has no `.py`
  extension — the spec-from-file-location idiom handles this); computation lives
  in pure functions, `main()` does argparse/print/exit only.
- **difflib ratio** = `difflib.SequenceMatcher(None, bounced_text,
  restaged_text).ratio()` (the pinned distance metric).

## B-4. Invalid solution classes

- **Hash as join key:** joining bounce→restage on `hash` equality. A revised
  draft has a NEW hash; a hash join silently drops exactly the success cases
  (counsel-led rewrites) — the most dangerous downgrade (review NOTE-1). MUST
  join on (session_id, channel_id); hash is evidence-of-change only.
- **Counting auto-retries as baseline dismissals** (review SHOULD-2): a
  no-counsel fast restage counted as a human "sent anyway" poisons the baseline.
- **Calendar-window decision** instead of event-count.
- **Decidable on under-power:** printing a real-looking comparison at <6 bounces
  or <2 per group instead of NOT YET DECIDABLE.
- **Crashing on a malformed/partial log line** instead of skipping it (the
  report must tolerate a truncated final line — JSONL written by an append hook).

## B-5. Named fragile implementation the tests MUST reject

**"Hash-join report":** correlates a `restaged` to its `bounced` by matching
`hash`, and computes counseled-vs-baseline from those matches. **Catching test
(`revised-draft-still-joined`):** a fixture where counsel produced a *rewritten*
draft (restage text ≠ bounce text → different hash) restaged to the same
(session, channel). The hash-join report drops this pair (no hash match) and
reports zero counseled-and-revised events; the correct report MUST count it as
one counseled pair with a difflib ratio < 1.0. This single fixture refutes the
hash-join class.

Second fragile impl: **"≥6-bounces-only decidable"** — gates DECIDABLE on bounce
count alone, ignoring the ≥2-per-group requirement. Caught by a fixture with 6
bounces but 0 counseled pairs → must print NOT YET DECIDABLE naming the missing
group, not DECIDABLE.

## B-6. Negative control fixtures

- **underpowered-report-says-so:** 3 bounces total → prints `NOT YET DECIDABLE`
  AND the remaining counts (e.g. "need 3 more bounces"). Asserted by substring.
- **auto-retry-excluded:** a (session,channel) with `bounced` then `restaged`
  within 90s and NO intervening `counseled` → tallied `auto_retry`, counted in
  NEITHER the counseled rate NOR the baseline rate. Assert the auto_retry count
  is 1 and both group denominators exclude it.
- **six-bounces-no-counsel-group:** 6 bounces, all baseline (≥2), 0 counseled →
  `NOT YET DECIDABLE` (the per-group floor not met), proving bounce-count-alone
  is insufficient.
- **malformed-line-tolerated:** a log whose final line is truncated JSON → report
  runs to completion, skipping the bad line, exits 0.

## B-7. Positive control

**zero-bounce-interpretable + decidable path.** Two assertions:
(a) `zero-bounce-interpretable`: a log of only `floor_evaluated` records (N
heartbeats, 0 bounces) → report prints the heartbeat total N (proving the hook
was live) and `NOT YET DECIDABLE` — distinguishable from "hook never fired".
(b) `decidable`: a fixture with ≥6 bounces, ≥2 counseled pairs (with rewritten
restages, difflib < 1.0) and ≥2 baseline pairs → prints `DECIDABLE`, the
counseled restage rate, the baseline restage rate, and both mean difflib ratios.
Proves valid output is not accidentally dropped and the decision actually flips.

## B-8. Missing / unresolved handling

- **Missing log file** (`--log` points at nonexistent path) → treat as zero
  records: print 0 heartbeats / 0 bounces / NOT YET DECIDABLE, exit 0 (NOT a
  crash — a fresh user has no log yet).
- **Malformed line** → skip it, continue (do not fail the whole report).
- **`restaged`/`counseled` with no matching `bounced`** (orphan) → not counted
  in any pair; does not crash. (Fail-open on join, but NEVER fail-open on the
  decision gate — under-power MUST surface as NOT YET DECIDABLE, never silently
  pass as DECIDABLE.)

## B-9. Final outcome verification

```
python3 -m pytest jixia/test_jixia_counsel_report.py -q
```
and the end-to-end run over a hand-built fixture that crosses BOTH artifacts:
feed the report a fixture log containing a `bounced` record written by Component
A's hook fixture plus a `counseled` and a rewritten `restaged` for the same
(session, channel), and assert the printed report classifies it as one counseled
pair. Whole-suite gate: `python3 -m pytest jixia/ -q` (both new suites + the
existing registry suite) green.

---

# Mutation-test enumeration (one Mn per spec scenario + negative controls)

Each suite is a `unittest.TestCase` set, runnable via pytest AND as a plain
script (`if __name__ == "__main__": unittest.main()`), modeled on
`jixia/test_validate_registry.py`: a positive fixture that PASSES clean, plus
mutations that assert the wrong-behavior is REJECTED and the offending
entity/record is NAMED in the output.

## `jixia/test_jixia_send_bounce.py` (Component A)

| Mn | Spec scenario | Asserts |
|---|---|---|
| **A-M1** | routine-dm-passes (neg control) | `D…` short → allowed, 1 `floor_evaluated` (D/false), 0 `bounced` |
| **A-M2** | short-unmarked-U (qualification neg control) | `U…` ≤280 no marker → allowed, `floor_evaluated` U/false, 0 `bounced` |
| **A-M3** | group-send-bounces (positive control) | `U1,U2` qualifying → 1 `bounced` (correct sha256), heartbeat, state line, deny NAMES `behavioral-psychologist`, no-autonomous-retry |
| **A-M4** | second-channel-still-eligible | bounce on A then qualifying staging to B same session → B gets its own `bounced` (refutes global-session cap) |
| **A-M5** | retry-proceeds | re-staging (same or revised) to an already-bounced (session,channel) → allowed, NO second `bounced` (the one-bounce invariant) |
| **A-M6** | C-channel-not-bounced (fragile-impl refute) | `C…` qualifying → allowed, `floor_evaluated` C/true, 0 `bounced`, 0 state line |
| **A-M7** | heartbeat-visibility / zero-bounce-interpretable (writer side) | every staging seen → exactly one `floor_evaluated` appended with tool/prefix_class/qualified |
| **A-M8** | restage-recorded (PostToolUse) | subsequent staging to a bounced (S,C) → `restaged` record with new text + hash, correct session+channel |
| **A-M9** | log-unwritable / fail-open | unwritable log+state dir, qualifying `U…` → exits 0, allows, raises nothing |
| **A-M10** | hash/qualify contract | `hash` of a `bounced` record == `sha256(text)`; marker-only short text qualifies; length-only unmarked >280 qualifies (the OR branch) |
| **A-M11** | tool-matcher drift-tolerance | both `mcp__plugin_slack_slack__…` and `mcp__claude_ai_Slack__…` draft/send names classify; suffix match drives draft-vs-send |

## `jixia/test_jixia_counsel_report.py` (Component B)

| Mn | Spec scenario | Asserts |
|---|---|---|
| **B-M1** | underpowered-report-says-so (neg control) | 3 bounces → `NOT YET DECIDABLE` + remaining counts |
| **B-M2** | revised-draft-still-joined (fragile-impl refute) | counsel→rewritten restage (new hash) same (S,C) → counted as 1 counseled pair, difflib < 1.0 (refutes hash-join) |
| **B-M3** | auto-retry-excluded | restage <90s, no counsel between → `auto_retry`, in NEITHER group |
| **B-M4** | zero-bounce-interpretable (positive control a) | only `floor_evaluated` records → heartbeat total printed, NOT YET DECIDABLE |
| **B-M5** | decidable path (positive control b) | ≥6 bounces, ≥2 counseled + ≥2 baseline → `DECIDABLE`, both rates + mean difflib ratios printed |
| **B-M6** | six-bounces-no-counsel-group | 6 bounces, 0 counseled pairs → NOT YET DECIDABLE naming missing group (refutes count-only gate) |
| **B-M7** | session-channel join primacy | join is on (session_id, channel_id), NOT hash; same text across two channels stays two pairs |
| **B-M8** | baseline-integrity | a slow (>90s) no-counsel restage counts as baseline; a fast one counts as auto_retry — the T boundary is exercised both sides |
| **B-M9** | malformed-line-tolerated / missing-log | truncated final line skipped, missing `--log` path → 0/0/NOT YET DECIDABLE, exit 0 (never crash) |

---

**Open for owner correction:** the three pinned constants (`QUALIFY_MIN_LEN=280`,
the marker list, `AUTO_RETRY_WINDOW_T=90s`) are craft pins justified above, not
load-bearing to the causal oracle — the tests assert each *boundary*, not the
specific value. If the owner has a measured basis to change any (e.g. real
restage latencies show humans re-draft in <90s), correct it HERE before the hook
and report encode it; both artifacts inherit whatever this brief fixes.
