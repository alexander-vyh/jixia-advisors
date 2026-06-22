# Convening-models research (June 2026)

Research pass on **which multi-agent deliberation / review / analysis topologies have
documented evidence of improving the quality of agentic analysis** — run to inform the
`/advise` convening-model routing increment (advisor-routing increment-2).

Promoted here from the ephemeral `.research/` scratch (gitignored) because it is a
durable knowledge body to revisit, not transient agent output. Content is citations of
public arXiv / TACL papers — no PII, no secrets.

## Start here

- **[`01-verified-synthesis.md`](01-verified-synthesis.md)** — the authoritative result.
  Verdict tally, the 7 verified sources, the design-driving themes with confidence
  levels and calibration caveats, and the design implications.
- **[`00-salvaged-synthesis.md`](00-salvaged-synthesis.md)** — the first-pass synthesis,
  kept for provenance (documents the rate-limit failure and the salvage).

## Per-source adversarial verification

One skeptical reader per source, fetched live, claims checked against the actual text:

| File | Source |
|------|--------|
| [`verify-s1.md`](verify-s1.md) | "Debate or Vote…" (arXiv 2508.17536) |
| [`verify-s2.md`](verify-s2.md) | "Can LLM Agents Really Debate?…" (arXiv 2511.07784) |
| [`verify-s3.md`](verify-s3.md) | "Peacemaker or Troublemaker: How Sycophancy Shapes Multi-Agent Debate" (arXiv 2509.23055) |
| [`verify-s4.md`](verify-s4.md) | "Talk Isn't Always Cheap…" (arXiv 2509.05396) |
| [`verify-s56.md`](verify-s56.md) | "LLMs Cannot Self-Correct Reasoning Yet" (2310.01798) + "When Can LLMs Actually Correct Their Own Mistakes?" (TACL / 2406.01297) |
| [`verify-s7.md`](verify-s7.md) | "Auditing Multi-Agent LLM Reasoning Trees…" (arXiv 2602.09341) |

## Headline

The original deep-research harness reported **"all 25 claims refuted"** — a **false
artifact**: the verifier votes were rate-limited (abstentions mis-scored as
refutations). Targeted re-verification found the opposite: **~22 of 24 SUPPORTED, 2
overstated (peripheral wording), 0 fabricated.** The load-bearing single-source
(2602.09341) was confirmed **real**.

## What it concluded (one paragraph)

Naive multi-round LLM debate often does NOT beat majority voting and can degrade
accuracy; the dominant failure mode is **sycophancy / disagreement-collapse** (agents
abandon correct answers to agree). The verified mitigation is a **mandated,
low-sycophancy dissent role** plus capping interaction to 2-3 rounds. Single-agent
self-critique (reflexion/self-refine) is unreliable without external feedback — so the
advisor *lenses* (external grounding) are the right mechanism, not self-revision. One
genuinely-new high-value structure surfaced (structured agreement/divergence
aggregation, "AgentAuditor"), but on single-preprint evidence — promising, not settled.

## Known gaps (for the next dive)

- All 7 sources are **LLM-specific**. The human-deliberation / Delphi / premortem
  search angles never fetched — no evidence gathered either way.
- `verify-s56` source B verified at abstract level only (TACL body returned HTTP 403;
  arXiv mirror abstract enumerates the findings).
- The "AgentAuditor" aggregation result is a single non-peer-reviewed preprint (~4
  months old) whose theory is a *borrowed* result used as interpretation — re-check
  before relying on it.

## Related

- Design principle distilled from this: **mandated dissent** (see bd memory
  `jixia-convening-mandated-dissent-principle-2026-06-22`).
- The `/advise-full` menu design informed partly by this lives in the (gitignored)
  `.research/advise-full-ux-20260622/` scratch — not yet promoted.
