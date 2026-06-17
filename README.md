# jixia-advisors

Personal advisor agents for Claude Code, Codex, and other agentic coding
surfaces. The pack provides management lenses, design critics, productivity
advisors, and domain-specific tools. It is source-controlled so the advisors
travel across machines and can be rolled back when a particular lens produces
worse output than expected.

The name comes from Jixia, the Warring States Qi intellectual community where
thinkers from multiple traditions were supported near power. In this repo,
Jixia means an adaptive advisory forum: select useful perspectives for the
question at hand, then synthesize counsel that is practical enough to use.

## Scope

This repo holds **personal preference**: frameworks I draw from, lenses I
think with, and agents I find useful for my own work. It is not a universal
framework, but the structure should be shareable enough that someone else
could adapt the same advisory model.

The **reusable workflow framework** (beads/openspec/continuation harness,
along with the two workflow-integral agents `adversarial-reviewer` and
`test-quality-reviewer`) lives in a separate repo:
[`escapement`](https://github.com/alexander-vyh/escapement). This repo is the
companion to escapement.

This split exists because `escapement` is a sharp,
opinionated framework that someone else might want to adopt; mixing in
the agents in this repo (management philosophizers, ux researchers, etc.)
would muddy that thesis and fail the bureaucracy-design tests its own
rules argue for.

## Advisory Model

`jixia-advisors` is the umbrella, not a fixed council. Most uses should stay
lightweight: one advisor, or one advisor plus a counter-lens. Broader questions
can use three to five advisors. Ambiguous or high-stakes work can use a
Seven Sages-style mode: up to seven selected views from the larger pool.

The repo can support multiple historical convening models:

- **Jixia:** everyday counsel mode. Triage the question, select the smallest
  useful lens set, and synthesize one practical next action.
- **Seven Sages:** bounded breadth mode. Collect up to seven compact principles
  or warnings, compare tensions, and distill short counsel.
- **Areopagus:** adjudicative review mode. Gate jurisdiction, frame evidence and
  harm, then return a verdict, remedy, or remand.
- **Junto:** mutual-improvement mode. Convert the topic into prepared queries,
  experiments, commitments, and follow-up checks.
- **Parishad:** interpretive stakeholder mode. Map authorities, roles, duties,
  conflicts, and the least-violating settlement.
- **Yushitai:** inspection and accountability mode. Trace evidence paths,
  identify control gaps, assign severity, and recommend correction or
  escalation.

The value is not the historical reference itself. The value is relevant
independent perspectives, productive disagreement, clear tradeoffs, and usable
counsel. Each method must behave differently, not merely swap in advisors with
different backgrounds. These modes should be benchmarked against real work
before being treated as settled defaults.

See [docs/advisory-model.md](docs/advisory-model.md) for the fuller naming and
benchmarking model. Historical source packets for the optional representative
lenses live in
[docs/historical-council-sources/README.md](docs/historical-council-sources/README.md).

## Contents

`claude/agents/` contains 20 personal advisor agents, deployed as symlinks into
`~/.claude/agents/`:

- **Management & leadership lenses:** `management-philosophizer`,
  `manager-tools-advisor`, `delegation-accountability-coach`
- **Executive & value creation:** `value-creation-advisor`, `capital-allocator`,
  `ceo-advisor`
- **Productivity & attention:** `attention-coach`, `behavioral-psychologist`,
  `habit-architect`, `personal-lean-advisor`, `personal-systems-integrator`
- **UX & design critics:** `ui-design-critic`, `ux-researcher`,
  `information-architect`
- **Ops & service:** `ops-excellence-advisor`, `service-design-reviewer`,
  `employee-experience-auditor`, `thinking-process-advisor`
- **Domain:** `dashboard-auditor`
- **Value & cost:** `value-translator`

The **Executive & value creation** cluster is deliberately edgy and
returns-first — a counterweight to the people-centric leadership lenses.
`value-creation-advisor` is a PE operating-partner lens (the equity value
bridge); `capital-allocator` is a cold ROIC/capital-allocation lens (Thorndike's
*Outsiders*); `ceo-advisor` is the wartime integrator that names the one binding
constraint. They are built to disagree productively when convened together.

Eight agents are pinned to `model: opus` (`dashboard-auditor`,
`management-philosophizer`, `personal-systems-integrator`,
`thinking-process-advisor`, `value-translator`, `value-creation-advisor`,
`capital-allocator`, `ceo-advisor`), the ones where false negatives or missed
cross-framework tensions are expensive. The remaining 12 are on
`model: sonnet`.

## Install

```sh
git clone https://github.com/alexander-vyh/jixia-advisors.git
cd jixia-advisors
./INSTALL.sh
```

Existing real files at `~/.claude/agents/<name>.md` are backed up as
`<name>.md.backup-YYYYMMDD-HHMMSS` before the symlinks land.

Uninstall:

```sh
./INSTALL.sh --uninstall
```

Removes the symlinks; backups stay.
