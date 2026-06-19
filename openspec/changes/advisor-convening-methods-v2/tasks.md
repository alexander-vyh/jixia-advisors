# Tasks — advisor-convening-methods-v2

Walking skeleton: all six convening methods become callable in Claude and
Codex, historical representatives are source-backed and lazy, and verification
rejects generic wrappers/ambient historical loading.

## 1. Registry, rosters, and validator

- [ ] 1.1 Produce the Test Oracle Brief for this change, including invalid
      solution classes and mutation cases: missing method, unresolved practical
      advisor, historical representative without source metadata, historical
      representatives loaded into ambient/session-start context, a historical-default
      method with no authored rep module body, and a single generic wrapper reused
      for all six methods. Then create the shared method registry for `jixia`,
      `seven-sages`, `areopagus`, `junto`, `parishad`, and `yushitai` with
      per-method default roster policy, question-driven practical selection, lazy
      historical rosters, source notes, confidence labels, behavior contracts
      (field-set + entry gate + refusal, pairwise-distinct), and synthesis shapes.
      Add a registry validator and tests. Specs: `method-registry` requirements
      `all-six-methods`, `practical-rosters-resolve`, `default-roster-policy`,
      `source-backed-representatives`, `historical-default-roster-functional`,
      `method-behaviors-differ`; `historical-representatives` requirements
      `named-vs-role-distinction`, `representative-grounding`. Done when the
      validator passes for the real registry and fails the named mutations.

- [ ] 1.2 Author the historical representative MODULE BODIES (the actual lens
      prompts, not just registry metadata) for the three institutional methods that
      default `historical` — `areopagus`, `parishad`, `yushitai` — each grounded in
      its source packet in `docs/historical-council-sources/README.md`, typed
      person/role/exemplar with a limitation note, translating source into a review
      stance (not antiquarian summary). Specs: `historical-representatives`
      requirements `representative-grounding`, `named-vs-role-distinction`,
      `useful-counsel-over-antiquarian-detail`; `method-registry`
      `historical-default-roster-functional`. Done when each of the three methods
      has a non-empty, functional default roster — invoking it produces method-shaped
      output from real rep modules, not an empty or metadata-only roster. (This is
      the scope cost of keeping all six per design Decisions; it is NOT registry
      metadata.)

## 2. Callable Claude and Codex surfaces

- [ ] 2.1 Add direct Claude command wrappers and Codex method skills/aliases for
      all six methods, backed by the shared registry rather than copied rosters.
      Extend install/verification so missing wrappers, missing skills, unresolved
      advisors, or missing historical source notes fail locally without network
      access. Specs: `method-call-surfaces` requirements
      `claude-method-commands`, `codex-method-skills`,
      `explicit-historical-flag`, `install-validation`, `no-v1-trigger-coupling`.
      Done when each method's default invocation loads its declared default roster
      (practical for everyday methods, historical role-reps for institutional
      methods), roster overrides change only the roster not the behavior contract,
      invocations stay method-scoped, and the calls work without v1 Slack hooks.

## 3. Invocation log, fixtures, and outcome verification

- [ ] 3.1 Add the lightweight invocation log plus smoke fixtures for at least `junto`,
      `areopagus`, and `yushitai`, with expected method-specific behavior and
      output features that a generic wrapper cannot satisfy. Add mutation checks
      for the bad implementations named in the Test Oracle Brief, then run the actual
      Claude/Codex method-call verification path against all six methods. Specs:
      `method-evidence` requirements `invocation-log`, `fixture-suite`,
      `mutation-checks`, `no-keepkill-oracle`; `historical-
      representatives` requirements `lazy-loading`, `method-scoped-loading`,
      `useful-counsel-over-antiquarian-detail`. Done when all six methods are
      callable, default calls record the method's default roster (zero historical
      reps for everyday methods; method-scoped reps for institutional methods),
      roster overrides record the overridden roster, and fixture/mutation checks
      reject generic wrappers and ambient/session-start-loaded reps.

Done when proof of delivery is observed: all six methods are callable in Claude
and Codex, no roster loads at session start, each method's default invocation
loads its declared roster (everyday → practical, institutional → method-scoped
historical reps) with overrides changing only the roster, the registry validator
proves the six method contracts are pairwise-distinct, the live-output fixtures
prove each method produces output satisfying its distinct contract
(required-output-field set + refusal gate), and every method — including the three
historical-default ones — produces a usable result (non-empty default roster). The
invocation log is curiosity only; there is no reuse/keep-kill gate.
