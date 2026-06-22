# Convening-models research — VERIFIED synthesis (2026-06-22)

## Findings

Supersedes the caveats in `00-salvaged-synthesis.md`. The original deep-research run
reported "all 25 claims refuted" — that was a **false artifact**: the verifier votes
were rate-limited (abstentions mis-scored as refutations). A targeted re-verification
(one skeptical reader per source, fetched live, claims checked against the actual text)
was run. Result below.

### Verdict tally (24 claims, 7 sources, all fetched live)

- **SUPPORTED: ~22** (many verbatim, with calibration qualifiers noted)
- **OVERSTATED: 2** (both peripheral wording, not theme-breaking)
- **FABRICATED / UNSUPPORTED / killed-on-merit: 0**
- The original harness verdict (0 confirmed / 25 killed) was **100% an artifact**.

### Sources (titles + authors now confirmed real)

| ID | Paper | Authors | Verdicts |
|----|-------|---------|----------|
| S1 | "Debate or Vote: Which Yields Better Decisions in Multi-Agent LLMs?" (2508.17536) | Choi, Zhu, Li — UW-Madison | 3 SUPPORTED, 1 OVERSTATED |
| S2 | "Can LLM Agents Really Debate? …Logical Reasoning" (2511.07784) | Wu (McGill/Mila), Z. Li, L. Li (USF) | 4 SUPPORTED, 1 OVERSTATED |
| S3 | "Peacemaker or Troublemaker: How Sycophancy Shapes Multi-Agent Debate" (2509.23055) | Yao, Shang, Du, He, Lian, Zhang, Su, Swamy, Qi — AWS AI Labs / UW-Madison | 5 SUPPORTED |
| S4 | "Talk Isn't Always Cheap: …Failure Modes in Multi-Agent Debate" (2509.05396) | Wynn (JHU), Satija (Vector), Hadfield (JHU) | 4 SUPPORTED |
| S5 | "Large Language Models Cannot Self-Correct Reasoning Yet" (2310.01798) | Huang et al. — Google DeepMind + UIUC | 2 SUPPORTED |
| S6 | "When Can LLMs Actually Correct Their Own Mistakes?" (TACL; mirror 2406.01297) | Kamoi et al. | 2 SUPPORTED (abstract-level; TACL URL 403, arXiv mirror used) |
| S7 | "Auditing Multi-Agent LLM Reasoning Trees Outperforms Majority Vote and LLM-as-Judge" (2602.09341) | Yang, S. Li, Ping, Zhang, Bogdan, Thomason | 3 SUPPORTED — **SOURCE IS REAL** |

### The two OVERSTATED claims (corrected)

- **S1-C4:** "contagion/propagate" + "only modest recovery" — the paper uses
  "subversion/convergence," and its interventions (Conformist/Follower) actually
  recover Arithmetics 0.76→0.92 ("meaningfully enhance"). → Drop "contagion" and the
  "only modest" minimizer.
- **S2-claim5:** "shared training/biases → echo chambers" is **cited prior work**
  (Oh 2025, Estornell 2024, Liu 2025) in S2's intro, NOT S2's own finding. S2's own
  result is "weak teams converge prematurely." → Attribute correctly.

### VERIFIED themes (design-driving)

1. **Voting ≥ debate; multi-round debate often doesn't help and can degrade.**
   S1 (voting 0.7691 *beats* debate avg 0.733–0.738, exact); S4 (debate "always harms"
   CommonSenseQA across tested configs — empirical, small-benchmark, not a theorem);
   S2 (gains bounded by the strongest reasoner; whether it's genuine debate vs
   ensembling is questioned). **Confidence: HIGH (3 sources).**
   CALIBRATION: don't upgrade authors' "can/may/preliminary" to "always/will."

2. **Sycophancy / disagreement-collapse is the dominant failure; mitigated by a
   low-sycophancy DISSENTER + capping rounds to 2-3.** S3, stats **verbatim**: debater
   sycophancy↔abandoning-correct r=0.902; judge r=0.639; worst-cell DCR 86.36%
   (decentralized 2-agent homogeneous Llama3.3-70B — preserve the qualifier). Best
   configs mix "peacemaker"+"troublemaker"; sycophancy intensifies in later rounds.
   **Confidence: HIGH.**

3. **Self-correction needs EXTERNAL feedback; intrinsic self-refine is unreliable and
   can degrade.** S5 (DeepMind: accuracy drops across all benchmarks after intrinsic
   self-correction — reasoning-scoped); S6 (no prior work shows successful
   self-correction from prompted-LLM feedback except exceptionally-suited tasks; works
   only with reliable external feedback or large-scale fine-tuning). **Confidence: HIGH.**

4. **Structured agreement/divergence aggregation beats majority-vote (~5%) and
   LLM-as-Judge (~3% CEILING, ~1-2% typical).** S7 (AgentAuditor) — source REAL.
   **Confidence: MEDIUM** — single non-peer-reviewed preprint, 4 months old; its
   theory (correlated-vote / confabulation-consensus) is a *borrowed* Austen-Smith &
   Banks 1996 result used as interpretation, explicitly NOT claimed as novel proof.
   Treat as one strong data point, not settled science.

5. **LLM-as-Judge inherits majority/conformity bias; cheap to mitigate** (a
   moderate/fixed-sycophancy judge is adequate; elaborate debiasing not needed). S3 + S7.
   **Confidence: MEDIUM.**

### Design implications — now VERIFIED (not just salvaged)

- **Do NOT build multi-round debate as a convening mode.** [verified — themes 1,2]
- **The dissenter/counter-lens is load-bearing; keep it low-sycophancy; cap interaction
  at 2-3.** [verified — theme 2] → directly validates the `/advise-full` UX decision to
  NAME the dissenter on Turn 1 and HARD-CAP rounds (never expose a rounds knob).
- **Advisor lenses as external grounding beat single-agent self-critique.** [theme 3]
  → do not add a self-refine convening mode; the lenses ARE the external grounding.
- **Structured agreement/divergence aggregation = the one genuinely-new high-value
  structure** → candidate 7th convening model, but ship it FLAGGED EXPERIMENTAL
  (single-preprint evidence), not as a peer of the battle-tested structures.
- **Caution on judge-decides modes** (areopagus verdict): real judge bias, cheap mitigation.

### Residual gaps (unchanged from salvaged)

- All 7 sources are LLM-specific. The **human-deliberation / Delphi / premortem** angles
  never fetched — no evidence either way on those. (User opted not to fill this yet.)
- S6 verified at abstract level only (TACL body 403; arXiv mirror abstract enumerates
  the findings).
