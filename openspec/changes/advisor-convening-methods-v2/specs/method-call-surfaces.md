<!-- Spec: method-call-surfaces -->

## Purpose

Make all six convening methods callable in Claude and Codex while keeping
platform-specific files thin and registry-backed.

## ADDED Requirements

### Requirement: claude-method-commands

The Claude surface SHALL provide direct slash-command wrappers for all six
methods: `/jixia`, `/seven-sages`, `/areopagus`, `/junto`, `/parishad`, and
`/yushitai`. Each wrapper SHALL delegate to the shared registry and method
runner, not embed an independent roster.

#### Scenario: claude-wrapper-delegates

- **WHEN** `/junto` is invoked
- **THEN** the command loads the `junto` registry entry and does not contain a
  hand-maintained copy of the `junto` roster

### Requirement: codex-method-skills

The Codex surface SHALL provide project skills or skill aliases that make the
same six method names triggerable in Codex. Skill metadata MUST name the method
and route to the same registry-backed runner or instructions used by Claude. The
skill file format SHOULD follow the existing `.agents/skills/beads/SKILL.md`
exemplar (frontmatter + metadata shape) rather than inventing a new one.

#### Scenario: codex-method-name-triggers

- **WHEN** the user asks Codex to "run yushitai on this plan"
- **THEN** the `yushitai` method skill is discoverable by metadata and routes to
  the registry entry for `yushitai`

### Requirement: explicit-historical-flag

Both Claude and Codex surfaces SHALL support roster overrides of a method's
default policy. A `practical`-default method MUST accept explicit historical
activation (e.g. `with historical representatives`, `historical roster`, or an
explicit representative id); a `historical`-default method MUST accept a
`practical-only` override. Overrides change only the roster, never the method's
behavior contract. Every invocation stays method-scoped: it loads only the invoked
method's reps.

#### Scenario: explicit-historical-loads-only-method-reps

- **WHEN** the user invokes `seven-sages with historical representatives`
- **THEN** the call loads only `seven-sages` historical representatives and does
  not load Jixia, Junto, Parishad, Areopagus, or Yushitai representatives

#### Scenario: practical-default-stays-practical-without-flag

- **WHEN** the user invokes `/seven-sages <question>` with no historical flag
- **THEN** the call uses question-driven practical advisors and zero historical
  representatives

#### Scenario: historical-default-overridable-to-practical

- **WHEN** the user invokes `/areopagus <question> practical-only`
- **THEN** the call uses question-driven practical advisors and loads no historical
  representatives, while keeping the `areopagus` behavior contract

### Requirement: install-validation

Install or verification scripts SHALL fail if command wrappers, Codex skill
entries, registry methods, advisor files, or historical source notes are out of
sync. Advisor and rep-module resolution MUST check the **repo** paths
(`claude/agents/` and the in-repo rep module bodies), NOT the installed
`~/.claude/agents/` symlinks, so a fresh checkout / CI validates without an install
step. The validator SHALL be runnable without network access. As the drift guard
for the registry↔README↔wrappers sync surface, the validator SHALL also assert each
registry historical-rep entry cites a source present in
`docs/historical-council-sources/README.md` (provenance link), in addition to the
existing wrapper↔registry comparison.

#### Scenario: missing-wrapper-fails

- **WHEN** the registry contains `parishad` but no Claude or Codex callable
  surface exists for it
- **THEN** validation fails and names the missing surface

#### Scenario: resolves-against-repo-not-install

- **WHEN** validation runs on a fresh checkout with no `~/.claude/agents/` symlinks
  installed
- **THEN** it resolves advisors and rep modules against the repo paths and passes
  (install state is not required)

#### Scenario: registry-rep-without-readme-source-fails

- **WHEN** a registry historical-rep entry cites a source not present in the
  historical-council-sources README
- **THEN** validation fails (registry↔README provenance drift)

### Requirement: no-v1-trigger-coupling

Method call surfaces MUST NOT require the v1 Slack send-bounce or `/advise`
automatic routing skeleton to be installed or enabled.

#### Scenario: v2-call-without-v1-hooks

- **WHEN** no Slack MCP hooks are configured
- **THEN** `/areopagus` and the Codex `areopagus` skill remain callable
