## ADDED Requirements

### Requirement: classifier-resolves-to-a-real-model

The routing classifier SHALL map a draft/decision plus its signals (audience, channel,
stakes, artifact shape) to a tuple `(convening model, roster, confidence, dissent seat)`.
The selected `convening model` MUST be one of the six methods defined in the
`advisor-convening-methods-v2` registry (`jixia`, `seven-sages`, `areopagus`, `junto`,
`parishad`, `yushitai`); the `roster` MUST resolve to that model's registry roster policy
or an explicit override; and the classifier MUST NOT invent a model or lens not present in
the registry.

#### Scenario: draft resolves to a registry model

- **WHEN** the classifier is given a draft with a clear convening signal (e.g. an
  accountability/audit artifact)
- **THEN** it returns one of the six registry model ids (e.g. `yushitai`) with a roster
  that resolves to a real roster policy, and a confidence value

#### Scenario: classifier never returns an unknown model

- **WHEN** the classifier processes any input
- **THEN** the returned model id is always one of the six registry ids, never a fabricated
  or non-registry name

### Requirement: advise-auto-runs-the-pick

`/advise` SHALL run the classifier's selected `(convening model, roster)` automatically,
without requiring the user to choose from a menu. It MAY state its selection in one line,
but MUST NOT block on a selection step for a confident match.

#### Scenario: confident match runs automatically

- **WHEN** the user invokes `/advise <draft>` and the classifier returns a confident match
- **THEN** the selected convening model is run on the verbatim draft with no menu, and its
  pick is recorded

### Requirement: advise-full-presents-a-pick-preselected-menu

`/advise-full` SHALL present the classifier's pick as a PRE-SELECTED default in a menu the
user can accept in one reply, and SHALL allow overriding the model, the roster, and
optionally specific agents. The menu SHALL present the model choice first with the roster
collapsed to the model's registry default and specific-agent selection hidden until
explicitly expanded; it SHALL NOT present the full model×roster×agent grid at once.

#### Scenario: accept the default in one reply

- **WHEN** the user invokes `/advise-full <draft>` and replies with acceptance (e.g. Enter)
- **THEN** the classifier's pre-selected model+roster is run, with no further prompting

#### Scenario: override the model

- **WHEN** the user names a different model (e.g. "use areopagus")
- **THEN** the selected model switches to that model and is run, and the override is
  recorded

### Requirement: no-confident-match-offers-never-guesses

The system SHALL offer the `/advise-full` menu (or the model/advisor list) when the
classifier's confidence is below the no-confident-match threshold, and SHALL NOT dispatch a
guessed model. Guessing a model on a low-confidence input is a defect.

#### Scenario: ambiguous draft is not force-routed

- **WHEN** `/advise` receives a draft with no confident convening signal
- **THEN** the system states no confident match and offers the menu, and dispatches no
  model until the user chooses

### Requirement: routing-decisions-are-logged

The system SHALL append a record of the auto-pick to `~/.claude/jixia/counsel-log.jsonl` on
every `/advise` / `/advise-full` invocation, and SHALL record when the user overrides the
pre-selected pick in `/advise-full`. The accept-vs-override rate computed from these records
is the routing-quality signal.

#### Scenario: auto-pick recorded

- **WHEN** `/advise` runs an auto-selected model
- **THEN** a record containing the selected model and roster is appended to the counsel log

#### Scenario: override recorded as a distinct signal

- **WHEN** the user overrides the pre-selected model in `/advise-full`
- **THEN** a record distinguishes the originally-recommended model from the
  user-selected one, so accept-vs-override is computable

### Requirement: round-count-and-synthesis-not-exposed

The system SHALL NOT expose round count or synthesis method as user-selectable knobs in
either entry point. Multi-round interaction SHALL be capped (2-3 exchanges) internally.

#### Scenario: no rounds knob in the menu

- **WHEN** the user views the `/advise-full` menu
- **THEN** no option to set debate rounds or synthesis method is presented
