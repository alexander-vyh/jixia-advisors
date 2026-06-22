## ADDED Requirements

### Requirement: dissent-seated-by-default

Every convening structure run through the router SHALL seat a dissent role (the "devil's
advocate") by default. A run without a seated dissenter is a defect.

#### Scenario: default run includes a dissenter

- **WHEN** any convening model is run via `/advise` or `/advise-full` with no roster
  customization
- **THEN** the convened roster includes exactly one seat designated as the dissenter

### Requirement: dissent-is-non-removable

The user MAY swap WHO holds the dissent seat but MUST NOT be able to remove the seat
itself. A customization that attempts to drop the dissenter SHALL still produce a run with
a dissenter (the seat is re-filled, not eliminated).

#### Scenario: swap the dissenter

- **WHEN** the user reassigns the dissent seat to a different advisor
- **THEN** the run proceeds with that advisor as the dissenter

#### Scenario: removal attempt is refused

- **WHEN** the user attempts to remove the dissent seat entirely
- **THEN** the run still seats a dissenter (default reinstated), and the system states the
  dissent role is mandatory

### Requirement: dissent-prompt-is-low-sycophancy

The dissent seat's instructions SHALL direct it to argue the strongest counter-case, to
resist agreeing for the sake of consensus, and to not soften its position in later
exchanges. The dissenter MUST NOT be a generic agreeable lens.

#### Scenario: dissenter prompt mandates opposition

- **WHEN** the dissent seat is instantiated for a run
- **THEN** its prompt contains directives to counter-argue, withhold easy agreement, and
  not soften across rounds

### Requirement: dissenter-named-on-entry

The system SHALL name the dissenter (by role or advisor name) to the user on the first turn
of a run, presented as a feature of the deliberation, so the dissent is recognized as
structural rather than noise.

#### Scenario: dissenter surfaced up front

- **WHEN** a run begins (auto or via the menu)
- **THEN** the first turn states who holds the counter-lens / dissent seat

### Requirement: dissent-resolves-to-a-real-occupant

For a historical-roster method, the dissent seat SHALL resolve to that method's native
dissent instance (e.g. areopagus Ephialtean power-limiter; yushitai remonstrance/impeachment
censor); for a practical-roster method, it resolves to the counter-lens. Whichever it is,
the dissent occupant MUST resolve to a real deployed agent file or a real source-backed
representative — never a placeholder.

#### Scenario: historical method uses its native dissenter

- **WHEN** `yushitai` is convened with its default historical roster
- **THEN** the dissent seat resolves to a real source-backed remonstrance/impeachment
  representative defined for `yushitai`

#### Scenario: practical method uses a real counter-lens

- **WHEN** an everyday practical-roster model is convened
- **THEN** the dissent seat resolves to a real advisor file under `claude/agents/`
