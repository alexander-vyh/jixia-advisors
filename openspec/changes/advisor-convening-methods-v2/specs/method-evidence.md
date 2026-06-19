<!-- Spec: method-evidence -->

## Purpose

Verify that method calls are *distinct* (via `fixture-suite` and `mutation-checks`
— the craft quality bar that keeps each method from collapsing into a generic
wrapper) and that historical representatives load correctly, plus keep a
**lightweight invocation log** for the user's own curiosity (which methods get
reached for). The log is NOT a keep/kill oracle: the methods are kept regardless
(they have intrinsic value), so this change deliberately carries no
reuse-threshold, no superiority comparison, and no demote branch. See design.md
Non-Goals.

## ADDED Requirements

### Requirement: invocation-log

Each method invocation SHOULD append a lightweight local log record containing
method id, platform (`claude` or `codex`), roster used (practical advisors and/or
historical reps loaded), and timestamp. This is a curiosity log — "which methods
do I reach for" — not an oracle: it MUST NOT require self-reported usefulness, and
nothing in this change gates a keep/kill decision on it.

#### Scenario: invocation-logged

- **WHEN** `/jixia` runs (practical-default, no historical override)
- **THEN** the log record shows the practical roster used and an empty historical
  list, with no usefulness field

### Requirement: fixture-suite

The skeleton SHALL include fixtures for at least three structurally different
methods. Fixtures MUST assert that a produced output satisfies that method's
**required-output-field set** from the registry `method-behaviors-differ`
contract (and its refusal gate where the fixture exercises one), so a generic
wrapper or background-only roster swap cannot pass. (Layer boundary: the registry
validator proves the contracts are pairwise-distinct offline; fixtures prove a
produced output satisfies its method's contract.)

#### Scenario: generic-output-fails-fixture

- **WHEN** the same generic council response is returned for `junto`,
  `areopagus`, and `yushitai`
- **THEN** fixture validation fails because each method's required-output-field
  set (and refusal gate) from the registry contract is not satisfied

### Requirement: mutation-checks

Verification SHALL include mutation checks for known bad implementations:
missing method, unresolved practical advisor, historical representative with no
source note, historical representatives loaded into ambient/session-start context
or across methods (rather than lazily and method-scoped on invocation), and a
single generic wrapper used for all six methods.

#### Scenario: ambient-load-mutation-fails

- **WHEN** an implementation preloads historical representatives into session-start
  context, or loads every method's representatives on any single method call
- **THEN** the mutation check fails even if the user-facing output looks
  complete

### Requirement: no-keepkill-oracle

This change SHALL NOT implement a reuse threshold, a superiority/ad-hoc
comparison, a `comparison_id`/paired-A-B mechanism, or a demote-to-docs branch.
The methods are kept regardless of measured use; the invocation log is curiosity
only. (Recorded explicitly so a later contributor does not "restore" a keep/kill
oracle the owner deliberately declined.)

#### Scenario: no-superiority-machinery

- **WHEN** the change is implemented and validated
- **THEN** no reuse-rate gate, comparison arm, or demote branch exists; the only
  evidence artifact is the lightweight invocation log
