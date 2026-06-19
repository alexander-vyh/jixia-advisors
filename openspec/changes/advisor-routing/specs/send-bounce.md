<!-- Spec: send-bounce -->

## Purpose

A sensitivity-gated, bounded deferral on the Slack staging tools: the first
qualifying draft/send attempt per channel per session is bounced once with a
specific lens suggestion that MUST reach the human, snapshotting the draft so
the subsequent re-draft can be diffed mechanically.

Revised after adversarial review (review-discovery.md): the dominant real tool
is `slack_send_message_draft` (15/17 measured calls), which stages a
human-edited draft — the actual send happens in the Slack UI, outside hook
visibility. The oracle is therefore the *draft-at-bounce vs draft-at-recreate*
diff, not a send capture.

## Requirements

### Requirement: target-tools

The hook pair SHALL register on BOTH `mcp__plugin_slack_slack__slack_send_message_draft`
and `mcp__plugin_slack_slack__slack_send_message` (matcher names centralized in
one place in the hook file).

#### Scenario: draft-tool-is-covered

- **WHEN** a qualifying message is staged via `slack_send_message_draft`
- **THEN** the bounce logic applies exactly as for a direct send

### Requirement: sensitivity-floor-taxonomy

The PreToolUse hook SHALL classify the target from the `channel_id` prefix in
`tool_input` — the only signal available pre-execution (`is_dm`/`name` exist
only in tool results): `D…` = DM (never bounce); `U…[,U…]` = user/group send
(comma-joined multi-user sends ARE bounce-eligible — the measured
org-dynamics-sensitive case). Skeleton scope (lean review): `C…` IDs (channel
OR mpdm group chat, indistinguishable pre-execution) are NOT classified in the
skeleton — they pass with heartbeat only; the C/mpdm branch is the taxonomy
increment, deferred because the ≥6-bounce oracle doesn't need that class and
its accepted mpdm false-positive would need caveating. Above the prefix floor,
qualification requires length above threshold OR
feedback/announcement/disagreement markers.

#### Scenario: routine-dm-passes

- **WHEN** a short DM (`D…` channel id) is staged
- **THEN** the hook allows it with only a heartbeat record

#### Scenario: group-send-bounces

- **WHEN** the first qualifying staging this session to a `U…,U…` multi-user
  target carries disagreement-shaped content
- **THEN** the hook bounces it (this was the review's false-negative case; it
  is now in-scope by design)

### Requirement: one-bounce-per-channel-per-session

The hook SHALL bounce at most once per (session, channel) pair — NOT once per
session globally (the review measured 2–6 qualifying sends per session with
the sensitive one rarely first; a global cap starves the sample). A retry or
subsequent staging to the same channel in the same session MUST proceed.
No message is ever bounced twice.

#### Scenario: second-channel-still-eligible

- **WHEN** a bounce fired for channel A and a qualifying message is then staged
  to channel B in the same session
- **THEN** channel B gets its own (single) bounce

#### Scenario: retry-proceeds

- **WHEN** the same or a revised message is staged to a bounced channel in the
  same session
- **THEN** the hook allows it

### Requirement: human-surfacing-denial

The deny reason SHALL instruct the model to RELAY the named lens suggestion to
the user verbatim and STOP — it MUST NOT offer an autonomous retry path the
model can satisfy without the human seeing the suggestion (review SHOULD-2:
model-reflexive retry contaminates the baseline with dismissals no human made).
The named lens MUST be a real deployed agent name resolved from the routing
table for the message type — never a generic "consider a relevant lens"
(value-not-presence, review NOTE-2).

#### Scenario: denial-reaches-human

- **WHEN** a bounce fires
- **THEN** the deny text names a specific real agent + why, and instructs the
  model to surface the suggestion to the user and await their direction
  (advise / send as-is) rather than retrying on its own

### Requirement: recreate-capture

A PostToolUse hook on the same staging tools SHALL append the text of any
SUBSEQUENT staging to a bounced (session, channel) as a `restaged` record —
this is the oracle's second observation (the model re-drafting after counsel
or after the user's direction). The design accepts that the human's final
hand-edit inside Slack is unobservable; the oracle measures whether counsel
changed what gets STAGED.

#### Scenario: restage-recorded

- **WHEN** a bounce fired for (session S, channel C) and a later staging call
  targets C in S
- **THEN** the counsel log gains a `restaged` record with the new text,
  correlated by session+channel

### Requirement: heartbeat-visibility

The PreToolUse hook SHALL append a lightweight `floor_evaluated` record (tool
name, prefix class, qualified yes/no) for EVERY staging call it sees — so a
zero-bounce report is distinguishable from a hook that never fired (review
SHOULD-4: silent fail-open converts plumbing failure into a false "no advice
needed" conclusion).

#### Scenario: zero-bounce-interpretable

- **WHEN** the report runs over a period with no bounces
- **THEN** heartbeat counts show how many stagings were evaluated, proving the
  hook was live

### Requirement: fail-open

Hook errors (unparseable payload, log unwritable, unexpected tool shape) MUST
never block or delay a staging beyond the single designed bounce.

#### Scenario: log-unwritable

- **WHEN** `~/.claude/jixia/` is not writable
- **THEN** the staging proceeds and the hook exits cleanly
