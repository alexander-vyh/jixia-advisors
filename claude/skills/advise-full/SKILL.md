---
name: advise-full
description: >-
  The deliberate-choice front door to the jixia advisor pool. Presents the
  deterministic classifier's pick as a PRE-SELECTED menu default (model-first, roster
  collapsed to the model's registry default, specific-agent selection hidden, dissenter
  named up front, NO round-count/synthesis knob) that the user accepts in one reply or
  overrides — the model, the roster, or specific agents. Runs the resolved pick on the
  verbatim draft with a non-removable dissent seat and appends one shared-schema `routed`
  record that distinguishes an override from an accept (the routing-quality signal). Use
  when the user types `/advise-full`, or wants to see and adjust the routing before it
  runs. For the always-acts, no-menu path, use `/advise` instead.
---

# /advise-full — advisor routing with a pre-selected menu

`/advise` auto-runs the classifier's pick with no menu. `/advise-full` shows that SAME
pick as a **pre-selected default** you can accept in one reply or override. A wrong
auto-pick from `/advise` is corrected by re-running here and overriding — and that
override is what the counsel log measures (the accept-vs-override rate validates the
classifier). The two entry points share ONE `routed` record schema; the only difference
is `entry` (`"advise"` vs `"advise-full"`) and, on an override, `recommended_model` ≠
`selected_model`.

## 1. Build the menu (no record is written yet)

Compute the pre-selected menu. This runs the deterministic classifier and seats the
dissenter, but writes NOTHING to the log — rendering the menu is not yet a routing
decision. Substitute the verbatim draft and the channel id (or `"adhoc"`):

```bash
python3 - <<'PY'
import os, sys, json
# Prefer the installed modules (INSTALL.sh symlinks them here); fall back to a checkout.
sys.path.insert(0, os.path.expanduser("~/.claude/jixia"))
sys.path.insert(0, os.path.join(os.getcwd(), "jixia"))
# --- fill these in ---
draft = r"""PASTE THE VERBATIM DRAFT TEXT HERE"""
channel_id = "CHANNEL_ID_OF_THE_DRAFT"   # copy VERBATIM from a deny's "channel: …"; else "adhoc"
# ---------------------
session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
try:
    import advise_full as af
except Exception as e:
    print(json.dumps({"fell_back": True, "selected_model": "jixia", "roster": "practical",
                      "dissenter": "manager-tools-advisor",
                      "dispatch_pair": ["behavioral-psychologist", "manager-tools-advisor"],
                      "reason": "advise_full unavailable: %s" % e}))
    sys.exit(0)
menu = af.build_menu(draft, session_id=session_id, channel_id=channel_id)
print(json.dumps(menu))
PY
```

## 2. Present the menu — model-first, collapsed, hidden third layer

Render the menu as three layers, but show only the FIRST expanded (never the whole
model×roster×agent grid at once):

- **Model (shown, pre-selected).** List the `models` in the given order — **light → heavy**
  — each with its one-line output-shape `gloss`. Mark the one with `is_default: true` as
  the pre-selected pick (it is the classifier's choice; `confidence` is its margin). State
  it as a one-line confirm, e.g. *"Pre-selected: **yushitai** (audit/accountability →
  findings, evidence path, owner, severity, corrective action). Press Enter to accept, or
  name another model."*
- **Roster (collapsed).** Show only `roster` — the selected model's registry default. Do
  NOT enumerate roster alternatives unless the user asks to change it.
- **Specific agents (hidden).** Do NOT list the advisor pool. Offer it only if the user
  explicitly asks to pick agents — that is the third layer.

**Name the dissenter up front** (mandated-dissent `dissenter-named-on-entry`): state
`dissenter` as a feature of the deliberation — e.g. *"Dissent seat: **discipline-impeachment-censor**
(mandated — argues the counter-case)."*

**Never present a round-count or synthesis-method choice** (`round-count-and-synthesis-not-exposed`):
those are not user knobs. Multi-round interaction is capped internally (2-3 exchanges).

The user resolves in one reply:
- **Accept** (Enter / "go" / "looks good") → run the pre-selected pick.
- **Override the model** ("use areopagus") → `model="areopagus"`.
- **Override the roster** ("run it practical") → `roster="practical"`.
- **Override specific agents** — swap the dissent seat (`dissent_occupant="ceo-advisor"`)
  or (an attempt to) drop it (`remove_dissent=True`). The seat is **non-removable**: a
  removal or an unresolvable swap re-seats a real default.

## 3. Resolve the selection and log the routing decision

Apply the user's reply and append the ONE `routed` record. An accept records
`recommended_model == selected_model`; an override records the difference. Fill the SAME
`draft`/`channel_id` as step 1 and pass ONLY the overrides the user actually gave (omit
them all for an accept):

```bash
python3 - <<'PY'
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/.claude/jixia"))
sys.path.insert(0, os.path.join(os.getcwd(), "jixia"))
import advise_full as af
# --- fill these in ---
draft = r"""PASTE THE VERBATIM DRAFT TEXT HERE"""
channel_id = "CHANNEL_ID_OF_THE_DRAFT"
# Overrides — leave as None for an ACCEPT of the pre-selected pick:
model = None            # e.g. "areopagus" to override the model
roster = None           # e.g. "practical" to override the roster
dissent_occupant = None # e.g. "ceo-advisor" to swap WHO holds the dissent seat
remove_dissent = False  # a removal ATTEMPT — the seat is re-imposed (non-removable)
agents = None           # e.g. ["ceo-advisor", "capital-allocator"] specific advisors
# ---------------------
session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
plan = af.resolve_selection(
    draft, model=model, roster=roster, dissent_occupant=dissent_occupant,
    remove_dissent=remove_dissent, agents=agents,
    session_id=session_id, channel_id=channel_id,
)
af.append_record(plan["record"])   # entry="advise-full"; recommended==selected iff an accept
print(json.dumps({
    "model": plan["model"], "roster": plan["roster"], "dissenter": plan["dissenter"],
    "mandatory": plan["mandatory"], "is_override": plan["is_override"],
    "fell_back": plan["fell_back"], "dissent_degraded": plan["dissent_degraded"],
    "reinstated": plan["reinstated"], "agents": plan["agents"],
    "dispatch_pair": plan["dispatch_pair"],
}))
PY
```

**Confirm what ran (one line):** name the resolved `model` + `roster` and the `dissenter`.
If `reinstated` is true, say the dissent seat was re-imposed (it is mandatory). If
`is_override` is true, you overrode the classifier's pick — that is the logged signal, not
an error.

## 4. Dispatch on the VERBATIM draft

- **If `fell_back` is false** — run the resolved `model`. Dispatch its advisors as named
  subagents, one holding the **dissent seat** (`dissenter`) with the low-sycophancy
  directive to argue the strongest counter-case. If the user chose specific `agents`, seat
  exactly those — but the `dissenter` in the plan is already guaranteed present (the seat
  is non-removable), so include it.
- **If `fell_back` is true** — the classifier stack was unavailable; dispatch the fixed
  pair in `dispatch_pair` (`behavioral-psychologist` + `manager-tools-advisor`).

Either way, **every dispatched prompt MUST contain the verbatim draft text** — never a
summary or paraphrase (the anti-horoscope guarantee) — plus the audience / stakes context:
who receives it, the channel, the relationship, the outcome the user wants.

## 5. Synthesize

Produce counsel the user can act on, attributing which lens produced which point — and
calling out the **dissenter's** counter-case explicitly. End with the concrete change to
the draft, not abstract advice. Do NOT ask the user whether the counsel changed their
action; measurement is mechanical and lives in the counsel log.

## 6. Record the consultation (the mechanical `counseled` obligation)

The `routed` record was appended in step 3. Now append **exactly one** `counseled` record —
identical to `/advise` step 4. The keep/kill report joins it to a `bounced` record by
`(session_id, channel_id)`, so those fields MUST match what the hook wrote; copy the
channel id VERBATIM from the deny's `channel: …`. If `$CLAUDE_CODE_SESSION_ID` is empty the
record cannot join a bounce, so the snippet refuses to write.

```bash
python3 - <<'PY'
import json, os, hashlib, datetime, pathlib, sys
# --- fill these in ---
draft = r"""PASTE THE VERBATIM DRAFT TEXT HERE"""
channel_id = "CHANNEL_ID_OF_THE_DRAFT"
lenses = ["yushitai", "discipline-impeachment-censor"]   # the real advisors actually dispatched
# ---------------------
session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
if not session_id:
    sys.exit("REFUSED: $CLAUDE_CODE_SESSION_ID is empty — counseled record would not join "
             "any bounce. Confirm the session id is set, then re-run.")
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

If `/advise-full` ran on a plain question with no channel, use `"adhoc"` in BOTH snippets;
the records still log, they simply won't join a bounce (there was none).

## Contract reference (counsel log)

`~/.claude/jixia/counsel-log.jsonl`, append-only JSONL. `/advise-full` writes the same two
record kinds `/advise` does — see `claude/skills/advise/SKILL.md` for the full field table.
The one `routed` field-set difference an override exercises:

### `routed` — the routing decision (accept-vs-override signal)

ONE shared schema with the `/advise` auto-pick record. `entry` is `"advise-full"` here.
The accept-vs-override rate is computed from these records:

- **Model override** — `recommended_model` (the classifier's pick) ≠ `selected_model` (what
  the user chose to run). This is the primary signal.
- **Roster override** — `selected_model` unchanged, but `roster` ≠ the selected model's
  registry `default_roster_policy` (derive it from `registry.json`).
- **Agent / dissent override** — `dissenter` ≠ the selected model's default seat.
- **Accept** — `recommended_model == selected_model`, default roster, default seat.

Only a **model**, **roster**, or **dissent-seat** change counts as an override. Selecting
different NON-dissent advisors (the roster's composition) logs as an **accept** in the
`routed` record — that composition is recorded downstream in the `counseled` record's
`lenses`, not here. An analyst reading the accept-vs-override rate should not expect
membership tweaks to show up as overrides.

`af.is_override(record)` decodes all of these (returns `True`/`False`, or `None` to
EXCLUDE a record). **Exclude `fell_back == true` records from the rate:** no classifier ran
on them (`recommended_model` is null), so they are neither an accept nor an override —
counting them either way corrupts the routing-quality rate. `dissent_degraded == true`
means the classifier ran but dissent seating failed; a real counter-lens is still named
(never the model's native seat, and never a decorative/empty seat).

> Known hole (acknowledged, not fixed here): if the whole `advise_full` / `advise_autopick`
> module is unimportable (a broken deploy), the step-1 snippet degrades to the fixed pair
> with NO `routed` record — the same acceptable gap `/advise` documents.
