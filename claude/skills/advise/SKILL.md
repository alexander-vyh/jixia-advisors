---
name: advise
description: >-
  Front door to the jixia advisor pool. Routes a question or a draft (especially
  an outward Slack message with org-dynamics stakes) to a convening model + roster
  via the deterministic classifier, auto-runs the pick on the verbatim draft with a
  non-removable dissent seat named up front, and appends one shared-schema `routed`
  auto-pick record to the counsel log (plus the mechanical `counseled` record). Use
  when the user types `/advise`, when a send-bounce hook has deferred a sensitive
  Slack message and named a lens, or when the user asks for advisor input on a draft
  or decision.
---

# /advise — advisor routing front door (auto-run)

The advisors only reach real work when something routes a question to them at the
moment it matters. This skill is that router. **`/advise` (no flags) ALWAYS acts** —
it never shows a menu and never declines. It runs the classifier's pick: a clear
specialist when one wins the margin gate, otherwise the **`jixia` adaptive-triage
default** (the universal floor). The menu + override lives only in `/advise-full`
(a separate skill); a wrong auto-pick is a cheap, logged `/advise-full` re-run.

## 1. Auto-pick — run the classifier and log the routing decision

Compute the pick with the deterministic classifier and seat the dissenter. This
appends the auto-pick `routed` record to the counsel log immediately (the routing
decision has happened) and returns the model, roster, and dissenter to state on the
first turn. Substitute the verbatim draft and the channel id (or `"adhoc"` for a
plain question with no channel):

```bash
python3 - <<'PY'
import os, sys, json
# Prefer the installed classifier + deps (INSTALL.sh symlinks them here); fall back to
# a repo checkout when developing.
sys.path.insert(0, os.path.expanduser("~/.claude/jixia"))
sys.path.insert(0, os.path.join(os.getcwd(), "jixia"))
# --- fill these in ---
draft = r"""PASTE THE VERBATIM DRAFT TEXT HERE"""
channel_id = "CHANNEL_ID_OF_THE_DRAFT"   # copy VERBATIM from a deny's "channel: …"; else "adhoc"
# ---------------------
session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
try:
    import advise_autopick as ap
except Exception as e:
    # The classifier stack is not importable — degrade to the fixed org-dynamics pair
    # rather than failing. Dispatch behavioral-psychologist + manager-tools-advisor.
    print(json.dumps({"fell_back": True, "model": "jixia", "roster": "practical",
                      "dissenter": "manager-tools-advisor",
                      "dispatch_pair": ["behavioral-psychologist", "manager-tools-advisor"],
                      "reason": "advise_autopick unavailable: %s" % e}))
    sys.exit(0)
plan = ap.plan_run(draft, session_id=session_id, channel_id=channel_id)
ap.append_record(plan["record"])   # the auto-pick record — recommended==selected (an accept)
print(json.dumps({
    "model": plan["model"], "roster": plan["roster"], "confidence": plan["confidence"],
    "dissenter": plan["dissenter"], "mandatory": plan["mandatory"],
    "fell_back": plan["fell_back"], "dispatch_pair": plan["dispatch_pair"],
}))
PY
```

**State the pick on the first turn (one line):** name the selected `model` + `roster`
and **name the dissenter** — e.g. "Running **yushitai** (historical roster). Dissent
seat: **discipline-impeachment-censor** (mandated — argues the counter-case)." Naming
the dissenter up front is required (mandated-dissent `dissenter-named-on-entry`): the
dissent is a structural feature of the deliberation, not noise.

**Explicit override** — if the invocation is `/advise <agent-name>: <question>`, the
named agent is the primary (verify it resolves to a real file in `claude/agents/` or
`~/.claude/agents/`); still seat a dissenter and log the routed record.

## 2. Dispatch on the VERBATIM draft

- **If `fell_back` is false** — run the selected convening `model`. Dispatch its
  advisors as named subagents, one of them holding the **dissent seat** (`dissenter`)
  with the low-sycophancy directive to argue the strongest counter-case.
- **If `fell_back` is true** — the classifier stack was unavailable; dispatch the
  fixed pair in `dispatch_pair` (`behavioral-psychologist` primary +
  `manager-tools-advisor` counter-lens), the advisor-routing skeleton default.

Either way, **every dispatched prompt MUST contain the verbatim draft text** — never a
topic summary or paraphrase (the anti-horoscope guarantee: counsel must be specific to
*this* artifact) — plus the **audience / stakes context**: who receives it, the
channel, the relationship, the outcome the user wants.

## 3. Synthesize

Produce counsel the user can act on, attributing which lens produced which point —
and calling out the **dissenter's** counter-case explicitly — so the user can tell the
advisors apart (the horoscope test: if the user can't tell who said what, synthesis
failed). End with the concrete change to the draft, not abstract advice.

**Do NOT ask the user whether the counsel changed their action.** Measurement is
mechanical and lives downstream in the counsel log + `jixia-counsel-report`.

## 4. Record the consultation (the mechanical `counseled` obligation)

The auto-pick `routed` record was already appended in step 1. Now append **exactly
one** `counseled` record — the consultation record the keep/kill report joins to a
`bounced` record by `(session_id, channel_id)`, so those two fields MUST match what
the hook wrote. `draft_hash` is evidence-of-change only. For an advised bounce, the
deny message the hook surfaced **shows the exact channel id** (`channel: …`) — copy
that string **verbatim** (a mistyped group id like `U1,U2`→`U1` poisons the report's
baseline). If `$CLAUDE_CODE_SESSION_ID` is empty the record cannot join a bounce, so
the snippet refuses to write in that case.

```bash
python3 - <<'PY'
import json, os, hashlib, datetime, pathlib, sys
# --- fill these in ---
draft = r"""PASTE THE VERBATIM DRAFT TEXT HERE"""
channel_id = "CHANNEL_ID_OF_THE_DRAFT"   # copy VERBATIM from the deny's "channel: …"
lenses = ["yushitai", "discipline-impeachment-censor"]   # the real advisors actually dispatched
# ---------------------
session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
if not session_id:
    sys.exit("REFUSED: $CLAUDE_CODE_SESSION_ID is empty — counseled record would "
             "not join any bounce. Confirm the session id is set, then re-run.")
rec = {
    "kind": "counseled",
    "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "session_id": session_id,
    "channel_id": channel_id,
    "lenses": lenses,
    "draft_hash": hashlib.sha256(draft.encode("utf-8")).hexdigest(),
}
p = pathlib.Path(os.path.expanduser("~/.claude/jixia/counsel-log.jsonl"))
p.parent.mkdir(parents=True, exist_ok=True)
with p.open("a", encoding="utf-8") as f:
    f.write(json.dumps(rec) + "\n")
print("counseled record appended:", rec["lenses"], rec["channel_id"])
PY
```

If `/advise` ran on a plain question with no channel, set `channel_id` to a stable
token (e.g. `"adhoc"`) in BOTH snippets; the records are still logged, they simply
won't join to a bounce (there was none).

## Contract reference (counsel log)

`~/.claude/jixia/counsel-log.jsonl`, append-only JSONL. Two record kinds are written
by `/advise`:

### `routed` — the auto-pick routing decision (routing-quality signal)

Shared ONE schema with the `/advise-full` override record (emp.6). The
accept-vs-override rate is computed from `recommended_model` vs `selected_model`. This
record is IGNORED by the keep/kill report (which consumes only bounced/counseled/
restaged) — it is a separate signal.

| field | value |
|---|---|
| `kind` | `"routed"` |
| `ts` | ISO-8601 string |
| `session_id` | `$CLAUDE_CODE_SESSION_ID` (may be empty; not the accept-vs-override key) |
| `channel_id` | the draft's channel, or `"adhoc"` |
| `entry` | `"advise"` (auto-run) or `"advise-full"` (menu; emp.6) |
| `recommended_model` | the model the classifier picked |
| `selected_model` | the model actually run (== recommended on an auto-pick / accept) |
| `roster` | the selected model's registry `default_roster_policy` |
| `dissenter` | who holds the dissent seat |
| `confidence` | integer classifier margin |
| `draft_hash` | `sha256(verbatim draft)` |
| `fell_back` | `true` iff the classifier was absent/errored (degraded to the fixed pair) |

### `counseled` — the consultation record (keep/kill signal)

| field | value |
|---|---|
| `kind` | `"counseled"` |
| `ts` | ISO-8601 string |
| `session_id` | `$CLAUDE_CODE_SESSION_ID` (same value the hook writes) |
| `channel_id` | the draft's channel (join key with the bounce) |
| `lenses` | list of the real advisor names dispatched |
| `draft_hash` | `sha256(draft_text)` — evidence-of-change only, never a join key |
