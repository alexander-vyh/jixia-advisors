# Problem Framing — advisor-routing

Confirmed with the user, 2026-06-11 (inline confirmation pass; escapement
supervisor session).

## Problem

16 deployed advisor agents (psychology, org-dynamics, management, UX,
productivity lenses) are consulted only when the user or model remembers them
at the right moment, which is rarely. Observable: near-zero advisor dispatches
in recent session history against daily moments where their lenses apply
(Slack messages with org-dynamics stakes, what-to-work-next choices).

## Why now

Recurring felt cost: messages and prioritization decisions keep going out
without lenses that already exist on disk — noticed enough times to act on.
Honest caveat (recorded deliberately): there is no forcing incident, and the
premise "advice would have helped" is itself unconfirmed — the design must
make that premise measurable rather than assume it.

## Decision authority

The user (alexander-vyh). Solo personal repo; the user owns the what and why.

## Behavioral population

Primary: Claude sessions (they must start consulting advisors at relevant
moments — mechanical routing). Secondary: the user (must read and act on
counsel rather than tolerate-and-ignore nudges).

## Riskiest Assumption

Betting: advisor counsel delivered at the moment of work changes the next
action often enough to be worth the friction. Wrong when: nudges fire, counsel
is generated, and messages/decisions ship unchanged anyway. Would know within
~2 weeks via the fired → followed → changed-action signal record.

## Success criteria

(Revised 2026-06-11 after adversarial review measured the real base rate: a
calendar window is underpowered by construction; the proof is event-count
driven.) Decidable at ≥6 bounces with ≥2 in each comparison group: counseled
bounces show restage rate/distance above the un-counseled baseline (the
mechanical changed-the-next-action metric), AND the trigger is still enabled
and not reflexively dismissed. Both halves required — value AND tolerability.
