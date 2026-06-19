# Tasks — advisor-routing

Walking skeleton (tests the riskiest assumption: counsel at the moment of work
changes what gets staged, measured mechanically). Revised after adversarial
review — see review-discovery.md and the design's revision note.

## 1. Routing table + `/advise` skill (front door)

- [ ] 1.1 Author the skeleton routing table as part of the skill: 2–3 question
      types end-to-end (outward message with org-dynamics stakes;
      what-to-work-next prioritization; optionally UX critique), each mapping
      to {primary, counter-lens} among the 16 agents, with an explicit
      no-confident-match rule (offer the agent list, never guess). Then
      `claude/skills/advise/SKILL.md`: dispatch with verbatim draft + audience
      context, synthesize, append `counseled` record to
      `~/.claude/jixia/counsel-log.jsonl`. No self-report question.
      Spec: specs/advise-skill.md. ~60 min (table is the hard half — if it
      exceeds the box, stop and split rather than hand-wave it).

## 2. Send-bounce hook pair

- [ ] 2.1 `claude/hooks/jixia_send_bounce.py`: PreToolUse on BOTH
      `slack_send_message_draft` AND `slack_send_message`; floor from
      channel-id prefix taxonomy (D never / U,U-group eligible / C eligible
      with documented mpdm false-positive) + length/markers; once per
      (session, channel); denial names the routed real lens and instructs the
      model to surface it to the human and STOP (no autonomous retry);
      `floor_evaluated` heartbeat on every staging; fail-open. PostToolUse
      `restaged` capture for bounced channels. Tests per specs/send-bounce.md
      scenarios incl. group-send-bounces and second-channel-still-eligible.
      ~60 min.

## 3. Counsel report + applied-and-observed install

- [ ] 3.1 `bin/jixia-counsel-report` (stdlib): join by (session, channel),
      exclude auto-retries from baseline, restage rate + difflib distance per
      group, DECIDABLE/NOT-YET line at ≥6 bounces ≥2/group
      (specs/counsel-log.md). Extend INSTALL.sh to deploy skill + hooks AND
      apply the settings merge (PreToolUse/PostToolUse matchers on both Slack
      staging tools), warning when the Slack plugin is absent. ~45 min.
- [ ] 3.2 Observed end-to-end fire (the skeleton's real done-bar): in a live
      session with the Slack plugin, stage one qualifying message; confirm a
      `bounced` record (and heartbeat records) land in the counsel log; confirm
      the lens suggestion reached the human. Install that merely parses is not
      done — this is the behavioral-config observe rung. ~15 min.

Done when (proof of delivery): the counsel report reaches DECIDABLE (≥6
bounces, ≥2 per group — event-count, not calendar) showing counseled restage
rate/distance above the un-counseled baseline, with the trigger still enabled
— not when the hooks merely ship.
