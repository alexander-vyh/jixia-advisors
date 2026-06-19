<!-- Spec: method-registry -->

## Purpose

The shared source of truth for convening methods, practical advisor rosters,
historical representative rosters, source notes, load policy, behavior
contracts, and synthesis rules. Claude and Codex surfaces must read or be
generated from this registry rather than maintaining independent method
definitions.

## ADDED Requirements

### Requirement: all-six-methods

The registry SHALL define exactly the six README methods for skeleton scope:
`jixia`, `seven-sages`, `areopagus`, `junto`, `parishad`, and `yushitai`.
Each method SHALL include display name, invocation aliases, a default roster
policy (which pool — practical advisors or historical role/exemplar reps — staffs
it by default), a question-driven practical-advisor selection rule, an optional
historical representative roster, a lazy-load policy, synthesis rules, behavior
contract, and evidence fields. Method identity (the behavior contract) is
orthogonal to the roster: structure and who-staffs-it are independent axes.

#### Scenario: six-methods-present

- **WHEN** the registry validator runs
- **THEN** it finds all six required method ids exactly once and fails if any are
  missing, duplicated, or renamed

### Requirement: practical-rosters-resolve

Practical advisors are selected per question (triage by relevance), not via a
fixed per-method list. Any practical advisor a method can select — whether named
in a method allowlist or reachable through question-driven selection — MUST
resolve to an existing advisor file under `claude/agents/`. The registry MUST NOT
use historical representatives as substitutes for missing practical advisors.

#### Scenario: unresolved-practical-advisor-fails

- **WHEN** a method's selectable practical-advisor set references
  `nonexistent-advisor`
- **THEN** validation fails and names the method and unresolved advisor

### Requirement: default-roster-policy

Each method SHALL declare a default roster policy naming which pool staffs it by
default: `practical` (question-driven selection from `claude/agents/`) or
`historical` (the method's own source-backed role/exemplar reps). Skeleton
mapping: `jixia`, `seven-sages`, `junto` default `practical`; `areopagus`,
`parishad`, `yushitai` default `historical` (their role/exemplar reps are
purpose-built for the structure). Rosters are ALWAYS lazy: no representative or
advisor module loads at session start or into ambient/routine context — a
method's default roster loads only when that method is explicitly invoked. A
`historical`-default method MAY be invoked practical-only via an override; a
`practical`-default method MAY add its historical reps via the explicit historical
flag.

#### Scenario: institutional-method-defaults-historical

- **WHEN** `/areopagus <question>` is invoked with no roster override
- **THEN** the plan loads `areopagus` historical role/exemplar reps (lazily, only
  on this invocation) plus any question-relevant practical advisors, and loads no
  other method's reps

#### Scenario: everyday-method-defaults-practical

- **WHEN** `/jixia <question>` is invoked with no historical flag
- **THEN** the plan uses question-driven practical advisors and zero historical
  representatives

#### Scenario: nothing-loads-at-session-start

- **WHEN** a new session starts and no method is invoked
- **THEN** no practical or historical roster module is loaded into ambient context

### Requirement: historical-default-roster-functional

A method whose default roster policy is `historical` MUST resolve to authored
representative **module bodies** (the actual lens prompts), not merely source
metadata in the registry. The validator SHALL fail a `historical`-default method
whose default roster is empty or references representative ids that have no module
body — a method must not ship non-functional-by-default under a green skeleton.

#### Scenario: historical-default-without-module-body-fails

- **WHEN** `areopagus` (default `historical`) lists representative ids that have
  source notes but no authored module body
- **THEN** validation fails and names the method and the bodiless representative

### Requirement: source-backed-representatives

Every historical representative entry MUST include a stable id, representative
type (`person`, `role`, or `exemplar`), method id, source title, source URL,
source note, and confidence label. Institutional methods MAY use role or
exemplar representatives when the source does not provide a stable named roster.

#### Scenario: source-missing-fails

- **WHEN** a historical representative lacks a source URL or source note
- **THEN** validation fails and names the representative id

#### Scenario: institutional-role-allowed

- **WHEN** `yushitai` defines `remonstrance-censor` as a role representative
- **THEN** validation accepts it if the representative has source metadata and
  does not claim to be a named historical person

### Requirement: method-behaviors-differ

Each method SHALL declare a behavior contract with three mechanically-checkable,
method-characteristic parts:

1. a **required-output-field set** — the named fields the method's synthesis MUST
   contain, including at least one **method-verb field** naming the method's
   characteristic act (areopagus → `verdict`/`remedy_or_remand`; yushitai →
   `corrective_action`; junto → `experiment_or_commitment`). Example sets:
   `areopagus` `{verdict, admissible_concerns, remedy_or_remand}`; `yushitai`
   `{findings[severity, owner, corrective_action], evidence_path}`; `junto`
   `{queries, experiment_or_commitment, followup_check}`. The registry is the SOLE
   canonical authority for these field-sets, phases, and refusal conditions; the
   README's Method Behavior Contracts table is a human-readable summary derived
   from the registry, NOT a second source of truth — there is no "keep consistent
   with the README" coupling to rot.
2. a distinct **entry gate** and a distinct **refusal/redirect condition** — each
   non-empty AND pairwise-distinct across methods (one boilerplate refusal reused
   for all six fails).
3. a **phase sequence** in which every required output field is produced by at
   least one phase.

The **core invariant** is pairwise distinctness across THREE axes at once — the
required-output-field set (including its method-verb field), the entry gate, and
the refusal condition. The validator SHALL fail when: any two methods share an
identical required-output-field set; any method lacks a method-verb field, or two
methods' verb-fields collide; any two methods share an identical (or empty) entry
gate or refusal condition; any method's required output fields are not all covered
by its phases; or all six methods share one behavior contract. A registry that
differs only by method name, advisor background, historical roster, OR by phase
*names* while keeping the same field-set/gate/refusal MUST fail — renaming phases
is not differentiation.

Honest limit (do not overclaim): this static check defeats *lazy* generic wrappers,
not a determined adversary who renames fields isomorphically. Pure-static checking
cannot prove *semantic* distinctness — that requires the live-output check in
task 3.1 (`method-evidence` → `fixture-suite`), which exercises real model output
per method. The static validator is the cheap craft gate; the live fixtures are
where semantic genericness is actually caught.

#### Scenario: generic-wrapper-rejected

- **WHEN** all six methods point to a single identical `generic_council`
  behavior contract
- **THEN** validation fails because the method layer is only a renamed wrapper

#### Scenario: background-only-variation-rejected

- **WHEN** `jixia`, `seven-sages`, `areopagus`, `junto`, `parishad`, and
  `yushitai` use different advisor rosters but share the same required-output-field
  set
- **THEN** validation fails because the methods differ only by advisor background
  rather than behavior

#### Scenario: phase-rename-does-not-count-as-differentiation

- **WHEN** two methods declare different phase NAMES but identical
  required-output-field sets
- **THEN** validation fails — cosmetic phase renaming is not a behavior difference

#### Scenario: fields-not-covered-by-phases-fails

- **WHEN** a method declares a required output field that no phase produces
- **THEN** validation fails and names the method and the uncovered field
