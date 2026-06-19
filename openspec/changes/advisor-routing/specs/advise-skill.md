<!-- Spec: advise-skill -->

## Purpose

The `/advise` skill is the front door to the advisor pool: it routes a
question or draft to one advisor plus one counter-lens (the everyday Jixia
default), synthesizes their counsel into usable form, and records the
consultation mechanically.

## Requirements

### Requirement: lens-routing

The skill SHALL select exactly one primary advisor and one counter-lens.
Skeleton scope (lean review, post-SHOULD-3: the oracle compares counseled vs
un-counseled, never lens-vs-lens, so routing variety feeds it nothing): ONE
hardcoded pair — {behavioral-psychologist, manager-tools-advisor} — for the
single routed type, outward message with org-dynamics stakes. The 2–3-type
routing table is the first post-skeleton increment. When no type matches confidently,
the skill SHALL say so and ask rather than fire a low-confidence lens. Every
lens name emitted (including in bounce denial text) MUST resolve to a real
deployed agent file. The user MAY override by naming advisors explicitly.
Routing the full 16-agent taxonomy is a future increment, not skeleton scope.

#### Scenario: no-confident-match

- **WHEN** `/advise` is invoked on a question outside the skeleton's routed types
- **THEN** the skill states no confident routing exists and offers the agent
  list rather than dispatching a guessed lens

#### Scenario: org-dynamics-message

- **WHEN** `/advise` is invoked on a draft Slack message announcing a process
  change to a team channel
- **THEN** the skill selects a psychology/org-dynamics-relevant primary (e.g.
  `behavioral-psychologist` or `manager-tools-advisor`) plus a counter-lens,
  states why, and dispatches both with the full draft text and audience context

#### Scenario: explicit-override

- **WHEN** `/advise ui-design-critic: <question>` names an advisor
- **THEN** the named advisor is the primary; routing selects only the counter-lens

### Requirement: counsel-grounding

Dispatched advisors MUST receive the actual draft text and audience/stakes
context, never only a topic summary, so counsel is specific to the artifact
(anti-horoscope).

#### Scenario: draft-passed-through

- **WHEN** the skill dispatches advisors for a bounced Slack draft
- **THEN** each advisor prompt contains the verbatim draft text and the
  channel/audience context captured at bounce time

### Requirement: consultation-record

On completion the skill SHALL append one consultation record to
`~/.claude/jixia/counsel-log.jsonl` containing: timestamp, session id, lenses
used, the draft hash it counseled on (when counseling a draft), and a
counsel-summary digest. The skill MUST NOT ask the user whether the counsel
changed their action — changed-action measurement is mechanical and lives in
`counsel-log`.

#### Scenario: record-written

- **WHEN** a counsel pass completes for draft hash H
- **THEN** the counsel log gains a `{"kind":"counseled", "draft_hash":"H", ...}`
  record, and no self-report question is asked
