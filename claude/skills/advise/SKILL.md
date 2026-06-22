---
name: advise
description: >-
  Front door to the jixia advisor pool. Routes a question or a draft (especially
  an outward Slack message with org-dynamics stakes) to one primary advisor plus
  one counter-lens, dispatches BOTH with the verbatim draft + audience context,
  synthesizes their counsel, and appends one mechanical `counseled` record to the
  counsel log. Use when the user types `/advise`, when a send-bounce hook has
  deferred a sensitive Slack message and named a lens, or when the user asks for
  advisor input on a draft or decision.
---

# /advise — advisor routing front door

The advisors only reach real work when something routes a question to them at the
moment it matters. This skill is that router. It is the **everyday Jixia default**:
exactly one primary advisor + one counter-lens, never a convening of the whole pool.

> **Skeleton scope.** This skeleton routes exactly ONE question type confidently
> (an outward message with org-dynamics stakes). The 2–3-type routing table is the
> first post-skeleton increment; the full 16-agent taxonomy and the convening modes
> (Seven Sages / Areopagus / Parishad / Yushitai) are deliberately deferred. Do not
> invent routing for types this skeleton does not cover — say so and offer the list.

## 1. Route

Pick the primary + counter-lens by this rule, in order:

1. **Explicit override** — if the invocation is `/advise <agent-name>: <question>`,
   the named agent is the **primary**. Verify the name resolves to a real file in
   `claude/agents/` (or `~/.claude/agents/`). Then choose a counter-lens that
   genuinely differs in school of thought. Skip step 2.

2. **The one routed type — outward message with org-dynamics stakes.** If the input
   is a draft message to a person/group (a Slack draft, an email, a PR comment, an
   announcement, feedback, a disagreement) where how it lands on people is the
   stake, route the **fixed skeleton pair**:
   - **primary: `behavioral-psychologist`** (how the message will be received,
     cognitive/emotional framing, what behavior it actually triggers)
   - **counter-lens: `manager-tools-advisor`** (results-first, the direct-feedback
     and relationship-bank discipline — a deliberately different tradition)

   This is the SAME primary the send-bounce hook names in its denial, so an advised
   bounce and the hook agree on the lens.

3. **No confident match** — for anything outside that one type, DO NOT guess a lens.
   State plainly that no confident routing exists yet in the skeleton, and offer the
   advisor list so the user can name one (which becomes an explicit override, step 1):

   > "No confident routing for this type yet (skeleton routes only outward
   > org-dynamics messages). Name an advisor and I'll run it with a counter-lens —
   > available: behavioral-psychologist, manager-tools-advisor, ceo-advisor,
   > capital-allocator, value-creation-advisor, value-translator, ui-design-critic,
   > ux-researcher, information-architect, attention-coach, habit-architect,
   > personal-lean-advisor, personal-systems-integrator, delegation-accountability-coach,
   > ops-excellence-advisor, service-design-reviewer, employee-experience-auditor,
   > dashboard-auditor, management-philosophizer, thinking-process-advisor."

## 2. Dispatch BOTH advisors on the VERBATIM artifact

Dispatch the primary and the counter-lens as two named subagents (per the
agent-teams default). Each prompt MUST contain:

- the **verbatim draft text** — never a topic summary or paraphrase (this is the
  anti-horoscope guarantee: counsel must be specific to *this* artifact), and
- the **audience / stakes context**: who receives it, the channel, the relationship,
  what outcome the user wants.

Give each its lens framing ("you are the primary / you are the counter-lens — argue
the case the primary will miss"). They may disagree — that is the point of the pair.

## 3. Synthesize

Produce counsel the user can act on, attributing which lens produced which point so
the user can tell the two apart (the horoscope test: if the user can't tell which
advisor said what, the synthesis failed). End with the concrete change to the draft,
not abstract advice.

**Do NOT ask the user whether the counsel changed their action.** Measurement is
mechanical and lives downstream in the counsel log + `jixia-counsel-report`. A
self-report question is explicitly out of scope (the user rejected it).

## 4. Record the consultation (the one mechanical obligation)

After synthesizing, append **exactly one** `counseled` record to the counsel log.
This is the skill's only contract with the measured pipeline — the report joins it
to a `bounced` record by `(session_id, channel_id)`, so those two fields MUST match
what the hook wrote. `draft_hash` is evidence-of-change only (the report never joins
on it), so use the hash of the draft you actually counseled on.

Run this (substitute the real draft text and the channel_id of the draft — for an
advised bounce, that is the channel the hook deferred):

```bash
python3 - <<'PY'
import json, os, hashlib, datetime, pathlib
# --- fill these in ---
draft = r"""PASTE THE VERBATIM DRAFT TEXT HERE"""
channel_id = "CHANNEL_ID_OF_THE_DRAFT"   # must match the bounced record's channel_id
lenses = ["behavioral-psychologist", "manager-tools-advisor"]
# ---------------------
rec = {
    "kind": "counseled",
    "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "session_id": os.environ.get("CLAUDE_CODE_SESSION_ID", ""),
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

If `/advise` was invoked on a plain question with no channel (not a draft to a
channel), set `channel_id` to a stable token for the artifact (e.g. `"adhoc"`); the
record is still logged, it simply won't join to a bounce (there was none).

## Contract reference (counsel log)

`~/.claude/jixia/counsel-log.jsonl`, append-only JSONL. The `counseled` record:

| field | value |
|---|---|
| `kind` | `"counseled"` |
| `ts` | ISO-8601 string |
| `session_id` | `$CLAUDE_CODE_SESSION_ID` (same value the hook writes) |
| `channel_id` | the draft's channel (join key with the bounce) |
| `lenses` | list of the real agent names used |
| `draft_hash` | `sha256(draft_text)` — evidence-of-change only, never a join key |
