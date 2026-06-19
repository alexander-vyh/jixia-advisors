<!-- Spec: historical-representatives -->

## Purpose

Provide optional source-backed historical representative lenses for each
convening method without turning the default advisor experience into historical
roleplay or increasing ambient context load.

## ADDED Requirements

### Requirement: lazy-loading

Historical representative modules SHALL be loaded lazily — only when a method that
includes them (by default roster policy or by explicit historical override) is
invoked. They MUST NOT be loaded into ambient/session-start context, nor installed
as always-on instructions, default Claude agents, or default Codex skills. (A
method whose default roster policy is `historical` still loads its reps only on
invocation, never at session start.)

#### Scenario: no-default-context-load

- **WHEN** a new Claude or Codex session starts
- **THEN** historical representative module bodies are not loaded into context by
  default

### Requirement: representative-grounding

Each representative module SHALL include a source note, the stance it contributes
to the method, and a limitation note. The module MUST NOT claim to speak as the
actual historical person or institution.

#### Scenario: limitation-note-required

- **WHEN** the `franklin-query-convener` representative is loaded
- **THEN** its prompt includes a limitation note explaining that it is a
  source-grounded lens, not an impersonation of Benjamin Franklin

### Requirement: named-vs-role-distinction

Representatives SHALL be typed as `person`, `role`, or `exemplar`. Methods with
unstable or institutional histories MUST use role/exemplar entries unless a
source supports a named person for the intended stance.

#### Scenario: areopagus-fake-member-rejected

- **WHEN** `areopagus` defines a made-up named council member as a `person`
- **THEN** validation fails unless a source note supports that named person as a
  representative for the method

### Requirement: method-scoped-loading

Explicit historical activation SHALL load representatives only for the invoked
method, unless the user explicitly names a cross-method representative.

#### Scenario: method-scope-preserved

- **WHEN** `parishad historical roster` is invoked
- **THEN** only Parishad representatives are eligible for loading

### Requirement: useful-counsel-over-antiquarian-detail

Representative modules SHALL translate source-backed historical context into a
review stance useful for the current work. They SHOULD avoid long background
summaries unless the user asks for historical explanation.

#### Scenario: representative-produces-actionable-stance

- **WHEN** a `yushitai` detection-censor representative reviews an implementation
  plan
- **THEN** its output focuses on accountability, inspection paths, and failure
  modes rather than a general history of the Censorate
