# Test Oracle Brief — advisor-convening-methods-v2 registry validator

**Form:** rapid 3-section (craft tool; per the 2026-06-18 scoping decision on
bead `jixia-advisors-9aw.1`) — *with* the mandatory named-fragile-implementation
challenge retained.

**Scope of what this brief constrains:** the ONLY piece of behavioral logic in
this change — the registry **distinctness validator** (built in `9aw.2`/T1b). The
advisors, method prompts, rep modules, and the counsel they produce are
prose/config judged by use; they get no oracle. This brief is authored *before*
the registry exists so the validator has a fixed target it cannot be bent to match.

**Pressure-test result (2026-06-19, with the owner):** all six methods are
genuinely pairwise-distinct — **no overlap exceptions**. The two *adjacent* pairs
(`jixia`↔`seven-sages`, `areopagus`↔`yushitai`) are the ones distinctness most
protects; the README itself warns "do not collapse Areopagus and Yushitai." So
strict pairwise-distinctness is the correct invariant.

---

## 1. Business invariant

The six convening methods are genuinely-distinct deliberation **structures**, not
one generic wrapper wearing six labels.

Operationalized mechanically, a method's contract is the triple:
`(required-output-field set incl. a method-verb field) ∪ (entry gate) ∪ (refusal/redirect)`.
The invariant: these contracts are **pairwise-distinct across all six**.

**Independent source of truth** (defines "distinct" independent of the validator's
code): the per-method behavior contracts in
`docs/historical-council-sources/README.md` (entry-gate / output-shape / refusal
columns). The registry is canonical for the field-sets; the README is the
human-readable provenance. Reference field-sets (method-verb field in **bold**):

| Method | Output-field set |
|---|---|
| jixia | diagnosis, selected_lenses, dissent, **next_action** |
| seven-sages | perspectives(≤7), **convergence_divergence_map**, **distilled_counsel** |
| areopagus | case_record, admissible_concerns, **verdict**, **remedy_or_remand** |
| junto | queries, observations, **experiment_or_commitment**, **followup_check** |
| parishad | authority_map, role_obligations, conflict_interpretation, **settlement** |
| yushitai | findings, evidence_path, owner, severity, **corrective_action** |

**Layering (the load-bearing honesty):** structure is the **floor** — a cheap
authoring gate that catches blur. It is *necessary but not sufficient*: a schema
is a promise, and only live output shows the promise was kept. The **binding**
distinctness oracle is the live-output fixtures (T4/`9aw.5`), which MUST include an
**adjacent pair** (`areopagus` vs `yushitai` on one shared prompt) — the hardest
case, not an obvious pair.

## 2. Negative controls (both retained, per the owner's GRILL-3 decision)

**NC-1 — copy-paste drift (realistic; STATIC validator MUST fail it).** A method
added/edited by copying an existing one and changing only the roster, leaving its
output-field set / entry-gate / refusal identical to the source. The static
validator catches this directly (literal contract collision). This is the failure
the solo repo will actually hit months from now.

**NC-2 — isomorphic rename (adversarial, blocker B1; the LIVE fixture MUST fail
it, the static validator CANNOT).** Two methods whose field-sets are different
*strings* but the same *template* — e.g. `areopagus` `{verdict,
admissible_concerns, remedy_or_remand}` vs a wrapper `{ruling, valid_concerns,
action_or_defer}`. A pairwise string-set comparison PASSES this (the strings
differ), so the static validator cannot catch it — this is the documented
honest-limit. The live-output fixture catches it: the renamed wrapper produces
counsel indistinguishable in *kind* from its twin and fails the adjacent-pair
distinctness check.

### Named-fragile-implementation challenge (mandatory — and it PASSES correctly)

Q: would a validator that only checks pairwise-distinct field-set *strings* pass a
known-bad implementation? **A: yes — it passes NC-2 (isomorphic rename).**
Therefore the static check ALONE is insufficient, and this brief REQUIRES the live
adjacent-pair fixture as the catching layer. (This is the rapid form retaining the
challenge: dropping it would let a generic wrapper ship green.)

## 3. Final outcome verification

The registry validator (T1b), run against the **real** registry, exits 0; run
against each mutation below, exits non-zero **naming the offending method**.
Fail-closed: any method missing a contract element fails validation.

**Mutation spec (static validator MUST fail each):**
- M1 — method count ≠ 6 (missing / duplicated / renamed id)
- M2 — unresolved practical advisor (not present in `claude/agents/`, resolved
  against the **repo** path, not `~/.claude/agents/`)
- M3 — historical representative with no source metadata
- M4 — historical reps loaded ambiently / cross-method (lazy + method-scoped
  violation)
- M5 — generic wrapper: all six share one behavior contract
- M6 — `historical`-default method with no authored rep module body
- M7 (= NC-1) — copy-paste drift: two methods with an identical contract
- M8 — a method missing its method-verb field, or two verb-fields colliding

**Live-output check (T4, the binding distinctness oracle; catches NC-2):** on one
shared real prompt, an adjacent pair (`areopagus` vs `yushitai`) each produces
output satisfying its own contract AND differing in kind; a generic or
isomorphically-renamed wrapper fails this.

---

**Open for owner correction:** the reference field-sets in §1 are derived from the
README behavior-contract table; if any method's *defining output* is wrong (e.g.
jixia's verb should be something other than `next_action`), correct it here before
T1b encodes it — the validator inherits whatever this brief fixes.
