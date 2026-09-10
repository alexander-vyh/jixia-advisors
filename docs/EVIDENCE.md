# Jixia Evidence

These are inspectable implementation records, not testimonials and not a
benchmark. The cited pull requests are merged and their bodies report local test
runs, but GitHub exposes no automated GitHub check runs for these changes. The
current repository suite is verified separately. Each record preserves what was
still missing instead of turning mechanism evidence into a claim about counsel
quality.

### PR #5 — implementation record

- **Record:** [Merged pull request #5](https://github.com/alexander-vyh/jixia-advisors/pull/5)
- **Observed PR-body facts:** <q>The six convening methods are now callable and registry-validated.</q>; <q>Both validators exit 0; 26 tests pass.</q>
- **PR-body limit:** <q>T4 (live-output distinctness verification + invocation log) is deferred.</q>; <q>Install wiring: command wrappers exist in-repo but aren't symlinked into ~/.claude/commands/ yet.</q>

### PR #6 — implementation record

- **Record:** [Merged pull request #6](https://github.com/alexander-vyh/jixia-advisors/pull/6)
- **Observed PR-body facts:** <q>fixed advisor pair</q>; <q>dispatches both with the verbatim draft + audience</q>; <q>Restage rate uses a per-group denominator</q>; <q>62 tests</q>; <q>idempotent</q>
- **PR-body limit:** <q>A live /advise invocation observed to append a real counseled record.</q>; <q>≥6 real bounces for an actual DECIDABLE corpus.</q>

### PR #7 — implementation record

- **Record:** [Merged pull request #7](https://github.com/alexander-vyh/jixia-advisors/pull/7)
- **Observed PR-body facts:** <q>surface channel_id in the send-bounce denial</q>; <q>pin the session_id join-key source equivalence</q>; <q>65 passed</q>
- **PR-body limit:** <q>The join holds only because Claude Code populates both from one session UUID</q>

### PR #11 — implementation record

- **Record:** [Merged pull request #11](https://github.com/alexander-vyh/jixia-advisors/pull/11)
- **Observed PR-body facts:** <q>seat_dissenter(model, customization) — the runtime authority for dissent seating.</q>; <q>8 dissent tests green (24 subtests)</q>
- **PR-body limit:** <q>Both are tunable without breaking any test</q>

### PR #15 — implementation record

- **Record:** [Merged pull request #15](https://github.com/alexander-vyh/jixia-advisors/pull/15)
- **Observed PR-body facts:** <q>plan_run() composes the emp.3 classifier and emp.4 dissent invariant into one routing decision</q>; <q>full suite 101 passed</q>; <q>three patch findings</q>
- **PR-body limit:** <q>Deferred to emp.6</q>; <q>exclude fell_back==true from the accept join</q>; <q>installed layout</q>

### PR #16 — implementation record

- **Record:** [Merged pull request #16](https://github.com/alexander-vyh/jixia-advisors/pull/16)
- **Observed PR-body facts:** <q>accept-in-one-reply or model/roster/agent override</q>; <q>suite 138 passed</q>; <q>Dissent seat remains non-removable through every override path.</q>
- **PR-body limit:** <q>Epic emp is now 6/7 — only emp.7 (end-to-end oracle) remains.</q>

## What this evidence supports

The record supports a bounded claim: Jixia provides distinct, callable advisory
methods; routes a real artifact without paraphrasing it; preserves dissent; and
records enough state to inspect routing and restaging behavior.

It does not establish that the router consistently chooses the best method, that
multiple advisors outperform one strong advisor, or that counsel causes better
decisions. Those are outcome questions for a future real-work corpus, not facts
to infer from passing mechanism tests.
