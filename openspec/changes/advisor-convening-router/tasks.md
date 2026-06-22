<!-- Walking skeleton = groups 1–2 (the routing classifier + its labeled oracle): the
minimum system that tests the riskiest assumption (does auto-routing pick a model the
user accepts). Groups 3–6 build out from there. -->

## 1. Test oracle & routing fixtures (foundation — author before any impl)

- [ ] 1.1 Author `test-oracle-brief.md`: business invariant (right model for the draft; unmatched → no-confident-match, never a guessed model), the mandated-dissent invariant, the named fragile implementations to reject ("always returns the everyday default", "keyword-anywhere → match"), negative controls, and the final outcome check (accept-vs-override is computable)
- [ ] 1.2 Pin the initial routing table: which draft-types/signals map to which of the six models, plus the confidence threshold for no-confident-match (record rationale in the brief)
- [ ] 1.3 Build the labeled routing fixture corpus: positive cases per mapped draft-type → expected model, and negative controls (ambiguous / out-of-scope → no-confident-match)

## 2. Routing classifier (walking skeleton — riskiest assumption)

- [ ] 2.1 Write failing classifier tests from the fixtures: positive per type, negative controls, and an assertion that the returned model is ALWAYS a real registry id (never invented)
- [ ] 2.2 Implement the classifier: signals (audience/channel/stakes/artifact-shape) → `(model, roster, confidence, dissent seat)`; deterministic core; fail CLOSED to no-confident-match below threshold
- [ ] 2.3 Resolve the selected model + roster against the `advisor-convening-methods-v2` registry; never emit a non-registry model
- [ ] 2.4 Make the failing tests pass; challenge against the named fragile implementations (the "always default" / "keyword-anywhere" impls must fail at least one test)

## 3. Mandated-dissent invariant

- [ ] 3.1 Write failing tests: every default run seats exactly one dissenter; a removal attempt re-seats the default; the dissenter resolves to a real agent file or source-backed rep
- [ ] 3.2 Implement dissent seating with a low-sycophancy prompt (argue strongest counter-case, resist agreeing, do not soften in later rounds)
- [ ] 3.3 Map each historical method to its native dissent instance (areopagus Ephialtean power-limiter; yushitai remonstrance/impeachment censor) and practical methods to the counter-lens; make the tests pass

## 4. `/advise` auto entry point

- [ ] 4.1 Wire `/advise` to call the classifier and run the selected model on the verbatim draft, with a fail-safe fallback to the current fixed-pair behavior if the classifier is absent/errors
- [ ] 4.2 Name the dissenter on the first turn; append the auto-pick record (model + roster + dissenter) to `~/.claude/jixia/counsel-log.jsonl`

## 5. `/advise-full` menu entry point

- [ ] 5.1 Author the `/advise-full` skill surface per `design-inputs/` (model-first; roster collapsed to registry default; agents hidden in a third layer; classifier pick short-circuits to a one-line confirm; dissenter named; NO rounds/synthesis knob; light→heavy model order; output-shape glosses)
- [ ] 5.2 Implement accept-in-one-reply and override of model / roster / specific agents (orthogonality reachable, grid never shown)
- [ ] 5.3 Record overrides distinctly from accepts so the accept-vs-override (routing-quality) rate is computable from the counsel log

## 6. Install, verify, and report

- [ ] 6.1 Extend `INSTALL.sh` to symlink the new classifier + `/advise-full` skill (idempotent; uninstall path)
- [ ] 6.2 Run the full test suite; confirm routing fixtures (positive + negative controls) and the mandated-dissent invariant all pass
- [ ] 6.3 Outcome check: exercise `/advise` (auto) and `/advise-full` (menu + an override) end-to-end; confirm an auto-pick record and a distinct override record land in the counsel log
