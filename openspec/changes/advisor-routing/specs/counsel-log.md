<!-- Spec: counsel-log -->

## Purpose

The user-level mechanical record of advisor routing (heartbeats, bounces,
consultations, restagings) and the report that turns it into keep/kill
evidence: counseled bounces' restage rate/distance versus the un-counseled
baseline, decided at an event-count threshold rather than a calendar date.

## Requirements

### Requirement: log-format

All components SHALL append JSONL records to
`~/.claude/jixia/counsel-log.jsonl` with at minimum: `kind`
(`floor_evaluated|bounced|counseled|restaged`), ISO `ts`, `session_id`, and
`channel_id`. `bounced`/`restaged` carry text snapshot + hash; `counseled`
carries lenses used and the draft hash counseled on. Records are append-only.

#### Scenario: cross-component-correlation

- **WHEN** a bounce, a counsel pass, and a restage occur for the same channel
  in one session
- **THEN** the three records are joinable on (session_id, channel_id)

### Requirement: session-channel-correlation

The report SHALL join bounce→counsel→restage by (session_id, channel_id) as
the PRIMARY key, treating hash equality only as evidence-of-no-change — never
as the join key (review NOTE-1: revised drafts have new hashes; a hash join
silently drops exactly the success cases).

#### Scenario: revised-draft-still-joined

- **WHEN** counsel leads to a rewritten draft (new hash) restaged to the same
  channel
- **THEN** the report counts it as a counseled-and-revised event

### Requirement: baseline-integrity

The report SHALL classify each bounce→restage pair as counseled (a `counseled`
record intervened) or un-counseled baseline, and SHALL separately tag pairs
where the restage followed with no intervening human turn (model-auto-retry
suspicion) and EXCLUDE them from the baseline rather than counting them as
human dismissals (review SHOULD-2).

#### Scenario: auto-retry-excluded

- **WHEN** a restage occurs with no counsel record and no human turn between
  bounce and restage
- **THEN** the pair is tallied as `auto_retry`, in neither comparison group

### Requirement: event-count-decision

`jixia-counsel-report` SHALL compute from the log alone: heartbeat totals,
bounces fired, counseled vs baseline restage rate and mean difflib distance,
and SHALL print the decision-readiness line: the keep/kill comparison is
DECIDABLE when ≥6 bounces exist with ≥2 in each comparison group — an
event-count threshold, not a 2-week calendar mark (review BLOCK-2: measured
base rate makes a calendar window underpowered by construction).

#### Scenario: underpowered-report-says-so

- **WHEN** the report runs with 3 bounces
- **THEN** it prints NOT YET DECIDABLE with the counts needed, rather than an
  inconclusive-but-official-looking comparison
