# Test Oracle Brief — Jixia product front door

## Business invariant

An operator arriving at the repository can tell, before installing anything,
what Jixia is, when to use it, what the shortest real invocation looks like,
what kind of counsel comes back, and which outcomes remain unproven. The public
story must describe the existing advisory system rather than invent a hosted
product, a universal council, or cross-host parity that the repository does not
ship.

## Independent source of truth

- `jixia/registry.json` defines the six distinct convening methods, gates,
  output fields, roster defaults, and action-bearing fields.
- `claude/skills/advise/SKILL.md` and `advise-full/SKILL.md` define the two
  current routing front doors.
- `INSTALL.sh` determines what is installed globally and for which host.
- Merged GitHub pull requests #5, #6, #7, #11, #15, and #16 plus the current
  executable test suite provide inspectable implementation evidence. Their
  bodies report test runs, but the repository has no automated PR-check history
  for these changes.

The new README, tour, and evidence page do not certify themselves.

## Solution constraints

- Preserve the existing registry, classifier, dissent seat, advisors, skills,
  installer, logging, and send-bounce runtime.
- Keep Jixia a companion to Escapement, not part of Escapement's workflow
  engine.
- Make the globally installed Claude surface and repo-local Codex method skills
  explicit; do not imply a Codex global installer exists.
- Label the walkthrough representative rather than a captured consultation.
- Preserve the difference between executable mechanism evidence and evidence
  that advice improves decisions.
- Add no dashboard, hosted service, telemetry, new advisor, or runtime
  dependency.

## Invalid solution classes

- A slogan-only README edit that leaves invocation, evidence, and limitations
  buried or absent.
- A generic “AI council” pitch that implies every question runs many agents.
- A fabricated consultation or testimonial presented as observed evidence.
- A claim that Jixia is globally installed for Codex by `INSTALL.sh`.
- A claim that the routing logs or existing tests prove decision quality.
- Architecture-first documentation that requires readers to reconstruct the
  product from method names and agent files.

## Fragile implementation to reject

Add the new category and promise above the existing README without changing its
order or adding a concrete first invocation, inspectable evidence, and truthful
host/quality limits. The product-surface contract must fail that shortcut.

## Negative control

The contract must reject missing tour/evidence links, installation before
limitations, and semantic mutations claiming universal councils, universal
Codex installation, guaranteed decision improvement, or an always-blocking
Slack hook.

## Positive control

The first README section contains the category, promise, companion relationship,
and operator audience. Before installation, it links the representative tour and
evidence, explains when to use Jixia, and states the current host and outcome-
quality boundaries.

## Missing and unresolved handling

Missing files, dead local links, unknown host support, absent PR records, or
unobserved outcome quality fail closed. The prose must state “not proven” or the
test must fail; it must not fill gaps with inferred capability.

## Final outcome verification

Run the complete repository suite, then run
`bin/verify-product-front-door`. The latter always enables the fail-closed live
oracle: it resolves every cited pull request through GitHub, requires `MERGED`
state and merge metadata, checks that each quoted source fact occurs in the live
PR body, and verifies the absence of claimed check/workflow evidence. It fails
rather than skips when GitHub is unavailable. Verify that the pull request's
README ordering and linked files match the candidate. Because this repository's
declared landing outcome is `pr-opened`, delivery ends with a reviewed, pushed
pull request unless the owner separately authorizes a merge.
