# Jixia Advisors

**The advisory layer for agentic work.**

> **Convene the right perspectives. Leave with a practical next action.**

**A companion to [Escapement](https://github.com/alexander-vyh/escapement).**

Jixia helps operators bring specialist judgment into decisions, drafts, reviews,
and operating problems without turning every question into a committee. It
routes the work to the smallest useful set of advisor lenses, keeps a dissenting
view in the room, and synthesizes the result into something the operator can do.

This repository is a source-controlled personal advisory system, built first for
operators using coding agents on real management, product, design, and operations
work. Its lenses are opinionated and adaptable, not universal expertise.

[Install for Claude Desktop, ChatGPT Desktop, omp, or Codex](#desktop-plugins-and-portable-skill) · [Install the Claude Code integration](#install-the-claude-surface)

## The advisory loop in two minutes

```text
frame → route → convene → dissent → synthesize → act → learn
```

On the Claude Code integration, start with the real question or artifact.
`/advise` resolves an automatic recommendation; `/advise-full` exposes it as a
preselected menu. The installed path demonstrated in the tour is a practical-agent override: it
passes the verbatim material to named installed advisors, retains a mandatory
counter-case, and returns counsel with a concrete action. The automatic
historical-route gap is disclosed below.

The walkthrough uses the existing Claude surface on a consequential team-message
decision. It is representative, not a captured consultation or proof that the
advice improves the decision.

[Open the representative product tour](docs/PRODUCT_TOUR.md)

## Evidence, including the unfinished proof

Jixia's public evidence is strongest about mechanism and weakest about outcome
quality. The repository shows that its six methods are structurally distinct,
that routing and dissent survive named bad implementations, and that independent
review found and repaired silent measurement defects. It does not yet publish a
benchmark showing that the resulting counsel improves real decisions.

[Inspect the evidence](docs/EVIDENCE.md)

## Start with the question you have

| What you need | Start here | What should come back |
|---|---|---|
| The router's automatic recommendation | `/advise` | A selected method, roster policy, and dissenter; see the historical-route caveat below |
| A recommendation you can inspect first | `/advise-full` | A preselected method you can accept or override in one reply |
| A currently demonstrable installed consultation | `/advise-full`, then name a practical roster and exact agents | Attributed counsel, explicit dissent, and one concrete next action |

`/advise` remains the fastest front door. The representative tour uses the third
path because every advisor it dispatches is present in the installed pool.

## Current surfaces and truthful limits

The repository currently contains 20 advisor lenses and six convening methods.
Their source contracts are shared, but host delivery is asymmetric:

- `INSTALL.sh` globally installs only the Claude Code surface: advisor agents,
  `/advise`, `/advise-full`, routing modules, the counsel report, and the
  connector-dependent Slack send-bounce hooks. It does not install the direct
  method command files under `claude/commands/`.
- omp and Codex can discover the portable `advise` skill and six repo-local method skills.
  Desktop plugins package the same `advise` workflow with its own copy of the core;
  they do not depend on a checkout, the Claude Code installer, or personal agents.
- The Slack send-bounce hook is Claude-specific, connector-name-dependent, and
  fail-open. It stages selected qualifying messages for counsel; it is not a
  universal approval gate and does not prevent every sensitive send.
- Routing records, mutation tests, and fixture-based restage tests exercise the
  mechanics and attribution joins. The repository publishes no real restage
  corpus, and better decision quality is **not proven** by the current evidence.
- The `INSTALL.sh` auto-router resolves a method, roster policy, and dissenter, but
  its run plan does not carry historical roster definitions or method output
  fields. Because `INSTALL.sh` also omits the direct method wrappers, automatic
  historical routes are not yet independently proved executable end to end. The
  representative tour uses an explicit practical-agent override that is.
- Historical names describe operating patterns and source-grounded review
  stances, not direct institutional continuity or timeless authority.

Jixia is not a hosted service, a general expert system, or a rule that more
agents are better. The default is the smallest relevant roster that changes the
answer.

[Browse the complete advisor roster](docs/ADVISOR_ROSTER.md), including each
lens's purpose and current model-pin policy, before installing anything.

## Desktop plugins and portable skill

This repository is a plugin marketplace named `jixia`. Its catalog,
`.claude-plugin/marketplace.json`, lists one plugin, `plugins/jixia-advisors/`:
the `advise` skill, the 20 advisors as named agents, and the method registry.
Installing needs no build, connector, or API key.

| Host | How to install |
|---|---|
| Claude Desktop | **Customize → Plugins → Add marketplace** → `alexander-vyh/jixia-advisors`, then install **Jixia Advisors**. Use **Check for updates** or **Sync automatically** to pick up changes. To use the skill in chat, [enable **Code execution and file creation**](https://support.claude.com/en/articles/12512180-use-skills-in-claude) under **Settings → Capabilities**. Cowork and Claude Code can also dispatch the bundled named agents as `jixia-advisors:<advisor-id>`. |
| ChatGPT Desktop | With Codex CLI installed, run `codex plugin marketplace add alexander-vyh/jixia-advisors`. Restart ChatGPT Desktop, open **Plugins** in Work mode or Codex, select the `jixia` marketplace, and install **Jixia Advisors**. [Marketplace guide](https://developers.openai.com/plugins/build/plugins) |
| ChatGPT workspace | Run `./bin/build-plugin` to write `dist/jixia-advisors.zip`. Where workspace uploads are enabled, an eligible administrator can upload it on the web under **Admin console → Plugins → Add → Upload plugin**. Members then install it from their workspace directory in Desktop. [Permissions and availability](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt) |
| Codex CLI | `codex plugin marketplace add alexander-vyh/jixia-advisors`, then `codex plugin add jixia-advisors@jixia`. In this checkout, `$advise` works without installing. |
| omp | `omp plugin marketplace add alexander-vyh/jixia-advisors`, then `omp plugin install jixia-advisors@jixia`. In this checkout, `/skill:advise` works without installing. |
| Other Agent Skills hosts | Copy `plugins/jixia-advisors/skills/advise/` into the host's skills directory. It carries its own resources. |

Try **“Use Jixia Advisors to review this rollout decision. Show me the proposed
method and roster before proceeding.”** Accept or change the selection; expect
each advisor's own view, their exchange and remaining disagreements, the
counter-case, then the method's ruling and a concrete next action. In plain chat
these are lenses applied in one conversation, not separate agents. When Python
is unavailable the skill uses the bundled method and roster files directly.
The plugin includes no Slack hooks, connectors, or counsel logging.

Maintainers: `agents/`, `skills/advise/jixia/`, and `.claude-plugin/plugin.json`
inside the plugin are copies generated from `jixia/`. After changing `jixia/`, run
`./bin/build-plugin`; the tests fail while those copies are stale. Claude Code and
Codex cache installs by `version`, so raise it in
`plugins/jixia-advisors/plugin.json` when releasing a change.

## Install the Claude surface

For Claude Code's unnamespaced `/advise`, `/advise-full`, report, and Slack
integration, use the existing installer rather than the desktop ZIP:

```sh
git clone https://github.com/alexander-vyh/jixia-advisors.git
cd jixia-advisors
./INSTALL.sh
```

**Upgrading an existing Claude Code install?** After `git pull`, run `./INSTALL.sh`
from this checkout. Advisors moved from `claude/agents/` to `jixia/advisors/`;
until you rerun the installer, the old advisor links are broken. Rerunning is
safe: the installer refreshes links and backs up existing regular advisor files.

Uninstall:

```sh
./INSTALL.sh --uninstall
```

Uninstall removes Jixia's symlinks and settings entries; backups remain.

## Advisory model and roster

`jixia-advisors` is an adaptive forum, not a fixed council. Most work should use
one advisor or one advisor plus a counter-lens. Broader questions may use three
to five advisors. `seven-sages` caps breadth at seven selected voices.

The six methods behave differently rather than merely changing costumes:

- **Jixia:** everyday triage and a right-sized practical lens set.
- **Seven Sages:** bounded breadth and a convergence/divergence synthesis.
- **Areopagus:** jurisdiction, evidence, verdict, and remedy.
- **Junto:** queries, experiment, commitment, and follow-up.
- **Parishad:** authority, role obligations, conflict, and settlement.
- **Yushitai:** inspection path, findings, severity, ownership, and correction.

The installed `/advise` and `/advise-full` routes retain one real,
low-sycophancy dissent seat. The holder can change; those front doors do not let
the counter-case disappear silently. Direct method wrappers have their own
contracts and do not all impose that seating mechanism. See
[the advisory model](docs/advisory-model.md) for the full method rationale and
[the source packets](docs/historical-council-sources/README.md) for the optional
historical representative lenses.

## Repository anatomy

| Area | Purpose |
|---|---|
| `jixia/advisors/`, `jixia/reps/` | Canonical practical advisor definitions and source-grounded historical lenses |
| `.claude-plugin/marketplace.json`, `plugins/jixia-advisors/` | Marketplace catalog and the installable plugin for desktop and CLI hosts |
| `bin/build-plugin` | Refreshes the plugin's generated copies of `jixia/` and zips it for upload |
| `claude/skills/advise/` | Automatic routing front door |
| `claude/skills/advise-full/` | Preselected menu and override surface |
| `claude/commands/` | Direct Claude method wrappers kept in source but not installed by `INSTALL.sh` |
| `.agents/skills/` | Repo-local skill discovery for omp, Codex, and other Agent Skills hosts |
| `jixia/registry.json` | Canonical method gates, rosters, phases, outputs, and refusals |
| `jixia/*.py` | Deterministic routing, dissent, and menu mechanics |
| `claude/hooks/` | Optional Slack send-bounce observation |
| `bin/jixia-counsel-report` | Mechanical routing/restage evidence report |

On hosts that honor Claude agent frontmatter, eight high-stakes advisor definitions
omit a model pin and inherit the current session model. The remaining 12 retain a `sonnet` pin as a
cost/latency choice. Host model selection, availability, and behavior remain
outside Jixia's control.

## Name and scope

The name comes from Jixia, the Warring States Qi intellectual community where
thinkers from multiple traditions were supported near power. Here it names a
forum that selects useful disagreement near the work.

Jixia holds personal preference: the frameworks and lenses its owner wants
available. Escapement owns reusable workflow control, delivery, and verification.
Keeping them separate lets Jixia remain eclectic without muddying Escapement's
control-system contract.

The operating patterns draw from management, behavioral psychology, Lean,
service design, information design, value creation, capital allocation, and the
historical sources documented in this repository.
