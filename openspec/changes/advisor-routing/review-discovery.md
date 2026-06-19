# Adversarial Review — advisor-routing (discovery / pre-skeleton)

Reviewer: independent adversarial pass, 2026-06-11. Reviewed the artifact
(problem-framing.md, design.md, tasks.md, specs/*), the 16 agent files,
INSTALL.sh, docs/advisory-model.md, AND the **actual recorded Slack MCP tool
calls** in `~/.claude/projects/-Users-…-crowdstrike-py/*.jsonl` — because the
entire design rests on the shape of a tool nobody in these artifacts ever
opened.

Every load-bearing empirical claim below is measured from 17 real
`slack_send_*` tool calls across 20 session files in the only project where
this user actually uses the Slack MCP. I did not take the design's word for the
tool shape. Neither should you.

## Findings

### BLOCK-1 — The bounce target does not send. It stages a human-edited draft. The entire mechanical oracle is built on a tool whose semantics it never checked. (blocking-for-skeleton)

The design says "PreToolUse on the Slack **send** tools … intercepting before
the action completes … diff of text-at-bounce vs text-at-send." It names the
target abstractly ("Slack send tools") and never inspects the real one.

The real one, used in **15 of 17** recorded calls, is
`mcp__plugin_slack_slack__slack_send_message_draft`. Its result string is:

> `"result":"Draft message is created. They can edit it before sending."`

This tool **does not send a message.** It creates a Slack draft that the human
then opens, edits, and sends *by hand in the Slack UI* — entirely outside Claude
Code, where no PostToolUse hook can ever see it. So:

- **The PostToolUse "final-text capture" (spec send-bounce §final-text-capture,
  the `sent` record) cannot fire for the dominant tool.** The model's tool call
  ends at "draft created." The actual send — and any edits the human makes — happen
  in Slack and are invisible to the hook. The bounce→send diff, which IS the
  riskiest-assumption oracle, has **no `sent` side for 88% of traffic.**
- Worse: with this tool the human *already* gets a review-and-edit step for
  free, on every message, before sending. The bounce inserts an advisory pause in
  front of a tool that is itself already a "pause and let the human edit"
  affordance. The premise "messages ship unchanged because there's no pause" is
  partly false for the actual workflow.
- The genuinely-sends tool, `slack_send_message`, appears **2 of 17** times.
  The oracle only works on that 12% slice — far too thin to reach the ≥2–3
  counseled-and-revised threshold in two weeks (see BLOCK-2).

**Minimal fix:** before any skeleton task, the design must decide what it is
actually intercepting. Either (a) target `slack_send_message_draft` and redefine
the oracle as *bounce → diff of draft-text-at-bounce vs draft-text-at-recreate*
(the model often recreates the draft after counsel — 3 consecutive `..._draft`
calls to the same channel appear in the data, so a re-draft IS observable),
explicitly abandoning the "captures the human's final hand-edit" claim; or (b)
restrict to `slack_send_message` and accept the base rate is far below what the
2-week proof needs. Option (a) is the only one with enough events, and it changes
the oracle's meaning — that is a design change, not an implementation detail.
**The current spec is unbuildable as written because its PostToolUse `sent`
record will essentially never appear for the tool that carries the traffic.**

### BLOCK-2 — Sample size is below the proof threshold, and the once-per-session cap actively starves it. (blocking-for-skeleton)

Proof of delivery: "≥2–3 counseled-and-revised sends with revision rate/distance
above the un-counseled baseline within ~2 weeks." For that you need, in two
weeks: enough bounces, split across *two* groups (counseled vs un-counseled),
with enough revision events in EACH to compare. Measured base rate:

- Across **20 session files** in this user's most Slack-active project, only
  **3 sessions** contained any floor-qualifying channel send. (Floor =
  channel-wide `C…` AND length>200 or marker word.)
- One-bounce-per-session means each of those 3 sessions yields **exactly one
  bounce** — even though they contained 3, 6, and 2 qualifying sends
  respectively. The cap throws away 8 of 11 qualifying events.
- So this corpus — which is *more* Slack-heavy than a typical two weeks — would
  have produced **3 bounces total.** Split into counseled vs un-counseled, that
  is ~1–2 per group. The proof needs ≥2–3 *counseled-and-revised* alone, plus a
  comparable baseline. **The design cannot reach its own keep/kill threshold in
  the stated window at the observed base rate.** It will land at "inconclusive,"
  which the Anti-Metrics correctly call out as the failure-of-failures (signal
  logged, never decisive).

**Minimal fix:** either extend the window until N is reached (make the proof
event-count-driven, not calendar-driven — "decide at ≥6 bounces, ~half
counseled," not "at 2 weeks"), OR raise events per session by replacing
once-per-session with once-per-*channel*-per-session (still bounded, still
honors "never twice for the same message," but doesn't spend the whole budget on
a routine first message — see SHOULD-1). At 3 bounces total the experiment is
underpowered by construction; shipping it as-is guarantees the measurement-theater
anti-metric.

### BLOCK-3 — There is no Slack MCP server in this repo's install path, and INSTALL.sh only links agents. The skeleton has no live trigger surface. (blocking-for-skeleton)

The Slack MCP (`plugin_slack`) is a **plugin** active in the user's *other*
projects; it is not configured in `~/.claude/settings.json`'s `mcpServers`
(which lists only imagesorcery, simplifi, local-llm), and jixia-advisors'
INSTALL.sh installs **agents only** — no hooks, no settings-merge, no MCP wiring
(verified: the script loops `claude/agents/*.md` and nothing else; `claude/hooks/`
does not exist). Task 3.1 says "document the settings-merge block" — *document*,
not apply. So at the end of the skeleton:

- The hook files exist on disk but are wired into nothing (no PreToolUse/
  PostToolUse matcher is actually registered in settings).
- Whether the Slack plugin is even loaded in a jixia-advisors session is
  unverified. If the user runs Claude in this repo and the plugin isn't active,
  the trigger never fires and the 2-week clock measures nothing.

This is the behavioral-config trap from the user's own tdd-enforcement rule: a
hook that parses is not a hook that fires. "Document the settings-merge" is the
parse rung; the design owes the **observe** rung — *a real send attempt in a
real session produces a real bounce in the log.*

**Minimal fix:** the skeleton's done-bar must include one observed end-to-end
fire: install, attempt a qualifying send via the actual Slack tool name, confirm
a `bounced` record lands in `~/.claude/jixia/counsel-log.jsonl`. Add the
settings-merge as an *applied* step with a verification, not a documented
suggestion. Until one real bounce is observed, the skeleton has not tested the
riskiest assumption — it has only tested that Python runs.

### BLOCK-4 — Channel-vs-DM detection works, but the floor is mis-specified against the real ID space, and "multi-person DM" defeats it both ways. (blocking-for-skeleton)

Good news the design got lucky on: channel type **is** derivable from
`tool_input` — but not how the design implies. The input carries only
`{channel_id, message}` (+ optional `thread_ts`). The *type* is in the ID
prefix: `D…`=DM, `C…`=channel/group, `U…`=user, and a comma-joined
`U…,U…`=ad-hoc multi-person DM. The reliable signal (`is_dm:true/false`,
`name`) is in the tool **result**, which PreToolUse does **not** have — it only
sees the input. So the hook must classify from the `channel_id` prefix alone.
The real data breaks the "channel-wide (not DM)" floor:

- A `C…` ID is **not** "a team channel." In the data, `C0B7FNHGGDB` resolves to
  `name:"mpdm-tia.allen--alexanderv--michael.schoen-1"`, `is_dm:false` — a
  **3-person DM**, semantically a private conversation, that the prefix-only
  floor will treat as a public channel and bounce. False positive on exactly the
  intimate low-stakes case the floor is supposed to exclude.
- Conversely `ULPLLCRQF,U04NA84CB` (comma-joined `U…`) is a multi-person
  group send that is *not* a `C…`, so the floor passes it through — even though
  "flagging an overlap before these PRs merge so we don't ship three…"
  (the actual message) is the org-dynamics-sensitive case the system most wants
  to catch. False negative on the target case.
- `mpdm-…` channel names are the only way to distinguish a real channel from a
  group DM, and that name is **not in the PreToolUse input.**

**Minimal fix:** the spec must define the floor against the *prefix taxonomy
that actually exists* (`D`, `C`-but-could-be-mpdm, `U,U,…`), state explicitly
that PreToolUse cannot see `is_dm`/`name`, and decide the mpdm cases on purpose.
The current "channel vs DM" framing is a two-category model of a four-category
reality and will fire on private group chats while missing group-send pile-ons.
The negative-control scenario ("routine DM passes") tests the easy `D…` case and
hides this.

### SHOULD-1 — Once-per-session keying under-fires exactly as feared; the first qualifying message is usually not the sensitive one. (should-fix)

The design defends session-keying only against *over*-firing (a re-draft has a
new hash). It never addresses under-firing. In the data, sessions fire 2–6
qualifying sends; the bounce lands on whichever is *first*, which is frequently a
status update or incident note (`"Incident-92 cleanup ran tonight…"`), not the
later genuinely-contested message. Budget spent, sensitive message sails through.
**Minimal fix:** key once-per-*channel*-per-session, or once per session but only
spend the bounce on the *highest-sensitivity* message seen so far. Either keeps
the "never twice for one message" promise without blowing the budget on routine
traffic. Folds naturally into the BLOCK-2 sample-size fix.

### SHOULD-2 — The PreToolUse deny may be consumed by reflexive model retry; the human whose behavior must change never sees the lens. (should-fix)

problem-framing.md §Behavioral population names the *user* as the population that
must "read and act on counsel." But a PreToolUse `deny` returns a reason to the
**model**, and models retry denied tool calls reflexively — the design's own
escape text ("retry to send as-is") is an *instruction the model can satisfy
without ever surfacing the suggestion to the human.* If the agent reads "deny:
consider an org-dynamics lens, or retry to send as-is" and just retries, the
bounce fired, a `bounced` record logged, the message went out unchanged, and the
human never saw a thing. The log will show "bounce ignored" and the design will
read it as "user chose not to revise" — when actually the user was never asked.
This is an **oracle-validity** bug: the un-counseled baseline is contaminated by
model-auto-retries that look like human dismissals. **Minimal fix:** the deny
reason must instruct the model to *surface the suggestion to the user and stop*,
not offer a retry the model can take autonomously; and the records should capture
whether a `/advise` or a human turn intervened, so model-auto-retry can be
excluded from the baseline rather than counted as a dismissal.

### SHOULD-3 — The routing table (task 1.1) is an unbounded design problem wearing a 60-minute estimate. (should-fix)

Task 1.1 — "selection table over the 16 agents by question type" — is the one
place the whole "specific, named lens at the moment it applies" value prop lives,
and it is **specified nowhere.** specs/advise-skill.md gives ONE example
(org-dynamics message → behavioral-psychologist / manager-tools) and an override
syntax. There is no table mapping question/draft types to {primary, counter-lens}
across 16 agents, no definition of "question type," no tie-break, no default when
nothing matches. That is not a 60-minute SKILL.md write; it is the core taxonomy
design, and burying it in a skeleton task hides the hardest part (the user's own
honest caveat — "the premise 'advice would have helped' is unconfirmed" — bites
hardest precisely on whether the *right* lens gets picked). **Minimal fix:** pull
the routing table into its own design artifact with the 16→type mapping and an
explicit "no confident match → don't fire / fall back to counter-lens-only" rule,
reviewed before 1.1 is estimated. At minimum, scope the skeleton to 2–3 question
types end-to-end and say so, rather than implying all 16 are routed.

### SHOULD-4 — Fail-open is correct but the design has no fail-open *visibility*; silent floor failure looks identical to "no sensitive messages." (should-fix)

spec send-bounce §fail-open mandates "errors MUST never block" — right call. But
combined with BLOCK-3 (hook may be wired into nothing) and BLOCK-4 (floor may
mis-classify), a fail-open hook that silently does nothing is indistinguishable
from a hook correctly seeing no qualifying traffic. At the 2-week mark the report
shows "0 bounces" and the user cannot tell "the experiment ran and messages
were benign" from "the hook never fired because it wasn't wired / threw on every
payload / the plugin wasn't loaded." **Minimal fix:** log a lightweight
`floor_evaluated` heartbeat (count of sends seen, qualifying or not) so a
zero-bounce report is interpretable. Without it, fail-open silently converts a
plumbing failure into a false "messages didn't need advice" conclusion — the
worst outcome for a keep/kill experiment.

### NOTE-1 — `draft_hash` correlation key is fragile across the re-draft flow.

counsel-log §cross-component-correlation correlates bounce/counsel/sent by
shared session/hash. But the natural flow is: bounce on draft H1 → `/advise` →
model rewrites → re-draft H2 → send. The `counseled` record is keyed to the
*draft it counseled on*; if that's the pre-revision text, hash linkage between
`bounced` (H1) and `sent` (H2) is via session+channel, not hash. Make
session+channel the primary correlation key and treat hash as evidence-of-change,
not as the join — otherwise the report's "was this bounce followed by counsel"
join silently misses the revised cases, which are precisely the *successes* you
want to count.

### NOTE-2 — Denial text bureaucracy compliance is asserted, not shown.

design.md leans on the repo's gate-design rules (escape-in-denial, persistent
signal, value-not-presence). The escape path is present ("retry to send
as-is"). The persistent signal is present (counsel-log). But **value-not-presence
validation** has no analog here — there's no check that the lens named in the
denial actually resolves to a real advisor for the message type (a bounce that
says "consider a relevant lens" with no specific agent is the horoscope
anti-metric in the denial itself). Tie the denial's named lens to the BLOCK-/
SHOULD-3 routing table and assert it's a real agent name, or the gate ships
mock-bureaucratic by its own repo's standard.

## Verdict

**RETHINK.**

Not because the idea is bad — the problem is real (16 agents, ~zero
consultations) and the instinct to make the changed-action signal *mechanical
rather than self-reported* is exactly right. RETHINK because the skeleton, as
specified, **cannot execute its own oracle**: the tool it intercepts stages
human-edited drafts the PostToolUse hook can never observe (BLOCK-1); the base
rate plus the once-per-session cap deliver ~3 bounces in a window that needs
many more (BLOCK-2); nothing is actually wired to fire (BLOCK-3); and the
sensitivity floor is a 2-category model of a 4-category ID space that bounces
private group chats and waves through group-send pile-ons (BLOCK-4). Each of the
four is a "the experiment silently produces an uninterpretable result" failure —
the precise outcome problem-framing.md and the Anti-Metrics were written to
avoid.

Fixable, and the fixes are mostly *specification* work, not new scope: pick the
real tool and redefine the diff around drafts; make the proof event-count-driven;
make install an applied+observed step; rewrite the floor against the real prefix
taxonomy. Do those four before estimating tasks, and this becomes PROCEED. As
written, the 3 tasks are not 30–60 min each — 2.1 hides the entire tool-semantics
+ floor-taxonomy problem and 1.1 hides the routing taxonomy.

## What I'd break first

I'd send three messages in a normal work session — a routine incident-status note
to `#incident-92`, then a contested "we're overlapping, let's align before these
PRs merge" to a `U…,U…` group DM, then a sharp piece of feedback to a `mpdm-…`
three-person DM that carries a `C…` id. The hook spends its one-per-session
bounce on the *routine status note* (first qualifying send, BLOCK-2/SHOULD-1),
waves the genuinely-contested group-DM message straight through because it's
`U…` not `C…` (BLOCK-4 false negative), and would have bounced the private
3-person feedback chat as if it were a public channel (BLOCK-4 false positive) —
except it never gets the chance because the budget's gone. Whatever did get
bounced was a `slack_send_message_draft` call, so the human opens the draft in
Slack, edits it, and sends it by hand — and the PostToolUse hook, watching only
Claude Code tool calls, records **no `sent` event at all** (BLOCK-1). Two weeks
later the report reads "1 bounce, 0 sends captured, inconclusive," and nobody can
tell whether the idea failed or the plumbing did (SHOULD-4). The design dies of
measurement theater — the one death its own Anti-Metrics named.
