#!/usr/bin/env python3
"""jixia send-bounce hook (PreToolUse + PostToolUse).

Self-contained, stdlib-only. Symlinked into ~/.claude/hooks/, so it MUST NOT
import any repo-local module. Decision logic lives in pure functions; main()
does stdin/stdout/exit only.

Oracle: openspec/changes/advisor-routing/test-oracle-brief.md (Component A)
Spec:   openspec/changes/advisor-routing/specs/send-bounce.md
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Module-level constants the brief pins (encoded independently in the tests).
# ---------------------------------------------------------------------------

# §A-3 / SHARED CONTRACT: suffix-based, centralized matcher list. Both the
# mcp__plugin_slack_slack__ and mcp__claude_ai_Slack__ prefixes resolve.
SLACK_TOOL_MATCHERS = [
    "mcp__plugin_slack_slack__slack_send_message_draft",
    "mcp__claude_ai_Slack__slack_send_message_draft",
    "mcp__plugin_slack_slack__slack_send_message",
    "mcp__claude_ai_Slack__slack_send_message",
]

# Suffixes used for drift-tolerant classification (check draft FIRST).
_DRAFT_SUFFIX = "slack_send_message_draft"
_SEND_SUFFIX = "slack_send_message"

# §0b.1 qualification length threshold.
QUALIFY_MIN_LEN = 280

# §0b.2 qualification markers (case-insensitive substring match on text).
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

# The routed primary advisor for the org-dynamics-sensitive outward-message
# type. A real deployed agent file in claude/agents/.
ROUTED_PRIMARY_AGENT = "behavioral-psychologist"

# Default user-level paths (overridable for tests).
_DEFAULT_LOG = os.path.expanduser("~/.claude/jixia/counsel-log.jsonl")
_DEFAULT_STATE = os.path.expanduser("~/.claude/jixia/bounce-state.jsonl")


def _now_iso():
    """Current time as an ISO-8601 string (UTC)."""
    return datetime.now(timezone.utc).isoformat()


def text_hash(text):
    """sha256 hex of text (pinned in §0). Evidence-of-change only, never a key."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def classify_prefix(channel_id):
    """Return the prefix class for a channel_id: 'D' | 'U' | 'C' | 'other'.

    Pre-execution channel_id prefix is the only signal. Comma-joined U ids are
    multi-user sends and classify as 'U'.
    """
    if not isinstance(channel_id, str) or not channel_id:
        return "other"
    first = channel_id[0]
    if first in ("D", "U", "C"):
        return first
    return "other"


def is_tool_matched(tool_name):
    """True iff tool_name is one of the Slack staging tools (suffix match)."""
    if not isinstance(tool_name, str):
        return False
    return tool_name.endswith(_DRAFT_SUFFIX) or tool_name.endswith(_SEND_SUFFIX)


def is_draft_tool(tool_name):
    """True iff tool_name is the draft-staging tool (suffix 'slack_send_message_draft')."""
    return isinstance(tool_name, str) and tool_name.endswith(_DRAFT_SUFFIX)


def qualifies(text):
    """True iff text qualifies for bounce consideration: len > QUALIFY_MIN_LEN
    OR any QUALIFY_MARKERS substring (case-insensitive)."""
    if not isinstance(text, str):
        return False
    if len(text) > QUALIFY_MIN_LEN:
        return True
    low = text.lower()
    return any(m in low for m in QUALIFY_MARKERS)


def already_bounced(session_id, channel_id, state_path):
    """True iff a (session_id, channel_id) line exists in the bounce-state file.
    Fail-open: unreadable file => treat as not-yet-bounced (return False)."""
    try:
        if not os.path.exists(state_path):
            return False
        with open(state_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if (rec.get("session_id") == session_id
                        and rec.get("channel_id") == channel_id):
                    return True
    except Exception:
        return False
    return False


def decide_bounce(tool_name, tool_input, session_id, state_path):
    """Pure decision: should this PreToolUse staging be bounced?

    Returns a dict describing the decision and the heartbeat to record. Never
    raises on bad input — fail-open (returns bounce=False).
    """
    result = {
        "bounce": False,
        "prefix_class": "other",
        "qualified": False,
        "channel_id": "",
        "text": "",
        "tool": tool_name if isinstance(tool_name, str) else "",
    }
    try:
        if not isinstance(tool_input, dict):
            return result
        channel_id = tool_input.get("channel_id", "")
        text = tool_input.get("text", "")
        if not isinstance(channel_id, str):
            channel_id = ""
        if not isinstance(text, str):
            text = ""
        result["channel_id"] = channel_id
        result["text"] = text
        prefix = classify_prefix(channel_id)
        result["prefix_class"] = prefix
        qual = qualifies(text)
        result["qualified"] = qual
        # Only outward U-sends are bounce-eligible. D never; C deferred.
        if prefix == "U" and qual and not already_bounced(
                session_id, channel_id, state_path):
            result["bounce"] = True
    except Exception:
        # Fail-open: any unexpected shape => do not bounce.
        return {
            "bounce": False,
            "prefix_class": result.get("prefix_class", "other"),
            "qualified": result.get("qualified", False),
            "channel_id": result.get("channel_id", ""),
            "text": result.get("text", ""),
            "tool": result.get("tool", ""),
        }
    return result


def denial_text(channel_id):
    """The deny reason. Names ROUTED_PRIMARY_AGENT and instructs relay-to-
    human-and-stop with NO autonomous-retry affordance.

    Surfaces the exact channel_id verbatim: the counseled record the SKILL later
    appends joins to this bounce on (session_id, channel_id). If the channel is
    not shown here, the model must reconstruct it from memory of a deferred tool
    call — and a paraphrased / mistyped channel (e.g. the comma-joined "U1,U2")
    lands the counseled record on the wrong channel, so the report files the
    eventual re-send as an un-counseled baseline. That baseline-poisoning is the
    worst error class in the Test Oracle Brief, so the join key is shown, not
    remembered."""
    return (
        "Jixia send-bounce: this outward message to a multi-user audience has "
        "org-dynamics stakes. Before it goes out, the %s advisor should weigh in "
        "(it is the routed primary lens for messages with interpersonal/"
        "organizational consequences). Surface this suggestion to the human "
        "VERBATIM: relay that the %s advisor is recommended for this draft "
        "(channel: %s), then STOP and await their direction (advise via /advise, "
        "or send as-is). Do NOT re-send, re-stage, or otherwise act on your own — "
        "the human must see this suggestion and decide. If they choose /advise, "
        "use this exact channel id verbatim — %s — never paraphrase or "
        "reconstruct it." % (
            ROUTED_PRIMARY_AGENT, ROUTED_PRIMARY_AGENT, channel_id, channel_id)
    )


def _ensure_log_dir(path):
    """Create the user-level jixia dir (one level) if absent. Does NOT create
    arbitrarily-deep nonexistent trees: a path whose parent dir does not already
    exist is treated as unwritable (the fail-open negative-control case). Returns
    True if the directory exists/was created, False otherwise."""
    d = os.path.dirname(path)
    if not d:
        return True
    if os.path.isdir(d):
        return True
    parent = os.path.dirname(d)
    # Only create the final jixia/ dir when its parent already exists.
    if parent and os.path.isdir(parent):
        try:
            os.makedirs(d, exist_ok=True)
            return True
        except Exception:
            return False
    return False


def append_record(record, log_path):
    """Append one JSON object as a line to the counsel log. Fail-open: on any
    write error, swallow and return (never raise)."""
    try:
        if not _ensure_log_dir(log_path):
            return
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        return


def append_bounce_state(session_id, channel_id, ts, state_path):
    """Append a (session,channel,ts) line to the bounce-state file. Fail-open:
    returns True on a successful write, False on any error (never raises). The
    caller uses this to gate the deny — a bounce we cannot persist must NOT be
    enforced (the one-bounce cap would be unbounded), so a failed write fails
    open to ALLOW."""
    try:
        if not _ensure_log_dir(state_path):
            return False
        with open(state_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "session_id": session_id,
                "channel_id": channel_id,
                "ts": ts,
            }) + "\n")
        return True
    except Exception:
        return False


def handle_pre_tool_use(payload, log_path=_DEFAULT_LOG, state_path=_DEFAULT_STATE,
                        now=None):
    """PreToolUse entry. Appends a floor_evaluated heartbeat for every staging
    seen; on a qualifying first U-staging appends a bounced record + bounce-state
    line and returns a deny decision. Returns {"decision": "allow"|"deny",
    "reason": str|None}. Fail-open: any error => allow, raise nothing."""
    try:
        if not isinstance(payload, dict):
            return {"decision": "allow", "reason": None}
        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})
        session_id = payload.get("session_id", "")
        if not is_tool_matched(tool_name):
            return {"decision": "allow", "reason": None}
        ts = now or _now_iso()

        decision = decide_bounce(tool_name, tool_input, session_id, state_path)
        channel_id = decision["channel_id"]

        # Heartbeat for EVERY staging the hook sees.
        append_record({
            "kind": "floor_evaluated",
            "ts": ts,
            "session_id": session_id,
            "channel_id": channel_id,
            "tool": tool_name,
            "prefix_class": decision["prefix_class"],
            "qualified": decision["qualified"],
        }, log_path)

        if decision["bounce"]:
            text = decision["text"]
            append_record({
                "kind": "bounced",
                "ts": ts,
                "session_id": session_id,
                "channel_id": channel_id,
                "text": text,
                "hash": text_hash(text),
            }, log_path)
            persisted = append_bounce_state(session_id, channel_id, ts, state_path)
            if not persisted:
                # Fail-open: a bounce we cannot persist would make the one-bounce
                # cap unbounded (re-bounce on every retry), so ALLOW instead of
                # enforcing a deny we cannot cap.
                return {"decision": "allow", "reason": None}
            return {"decision": "deny", "reason": denial_text(channel_id)}

        return {"decision": "allow", "reason": None}
    except Exception:
        # Fail-open: never block beyond the single designed bounce.
        return {"decision": "allow", "reason": None}


def handle_post_tool_use(payload, log_path=_DEFAULT_LOG, state_path=_DEFAULT_STATE,
                         now=None):
    """PostToolUse entry: if this staging targets an already-bounced
    (session,channel), append a restaged record (text + hash). Fail-open."""
    try:
        if not isinstance(payload, dict):
            return {"decision": "allow", "reason": None}
        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})
        session_id = payload.get("session_id", "")
        if not is_tool_matched(tool_name):
            return {"decision": "allow", "reason": None}
        if not isinstance(tool_input, dict):
            return {"decision": "allow", "reason": None}
        channel_id = tool_input.get("channel_id", "")
        text = tool_input.get("text", "")
        if not isinstance(channel_id, str):
            channel_id = ""
        if not isinstance(text, str):
            text = ""
        if already_bounced(session_id, channel_id, state_path):
            ts = now or _now_iso()
            append_record({
                "kind": "restaged",
                "ts": ts,
                "session_id": session_id,
                "channel_id": channel_id,
                "text": text,
                "hash": text_hash(text),
            }, log_path)
        return {"decision": "allow", "reason": None}
    except Exception:
        return {"decision": "allow", "reason": None}


def main():
    """stdin/stdout/exit only — reads the hook payload, dispatches to the
    Pre/Post handler by hook event, prints any decision, exits 0."""
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        # Fail-open: unparseable stdin => allow, exit clean.
        sys.exit(0)

    try:
        event = payload.get("hook_event_name", "") if isinstance(payload, dict) else ""
        if event == "PostToolUse":
            handle_post_tool_use(payload)
            sys.exit(0)
        decision = handle_pre_tool_use(payload)
        if isinstance(decision, dict) and decision.get("decision") == "deny":
            out = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": decision.get("reason") or "",
                },
            }
            print(json.dumps(out))
        sys.exit(0)
    except Exception:
        # Fail-open under all circumstances.
        sys.exit(0)


if __name__ == "__main__":
    main()
