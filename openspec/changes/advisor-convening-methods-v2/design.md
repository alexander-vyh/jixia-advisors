# Design — advisor-convening-methods-v2

## Problem Statement

The six historical convening models in the README become usable methods rather
than decorative names. After this change, a Claude or Codex session can invoke
`jixia`, `seven-sages`, `areopagus`, `junto`, `parishad`, or `yushitai`,
receive method-shaped counsel from concrete advisor rosters, and optionally call
source-backed historical representatives for that method without loading those
representatives by default.

## Non-Goals

1. **No ambient historical cosplay.** Historical representatives never load into
   session-start/ambient context or into routine (jixia) advice — they are always
   lazy, loading only when a method that convenes them is explicitly invoked. This
   locks in a low-context default path and keeps irrelevant historical voices out
   of routine advice. (Refined 2026-06-16: roster staffing is per-method — the
   institutional methods areopagus/parishad/yushitai default to their purpose-built
   historical role-reps *on invocation*; that is not ambient loading and not
   cosplay-by-default. See Decisions → roster model.)
2. **No claim of historical authenticity.** The representative modules are
   source-grounded lenses, not claims to reproduce the actual people or
   institutions. This locks in explicit source notes, confidence labels, and a
   refusal to invent stable rosters where the historical story does not provide
   one.
3. **No replacement for v1 advisor-routing.** This change does not implement or
   alter the unfinished `/advise`, Slack send-bounce, or counsel-report skeleton.
   This locks in v2 as a manual callable method layer that can later feed v1, but
   does not depend on automatic Slack triggers.
4. **No always-on council rule.** No global instruction tells every session to
   consider every method. This locks in explicit invocation as the activation
   mechanism.
5. **No runtime web research requirement.** Historical source selection happens
   at build/design time and is recorded in local registry/reference files. This
   locks in deterministic runtime behavior when offline.
6. **No keep/kill gate.** The methods are kept regardless of measured use — they
   have intrinsic/craft value to the owner. This change implements no reuse
   threshold, superiority comparison, or demote-to-docs branch — only a lightweight
   curiosity log. Locks out re-introducing measurement-as-gate that the owner
   deliberately declined; distinctness is enforced as a craft quality bar, not as a
   falsification oracle.

## Capabilities

### New Capabilities

- `method-registry` — a shared registry describing all six methods, invocation
  names, per-method default roster policy (practical vs historical), the
  question-driven practical-advisor selection rule, optional historical rosters,
  lazy-load policy, behavior contract, synthesis shape, and evidence fields.
  Method identity (behavior contract) and roster (who staffs it) are orthogonal
  axes.
- `method-call-surfaces` — Claude and Codex invocation surfaces generated or
  checked against the shared registry, so the six methods are callable in both
  environments without hand-maintained drift.
- `historical-representatives` — lazy, source-backed representative modules for
  each method, loaded only on invocation of a method that convenes them. Named-
  person methods may use named figures; institutional methods use sourced roles or
  exemplar figures (and default to them) rather than fabricated member lists.
- `method-evidence` — a lightweight invocation log (curiosity, not a keep/kill
  oracle) plus smoke fixtures and mutation checks that prove method calls are
  distinct and reject generic wrappers / ambient historical loading.

### Modified Capabilities

- `advise-skill` remains conceptually adjacent but unchanged. A future increment
  can make `/advise` delegate to `method-registry`; this skeleton does not.

## Impact

- New registry/reference files, likely under `jixia/` or `data/jixia/`, become
  the source of truth for methods and representatives.
- Claude surface: slash commands such as `/jixia`, `/seven-sages`,
  `/areopagus`, `/junto`, `/parishad`, `/yushitai`, plus install wiring to place
  them under `~/.claude/commands/`.
- Codex surface: project skills under `.agents/skills/` with method names in
  metadata so a user can invoke the same six method names in Codex.
- Existing `claude/agents/*.md` stay as the practical advisor pool. Historical
  representatives live as lazy references or method-scoped modules, not global
  `claude/agents` entries unless explicitly installed later.
- `INSTALL.sh` must validate that every default advisor name resolves to a real
  deployed advisor file and that every historical representative has a local
  source note.

## Historical Representative Source Audit

The skeleton ships all six methods, but it must encode the source shape honestly:

| Method | Representative shape | Initial roster direction |
| --- | --- | --- |
| `jixia` | Named scholars associated with Jixia Academy | Mencius, Xunzi, Zou Yan, Shen Dao, Yin Wen, Song Xing, Chunyu Kun; optionally Tian Pian and Peng Meng as additional Daoist/Huang-Lao seats. |
| `seven-sages` | Named sages with canonical-list variance | Thales, Pittacus, Bias, Solon, Chilon, Cleobulus, Myson as the default Plato-style roster; Periander, Anacharsis, Pythagoras, and others recorded as variants. |
| `areopagus` | Institution plus exemplar figures/roles, not a stable named membership list | Former-archon councillor, Areopagite homicide juror, Solonian law-guardian, Ephialtean power-limiter, Aeschylean trial reader; optionally Draconian homicide-law keeper. |
| `junto` | Franklin's mutual-improvement circle and roles | Benjamin Franklin, Joseph Breintnall, Thomas Godfrey, Nicholas Scull / William Parsons surveyor seat, William Coleman, Robert Grace, John Jones Jr. |
| `parishad` | Council roles more than stable named individuals | Dharmadhikarin chief judge, Vedic scholar, Vedanga scholar, Dharmashastra scholar, student, householder, ascetic, law-school representative. |
| `yushitai` | Censorate office roles | Censor-in-chief, investigating censor, palace-audience censor, admonishment censor, detection/monitor censor. |

Source notes used for this discovery:

- Jixia Academy sources name the academy and list associated scholars including
  Tian Pian, Shen Dao, Peng Meng, Zou Yan, Yin Wen, Song Xing, Mencius, Xunzi,
  and Chunyu Kun.
- The Seven Sages tradition has multiple lists; Livius notes four highly stable
  names and many candidates for the remaining seats, so the registry must carry
  both a default list and variant metadata.
- Areopagus sources describe a council/court, former-archon membership,
  contested Solonian law-guardian traditions, later democratic limitation, and
  Aeschylus' dramatic trial story; that supports role/exemplar modules with
  explicit caveats, not a fake fixed roster.
- Franklin/Junto sources support both the method shape (queries, mutual
  improvement, debate without victory-seeking) and several named members.
- Parishad sources describe a learned council, chief judge, and membership
  composition by expertise/social role; that supports role modules.
- Yushitai/Censorate sources describe supervisory branches and censor roles;
  that supports office-role modules.

## Method Behavior Contracts

The methods must differ in behavior, not only in advisor background. The shared
registry needs to encode at least an entry gate, phase sequence, output contract,
and refusal/redirect condition for each method.

| Method | Entry gate | Required phases | Output contract | Refusal / redirect |
| --- | --- | --- | --- | --- |
| `jixia` | Everyday counsel or right-sized lens selection. | Triage prompt, select smallest useful advisor mix, add counter-lens only when useful, synthesize next action. | Diagnosis, selected lenses, dissent/tension, recommended next action. | Redirect formal adjudication, audit, stakeholder settlement, or habit cadence to a sharper method. |
| `seven-sages` | Ambiguous planning question needing bounded breadth. | Select up to seven voices, collect compact principles/warnings, compare tensions, distill counsel. | Up to seven terse views, convergence/divergence map, distilled counsel. | Redirect evidence trial, source-law interpretation, operational inspection, or coaching cadence. |
| `areopagus` | Consequential decision needing review before action. | Gate jurisdiction, frame case, classify evidence/harm, test mandate/precedent/legitimacy, judge remedy. | Case record, admissible concerns, verdict, remedy or remand. | Refuse routine brainstorming or advice with no consequential decision. |
| `junto` | Self-improvement, operating cadence, or practical improvement. | Convert to prepared queries, keep truth-seeking discipline, produce experiments/commitments, schedule follow-up. | Query list, observations, experiment or habit commitment, follow-up check. | Redirect formal ruling, audit, or stakeholder balancing. |
| `parishad` | Tradeoff across roles, duties, sources of authority, or stakeholders. | Identify authorities, map affected roles, interpret conflicts, weigh custom/context, settle least-violating path. | Authority map, role obligations, conflict interpretation, caveated settlement. | Redirect tactical advice or audit without a real role/source conflict. |
| `yushitai` | Accountability, audit, remonstrance, or failure-mode detection. | Trace inspection path, collect evidence, identify misconduct/control gap, test capture risk, recommend escalation/correction. | Findings, evidence path, owner, severity, corrective action. | Redirect open-ended ideation or balanced synthesis. |

A registry that only changes historical representatives or practical advisor
backgrounds while preserving one common phase list and output template is still
a generic wrapper and must fail validation.

## Riskiest Assumption

These methods are kept regardless of measured payoff — they have intrinsic/craft
value to the owner (see Non-Goals → no keep/kill gate) — so the risk is NOT "are
they worth keeping." The riskiest assumption is a **craft-feasibility** one: that
the six methods can be made *genuinely distinct and usable* rather than six labels
over one generic wrapper, and that the three institutional methods which default to
historical reps can have those rep modules authored into lenses that actually
produce method-shaped output. We will know this is true when the distinctness
validator + live-output fixtures show each method behaving differently AND every
method (including the historical-default three) produces a usable result on a real
prompt. If false, the failure is a generic-wrapper method or a non-functional
historical-default method shipping under a green skeleton.

Liveness: a generic-wrapper or non-functional method that ships unnoticed is the
failure mode; the skeleton must reject generic wrappers and ambient-loaded
historical reps, and prove every method produces output (non-empty default
roster), before broader work.

## Strategic Alternatives

- **Docs-only clarification** — rejected: it would fix overstatement but not let
  the user actually use the modes, which is an explicit goal.
- **One generic `/convene` prompt with a `mode=` argument** — rejected as the
  only surface: it is easy to implement but too easy for Claude/Codex affordances
  to miss, and it would not make each method directly callable.
- **Install historical representatives as global agents** — rejected: the user
  explicitly does not want them loaded ambiently into every session because they are often
  irrelevant.
- **Finish v1 automatic Slack routing first** — rejected as a blocker: v2 manual
  methods can be useful independently, and v1 is about automatic trigger moments
  rather than callable convening modes.

## Walking Skeleton

1. **Method registry + source-backed rosters.** Create the shared registry for
   all six methods with per-method default roster policy (practical vs
   historical), question-driven practical selection, lazy historical rosters,
   source URLs/notes, and synthesis rules. Include static checks that every
   selectable practical advisor resolves and every historical representative has a
   source note. Because the institutional methods (areopagus/parishad/yushitai)
   default to historical role-reps, this step also AUTHORS those rep modules — a
   scope cost the everyday practical-default methods do not incur, accepted as part
   of the all-six skeleton scope (see Decisions).
2. **Callable Claude/Codex surfaces.** Add six Claude command wrappers and six
   Codex skill entries that delegate to the registry. Each call loads the method's
   declared default roster (practical for everyday methods, historical role-reps
   for institutional methods), method-scoped only; roster overrides
   (`with historical representatives` / `practical-only`) change the roster, not
   the behavior contract. Nothing loads at session start.
3. **Evidence and mutation checks.** Add smoke fixtures for at least three
   different methods, plus static/mutation checks that fail a generic wrapper,
   a missing method, an unresolved advisor, a historical representative with no
   source note, and any implementation that loads historical reps by default.

## Proof of Delivery

This is done when all six methods are callable in Claude and Codex, no roster loads
at session start, each method's default invocation loads its declared roster
(everyday → practical, institutional → method-scoped historical reps) with
overrides changing only the roster, the registry validator proves the six method
contracts are pairwise-distinct, the live-output fixtures prove each method
produces output satisfying its distinct contract (required-output-field set +
refusal gate), and every method — including the three historical-default ones —
produces a usable result on a real prompt (non-empty default roster). A
lightweight invocation log exists for curiosity; there is no reuse/keep-kill gate.

## Anti-Metrics

1. Default session context increases because historical representatives are
   always installed or loaded.
2. All six methods produce the same structure with only the method name changed.
3. Source notes rot into vague provenance such as "ancient Greek philosopher" or
   "Chinese official" without a URL/title and confidence label.
4. Method calls bypass the current practical advisor agents and become
   historical roleplay instead of useful counsel.

## Decisions

- **Shared registry is the source of truth.** Chosen over hand-written command
  prompts because Claude and Codex surfaces must not drift. The registry should
  drive validation and, where practical, generation.
- **Direct method names plus shared runner.** Chosen over a single generic entry
  because the user wants each method callable by name. The shared runner keeps
  implementation small while preserving direct invocation.
- **Orthogonal structure/roster axes + per-method default roster.** A method's
  identity is its behavior contract (output schema, phases, refusal); who staffs it
  is a separate axis. Each method declares a default roster policy: everyday
  methods (jixia/seven-sages/junto) default to question-driven practical advisors;
  institutional methods (areopagus/parishad/yushitai) default to their
  purpose-built historical role/exemplar reps, which fit the adjudicative/
  stakeholder/audit structures better than the management-productivity advisors do
  — filling the gap left by the escapement repo split, where reviewer-type lenses
  live.
- **Lazy historical representatives.** Chosen over global agents because context
  cost matters: reps load only on invocation of a method that convenes them, never
  at session start or into routine advice — even for historical-default methods.
- **Role modules for institutional stories.** Chosen over fabricated named rosters
  for Areopagus, Parishad, and Yushitai because the sources describe offices,
  assemblies, and functions more clearly than stable member lists.
- **Skeleton covers all six methods and their behavior contracts.** Chosen
  because the success criterion is all methods callable, while the risky part is
  whether the method layer changes the workflow rather than only changing the
  advisor roster. Reaffirmed 2026-06-16 after the roster model added historical
  rep-authoring for the three institutional methods (areopagus/parishad/yushitai)
  to skeleton cost: the all-six scope is accepted with that cost rather than cut to
  a contrasting pair.

## Risks & Trade-offs

- Historical rosters become trivia → Mitigation: representative modules must
  translate source-backed history into a specific review stance and must be
  optional.
- Six direct surfaces create maintenance duplication → Mitigation: make wrappers
  tiny and registry-backed; static checks compare wrappers to registry entries.
- Codex and Claude capability models diverge → Mitigation: define the shared
  contract at the registry layer, then keep platform surfaces thin.
- Fixture evaluation becomes subjective → Mitigation: test for structural and
  behavioral invariants that generic wrappers cannot satisfy. Usefulness is NOT
  gated (Non-Goal #6) — distinctness is the bar; the invocation log is curiosity
  only.
- V2 competes with unfinished v1 → Accepted because v1 automatic routing and v2
  manual convening answer different moments; the registry can be reused later.

## Future Increments

[PLACEHOLDER] — options purchased by validating the skeleton:

- **V1 integration** — `/advise` delegates to `method-registry` when the
  automatic routing work resumes. Done when a bounced Slack draft can name a
  method and route through the same registry, not when a second routing table is
  copied.
- **Benchmark harness (optional, curiosity only).** Since the methods are kept
  regardless, this is NOT a keep/kill instrument — run it only if the owner is
  curious whether a method beats ad hoc single-advisor selection. The only valid
  form is paired, blinded A/B on a frozen set of real historical prompts (same
  input through both arms, dispatched independently, outputs stripped of labels and
  scored by an LLM-judge against a pre-registered rubric). Formative, never powered
  at solo N. Explicitly not part of the skeleton or its done-bar.
- **Representative depth pass** — improve historical modules with stronger
  primary/academic sources. Done when every representative has a confidence label
  and at least one better-than-summary source where available, not when the first
  roster compiles.
- **More trigger moments** — backlog choice, PR review, incident writeups,
  message drafting. Done when an observed workflow invokes a method and changes
  the produced artifact, not when a trigger exists.

## Open Questions

- **[DEFERRABLE]** Whether historical representative modules should eventually be
  installable as true Claude agents. The skeleton should not do this because the
  user explicitly does not want them loaded ambiently into every session.
- **[DEFERRABLE]** Whether the `Seven Sages` default should use Myson or
  Periander. The registry can carry a default and variants; the exact default is
  not skeleton-blocking.
