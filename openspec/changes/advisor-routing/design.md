# Design — advisor-routing

> Revised 2026-06-11 after adversarial review (review-discovery.md, verdict
> RETHINK→fixes applied, user-approved): oracle redefined around the real
> dominant tool (`slack_send_message_draft` stages human-edited drafts — the
> send itself is unobservable), proof made event-count-driven, bounce keyed
> per-channel-per-session, floor rewritten against the real channel-ID
> taxonomy, denial must reach the human, install is applied-and-observed.

## Problem Statement

Counsel from the 16 deployed advisors reaches real work only when someone
remembers to ask — observably, almost never. After this change, Claude
sessions surface a specific, named lens at the moment it applies (an
org-dynamics pass before a sensitive Slack message; later, a prioritization
lens at a backlog fork), and every consultation leaves a *mechanical* record
of whether the action changed — measured by tooling, never by self-report.

## Non-Goals

1. **No always-on advisory rule.** No resident CLAUDE.md/rules text telling
   every session to "consider advisors" — the compliance-based pattern this
   user's repos migrated away from twice (gate-design, beads-worktree). Locks
   in: sessions without a trigger moment get zero advisor presence, by design.
2. **No standing gates.** The system never *prevents* a send and never bounces
   the same message twice: at most ONE deferral per channel per session, the
   escape path is in the denial text (surfaced to the HUMAN, who directs
   advise-or-send — never an autonomous model retry), and subsequent stagings
   always proceed. (Deliberately relaxed
   from "never blocks": automatic changed-action measurement requires
   intercepting before the action completes — the one-bounce is the price of
   a mechanical oracle.) Locks in: the system cannot stop a bad message, only
   make a better one cheap.
3. **No multi-mode convening in v1.** Seven Sages / Areopagus / Parishad /
   Yushitai are not built — only the everyday Jixia default (one advisor +
   counter-lens). Locks in: high-stakes decisions get no special machinery yet.
4. **No escapement coupling.** Hooks, skills, and install wiring live entirely
   in jixia-advisors; the escapement framework is untouched (deliberate repo
   split per README scope).

## Capabilities

### New Capabilities
- `advise-skill` — the `/advise` front door: routes a question/draft to one
  advisor + one counter-lens, synthesizes counsel, logs the consultation
  against the draft hash.
- `send-bounce` — sensitivity-gated one-bounce deferral on Slack send tools,
  with draft snapshot at bounce and final-text capture at send.
- `counsel-log` — the user-level mechanical signal record
  (`~/.claude/jixia/counsel-log.jsonl`) and the `jixia-counsel-report` tally
  (fired / counseled / revision-distance vs un-counseled baseline).

### Modified Capabilities
None (greenfield integration layer; `claude/` currently contains only agents).

## Impact

- New: `claude/hooks/` (bounce hook + post-send capture), `claude/skills/advise/`,
  `bin/jixia-counsel-report` (name indicative), additions to `INSTALL.sh`
  symlink PLAN and a documented settings-merge block (PreToolUse +
  PostToolUse matchers on the Slack MCP send tools).
- New runtime state: `~/.claude/jixia/counsel-log.jsonl` (user-level,
  cross-repo — counsel applies wherever work happens; per-repo
  `.gate-signal.jsonl` is escapement-owned and stays out of this).
- No changes to advisor agent files or to escapement.

## Riskiest Assumption

We believe advisor counsel delivered at the moment of work changes the next
action often enough to justify the friction. We will know this is true when
the counsel report shows counseled bounces RESTAGED at a rate/distance above
the un-counseled baseline, decided at ≥6 bounces with ≥2 per comparison group
(event-count, not calendar — the measured base rate makes a 2-week window
underpowered). Honest narrowing, user-approved: the oracle measures whether
counsel changes what the model STAGES; the human's final hand-edit inside the
Slack UI is unobservable by construction. If false, we keep `/advise` as a
manual tool, remove the bounce, and stop investing in routing.

Liveness: if false and undiscovered for two weeks, every sensitivity-qualifying
Slack send has paid a bounce for nothing, and the user has been trained to
reflexively retry — habituation that poisons future advisory attempts.
Significant — the skeleton tests this first.

## Strategic Alternatives

- **Do nothing** — rejected: the status quo is the documented failure state
  (advisors deployed 2026-05-28; consultations since: ~zero).
- **Resident always-on rule** — rejected: per-session token cost, high
  mock-bureaucracy risk, contradicts the repo owner's own rule→hook+skill
  migration history.
- **Human-side habit only** (calendar block, no tooling) — rejected as
  primary: the user owns `habit-architect` and still doesn't consult it;
  unassisted remembering is the disproven mechanism. Kept as a complement.
- **Fold into escapement's skills** — rejected: breaks the deliberate repo
  split; covers only design-time moments, not comms or prioritization.

## Walking Skeleton

1. **`/advise` skill** — router per docs/advisory-model.md (default: one
   advisor + one counter-lens selected from the 16 by question type), feeds
   the actual draft/context to the agents, synthesizes counsel, and appends a
   consultation record (lenses used, draft hash, timestamp) to the counsel
   log. No closing question — measurement is mechanical, downstream.
2. **Send-bounce hook pair** — PreToolUse on BOTH staging tools
   (`slack_send_message_draft` — 88% of real traffic — and
   `slack_send_message`): floor classified from the channel-id prefix taxonomy
   (`D` never; `U,U…` group sends eligible; `C` eligible, mpdm false positives
   accepted and documented) plus length/markers; bounce once per channel per
   session; the denial names a real routed lens and instructs the model to
   surface it to the human and stop — no autonomous retry. PostToolUse captures
   subsequent RESTAGINGS to bounced channels. `floor_evaluated` heartbeat on
   every staging call so zero-bounce reports are interpretable.
3. **Counsel report + applied install** — `jixia-counsel-report` joins
   bounce→counsel→restage by (session, channel), excludes model-auto-retries
   from the baseline, computes restage rate + difflib distance per group, and
   prints DECIDABLE/NOT-YET at the ≥6-bounce threshold. INSTALL.sh DEPLOYS
   hook + skill AND applies the settings merge; the skeleton's done-bar
   includes one OBSERVED end-to-end fire (real qualifying staging → real
   `bounced` record in the log) — install that merely parses is not done.

## Proof of Delivery

This is done when the counsel report reaches DECIDABLE (≥6 bounces, ≥2 per
comparison group — however long that takes) and shows counseled bounces
restaged at rate/distance above the un-counseled baseline, AND the bounce
trigger is still enabled rather than disabled or reflexively dismissed.

## Anti-Metrics

1. Any message bounced more than once, ever (the deferral degrading into a gate).
2. Counsel so generic the user cannot tell which lens produced it (horoscope test).
3. Signal logged but never reviewed — the report exists and is not run at the
   2-week mark (measurement theater).

## Decisions

- **One-bounce deferral over pure-advisory nudge.** Automatic measurement
  requires interception before the send completes; the bounce buys a
  mechanical pre/post diff and a free control group. Alternative (non-blocking
  additionalContext nudge) rejected: counsel would arrive after the message is
  already sent, forcing self-report — which the user explicitly rejected.
- **Mechanical changed-action oracle, draft-restage form.** Diff of
  text-at-bounce vs text-at-restage (difflib ratio), joined by
  (session, channel) — hash only as evidence-of-change, never the join key.
  Alternative (self-report at counsel close) rejected by user. Alternative
  (intercept only true `slack_send_message`) rejected: 12% of measured traffic
  can never reach decision threshold. Limitation accepted and user-approved:
  measures what the model stages, not the human's final in-Slack edit; the
  diff proves change-after-counsel, not causation or quality — the baseline
  comparison (with model-auto-retries excluded) is the causal approximation;
  counsel *quality* benchmarking stays a future increment.
- **Denial must reach the human.** The deny text instructs the model to relay
  the lens suggestion verbatim and stop; records tag whether a human turn
  intervened so auto-retries never masquerade as human dismissals.
- **Counsel log at user level** (`~/.claude/jixia/`), not per-repo: advice
  applies wherever the user works; escapement's per-repo signal corpus is
  framework-owned and deliberately not reused.
- **Cooldown keyed per (session, channel), not per session or message hash** —
  hash-keying re-fires on revised drafts (violates one-bounce); global
  session-keying spends the budget on the first qualifying message, which the
  measured data shows is usually a routine status note, starving the sample
  (review BLOCK-2/SHOULD-1).

## Risks & Trade-offs

- Bounce fatigue → sensitivity floor + once-per-session cap + the report's
  fired/ignored rates feed a half-life review; kill criteria are explicit in
  Proof of Delivery.
- Counsel latency makes /advise unattractive → counsel runs on the bounced
  draft while the user decides; single advisor + counter-lens keeps it small.
- Generic counsel (horoscope risk) → the skill passes the actual draft text +
  audience context to the advisor agents, never just the topic; anti-metric 2
  watches this.
- Tool-shape drift (Slack MCP tool names change) → matcher names centralized
  in one hook file; install verifies the tools exist and warns otherwise.
- Attribution noise (user edits for unrelated reasons) → accepted: the
  baseline comparison absorbs it at keep/kill granularity.

## Future Increments

[PLACEHOLDER] — options purchased by validating the riskiest assumption:

- **Cadence convening** — weekly Junto memo / Monday Parishad backlog pass;
  strongest candidate for increment 2 (guarantees regularity independent of
  trigger precision). Done when a scheduled run produces a memo the user acts
  on, not when the cron fires.
- **Prioritization moment** — advisor recommendation vs observed `bd claim`
  agreement (mechanical, no interception needed). Done when recommendation→
  claim agreement is measurable over real forks, not when the hook ships.
- **More moments** — Gmail, calendar, PR descriptions.
- **Convening modes** — Seven Sages / Areopagus / Yushitai for high-stakes work.
- **Benchmark harness** per docs/advisory-model.md (usefulness, novelty, cost).

## Open Questions

- **[DEFERRABLE]** Which cadence mode ships first in increment 2 (Junto vs
  Parishad) — resolve when that increment starts.
- **[DEFERRABLE]** Whether the sensitivity floor should learn from the
  fired/ignored signal (adaptive threshold) or stay static — needs corpus first.
