# Jixia Product Tour

This is a representative walkthrough of behavior already present in the
repository. It is not a captured consultation, testimonial, benchmark, or
promise that the advice will improve every decision.

The example is a real kind of operator problem: announcing a new team-management
practice whose intended accountability benefit may also create surveillance,
gaming, or trust costs. The consultation is hypothetical; the control surfaces
and output contracts are not.

## Try it after installation

In Claude Code, give `/advise-full` the full question, audience, and desired
outcome:

> /advise-full I am considering a daily individual sales leaderboard in our manager
> dashboard. The audience is the sales team and their managers. I want earlier
> coaching and clearer accountability without encouraging public shaming or
> metric gaming. Should we ship it, change it, or reject it?

There is no separate Jixia application. `/advise` is the shortest installed
front door. This tour deliberately uses `/advise-full` to show and override the
recommendation before anything runs. That produces a named practical roster the
installed surface can dispatch end to end. In Codex, invoke one of the six
repo-local method skills directly while this repository context is active.

## 1. Frame the work

Jixia keeps the exact prompt rather than reducing it to “review a dashboard.”
The artifact, audience, relationship, stakes, and desired outcome travel with
the consultation. That verbatim context is the defense against generic,
horoscope-like advice.

The operator remains the decision owner. Delegating counsel does not authorize
Jixia to publish the dashboard, message the team, or make the policy choice.

## 2. Route to the method

`/advise` runs the existing deterministic classifier. A clear specialist signal
selects one of the six registry methods; weak or tied evidence falls to the
adaptive `jixia` default instead of fabricating confidence.

On the first turn, the surface names the selected method, roster type, and
dissent seat. If the selection looks wrong, `/advise-full` presents the same
pick as a preselected menu that the operator can accept or override in one reply.

For this exact prompt, the current menu recommendation is:

```text
method: yushitai
roster: historical
confidence margin: 1
dissent seat: discipline-impeachment-censor
```

That is an inspection-and-accountability recommendation, not the everyday
`jixia` fallback. The prompt's accountability language is the winning specialist
signal. This tour does not accept that historical route: the current installed
front door resolves its method, roster policy, and dissenter, but does not carry
the historical roster definitions and output contract into its run plan.

## 3. Resolve an installed roster

Reply to the preselected menu with an explicit practical override:

> Use jixia with the practical roster and exactly behavioral-psychologist and
> management-philosophizer.

The current executable resolver returns:

```text
method: jixia
roster: practical
agents: behavioral-psychologist, management-philosophizer
dissent seat: management-philosophizer
override: true
```

Both named advisors are part of the 20-agent pool installed by `INSTALL.sh`.
Every advisor receives the verbatim prompt and the same stakes context. This
explicit override avoids pretending that the current installed auto-route can
expand a historical method plan it does not yet carry.

## 4. Keep dissent structural

For this resolved run, `management-philosophizer` holds the dissent seat. Its
instruction is to argue the strongest counter-case, resist agreement, and avoid
softening merely because the voices converge.

The operator may swap who holds that seat. An attempt to remove it re-seats the
default. This preserves productive disagreement without requiring a large
council.

## 5. Synthesize into action

The response attributes material points to their lenses, names the dissenter's
counter-case, and ends with a concrete change. A representative synthesis for
this resolved practical run is shaped like this:

```text
diagnosis
- The proposal combines a legitimate need for earlier coaching with public
  comparison, which creates plausible shaming and metric-gaming pressure.

selected lenses
- behavioral-psychologist: examine incentives, safety, and gaming behavior.
- management-philosophizer: test whether withholding visible accountability
  protects comfort at the expense of results.

dissent
- Rejecting comparison entirely can conceal persistent performance gaps. Test
  whether a transparent but carefully scoped signal improves coaching without
  creating the harms above.

next action
- Do not ship the public ranking as proposed. Prototype a manager-only coaching
  view, define guardrails and success criteria, and review a time-bounded pilot
  before broader release.
```

This is illustrative counsel, not the transcript of an observed run. Its fields,
resolved roster, and dissent occupant match the executable plan; the particular
recommendation remains a representative synthesis.

## 6. Learn without pretending

The route and consultation are logged. When the optional Claude Slack
send-bounce path is involved, the counsel report can distinguish counseled and
baseline restaging by session and channel. An ad-hoc question still records the
route, but it has no Slack bounce to join.

Those records can reveal routing acceptance, overrides, and draft restaging.
They do not by themselves establish that the advice caused a better decision.
That outcome is not proven by the current public evidence and remains the
important unfinished product question.

## What the operator experiences

Jixia replaces “ask the model to think harder” with a deliberate advisory move:
bring in the few perspectives that see different failure modes, preserve one
counter-case, and leave with an action rather than a transcript of debate.

For the implementation record and counterevidence, see
[Evidence](EVIDENCE.md). For current delivery boundaries, return to
[Current surfaces and truthful limits](../README.md#current-surfaces-and-truthful-limits).
