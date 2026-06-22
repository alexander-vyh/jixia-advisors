# Adversarial Verification — arXiv 2602.09341 (Reasoning Tree / AgentAuditor)

## Findings

### Source reality check — THE SOURCE IS REAL

The arXiv id **2602.09341 resolves to a real 2026 paper.** Both
`https://arxiv.org/html/2602.09341v1` (63 sections, 134 KB) and
`https://arxiv.org/abs/2602.09341` fetched successfully and are internally
consistent on title, authors, and date.

- **Title:** "Auditing Multi-Agent LLM Reasoning Trees Outperforms Majority Vote and LLM-as-Judge"
- **Authors:** Wei Yang, Shixuan Li, Heng Ping, Peiyu Zhang, Paul Bogdan, Jesse Thomason
- **Category:** cs.AI
- **Submitted:** 10 Feb 2026
- The system it introduces is named **AgentAuditor**, plus a training method **ACPO** (Anti-Consensus Preference Optimization).

This is NOT a fabricated source. The "new structure" recommendation that rests on it
has a real paper underneath. (Caveat: a single arXiv preprint, not peer-reviewed;
its own Appendix C explicitly disclaims novel theoretical guarantees — see Claim 2.)

---

### Claim 1 — "~5% over majority vote, ~3% over LLM-as-Judge, six architectures, four benchmarks"

**Verdict: SUPPORTED (with one internal-inconsistency caveat the paper itself carries).**

Exact figures from the paper:
- **Abstract:** "across 5 popular settings that it yields **up to 5% absolute accuracy
  improvement over a majority vote, and up to 3% over using LLM-as-Judge.**" — the
  "up to ~5% / ~3%" framing is verbatim and correct.
- **Body (§6.1 RQ1):** "consistently outperforms both Majority Voting (MV) and
  LLM-as-Judge **across six architectures and four benchmarks**." The "six
  architectures / four benchmarks" framing is verbatim and correct.
- Supporting numbers: average ~3% over MV, peak **+5.7% on AMC (GPTSwarm)** and
  **+5.5% on GSM8K (DyLan)** — consistent with "up to 5%."
- vs LLM-as-Judge: "approximately 1–2%" on the headline benchmarks (e.g. 59.92 vs
  58.10 on LLM-Debate), with "up to 3%" as the maximum. The headline-typical gain
  over the Judge is closer to 1–2%; 3% is the ceiling, not the average.
- Four benchmarks confirmed in Appendix B.1: **GSM8K, MATH, AMC, MMLU.**

**Caveat — internal inconsistency in the paper (not the team lead's framing):** the
abstract says "**5** popular settings" while the body and Table 1 say "**six**
architectures." The team lead's claim says "six architectures / four benchmarks,"
which matches the body and the experimental tables — so the team lead's claim is the
*correct* count. The 5-vs-6 wobble is a defect IN the paper's own abstract, not in
the claim being checked. Recommend citing "six architectures, four benchmarks" (body)
rather than the abstract's "5 settings."

The "~3% over Judge" is mildly **generous as a typical number** (typical 1–2%, max
~3%), but the claim says "up to ~3%," which is exactly the ceiling the paper reports.
SUPPORTED.

---

### Claim 2 — "Majority voting fails under correlated bias (confabulation consensus); theoretically, if inter-agent correlation is bounded away from zero, adding more agents does not improve majority-vote reliability"

**Verdict: SUPPORTED — but the theory is explicitly a 'supporting interpretation,' not a proven guarantee.**

- "Confabulation consensus" is the paper's central named failure mode, defined exactly
  as the claim states: agents "share correlated biases and converge on the same
  incorrect rationale" (abstract).
- The theoretical part is **Proposition C.1 (Appendix C.1, "Failure of independence
  assumption")**, built on a correlated-voting model citing Austen-Smith & Banks (1996):
  "If ρ=0 and p>1/2, then Var(X̄)=O(1/N) and X̄ concentrates around p, recovering the
  classical CJT [Condorcet Jury Theorem] intuition. **If ρ>0 is bounded away from 0,
  then Var(X̄) does no[t vanish]**" — i.e. the variance floor means adding agents N→∞
  does NOT drive the estimator to concentrate, so more agents do not buy reliability.
  This is exactly the claim's "bounded away from zero ⇒ more agents don't help."
- **Critical scrutiny / honest caveat the team lead should know:** Appendix C opens
  with an explicit disclaimer — "Our goal is **not to introduce a new theory or claim
  novel guarantees** for arbitrary LLM behaviors... The analysis should be read as an
  **interpretation of the underlying mechanism rather than a complete characterization**."
  So the "theoretically" in the claim is real but is a *known textbook* correlated-CJT
  result (Austen-Smith & Banks) applied as an interpretive lens, NOT a novel theorem the
  authors prove for LLMs. The empirical anchor is stronger: in §6.2 RQ2, on
  Minority-Correct instances MV "deterministically achieves 0% by construction" — a
  clean demonstration that multiplicity of a wrong answer cannot be voted away.

SUPPORTED as stated; downgrade only if someone reads "theoretically … proven" as a
novel LLM-specific guarantee — it is a borrowed social-choice result used as
interpretation, by the authors' own admission.

---

### Claim 3 — "LLM-as-Judge is prone to sycophancy/conformity bias, defaulting to the majority view even when the minority is better supported"

**Verdict: SUPPORTED as the paper's stated motivation; the 'defaults to majority' mechanism is asserted + empirically indicated, not isolated in a dedicated bias experiment.**

- §1 Introduction states it directly: "a straightforward alternative is to adopt an
  LLM-as-a-Judge, yet **naive judging is insufficient because it is both
  computationally inefficient and prone to sycophancy bias.**"
- The paper's whole ACPO contribution is framed as immunizing the auditor against this:
  "ACPO, a training strategy that **immunizes the Auditor against sycophancy bias** by
  optimizing for minority-truth" — and "explicitly penalizes popular-but-wrong decisions
  and rewards minority-but-correct reasoning."
- Empirical support that the Judge under-recovers minority-correct cases: §6.2 RQ2 —
  AgentAuditor beats LLM-as-Judge "by roughly 9 points on both [GSM8K and AMC]" on the
  Minority-Correct regime, and "this margin suggests that generic judging is
  insufficient." This is consistent with the Judge defaulting toward support cues
  (≈ the majority) rather than branch-level evidence.

**Honest scope note:** the "sycophancy/conformity, defaults to majority" mechanism is
stated as motivation and supported indirectly by the MinC gap; I did not find a
dedicated controlled ablation that isolates *sycophancy specifically* (vs. the Judge's
other named weakness, attention dilution over long multi-agent contexts). The claim is
true to the paper's argument, but the cleanest evidence is the 9-point MinC gap, not a
purpose-built sycophancy probe.

---

## Bottom line for the team lead

- **The source is real.** 2602.09341 is a genuine 10-Feb-2026 cs.AI arXiv preprint
  with the exact title/authors implied. The "new structure" recommendation is not
  resting on a hallucinated citation.
- **All three claims are SUPPORTED** in substance. None is fabricated or contradicted.
- **Three caveats to carry forward, in order of importance:**
  1. It is a **single non-peer-reviewed preprint** (4 months old). For a load-bearing
     "adopt a new design structure" decision, treat it as one promising data point, not
     settled science.
  2. The **theory (Claim 2) is the authors' own admitted *interpretation*** of a
     classic correlated-CJT result (Austen-Smith & Banks 1996), explicitly NOT a novel
     guarantee. Cite it as motivation, not proof.
  3. Minor internal inconsistency: abstract says "5 settings," body says "six
     architectures." Cite the body's "six architectures, four benchmarks (GSM8K, MATH,
     AMC, MMLU)" — that is the count the experiments actually support.
  4. The "~3% over LLM-as-Judge" is the ceiling; typical gain over the Judge is ~1–2%.
