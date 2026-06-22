# Adversarial Verification — arXiv 2508.17536v1

**Source:** https://arxiv.org/html/2508.17536v1 (fetched and parsed successfully — NOT rate-limited)
**Title:** "Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?"
**Authors:** Hyeong Kyu Choi, Xiaojin Zhu, Yixuan Li (Dept. of Computer Sciences, University of Wisconsin–Madison)
**Method note:** Prose verified via FTS5 search; all numeric claims verified by parsing the raw HTML tables directly (Table 1 = Qwen2.5-7B main results; Table 2 = belief-update interventions). FTS5 snippets initially surfaced Table 4 (Qwen2.5-32B) numbers, which differ — numeric verdicts below rest on the correctly-identified tables.

## Findings

### Claim 1 — Majority voting on par with debate; 0.7691 voting vs 0.7330–0.7377 debate (Qwen2.5-7B)
**Verdict: SUPPORTED**

Table 1 (Qwen2.5-7B-Instruct), Average column, ground-truth values:
- Majority Voting = **0.7691** (exact match)
- Decentralized MAD T=2 = **0.7377**; Sparse MAD T=2 = **0.7330** (the cited 0.7330–0.7377 range is exactly the two best debate configs' averages)
- Best debate avg (0.7377) < voting (0.7691); single-agent baseline = 0.7205

Abstract: "Majority Voting alone accounts for most of the performance gains typically attributed to MAD." §3.2: "in most cases, majority voting performs on par with MAD." The framing and all three numbers check out. Minor nuance: "on par with debate" is slightly generous — voting actually *beats* every debate config on average for 7B (0.7691 vs ≤0.7377), though within-benchmark it is "on par" in many cells. The claim's own numbers make voting the winner, so the wording errs conservative, not overstated.

### Claim 2 — Debate alone does not improve expected correctness; martingale over belief trajectories
**Verdict: SUPPORTED**

Theorem 2 (Martingale Behavior of Multi-Agent Debate), §4: "the agent's belief in the correct answer behaves like a martingale—that is, its expected value remains unchanged across rounds... debate itself does not systematically improve or degrade an agent's belief on average... the expected belief in the correct answer remains equal to the initial p_0." Abstract: "we prove that it induces a martingale over agents' belief trajectories, implying that debate alone does not improve expected correctness." Direct, near-verbatim support. (The model is a Dirichlet-Compound-Multinomial / Pólya-urn process; the martingale result is theoretical, under that model's assumptions — worth noting it is a modeling result, not a model-free empirical law.)

### Claim 3 — Extended rounds can degrade; Decentralized MAD 0.76 (T=2) → 0.67 (T=5) on Arithmetics; well-prompted single agents can outperform
**Verdict: SUPPORTED**

Table 1, Decentralized MAD, **Arithmetics** column: T=2 = **0.7600**, T=3 = 0.6700, T=5 = **0.6700**. Exact match (decline lands by T=3 and holds flat at T=5; "0.76 → 0.67" is correct). Average column also declines monotonically: T=2 0.7377 → T=3 0.7112 → T=5 0.7050, confirming "extended rounds can degrade."
"Well-prompted single agents can sometimes outperform debate" — this is in §7 Related Works, attributed to wang2024rethinking ("well-prompted single agents can sometimes outperform MAD"), NOT an original finding of this paper. Claim attributes it to "this source," which is technically correct (it appears in the source) but it is the source *citing prior work*, not the source's own result. Direction fully supported; provenance is secondhand.

### Claim 4 — Debate-only convergence/contagion failure; majority-biasing (Conformist/Follower) yields only MODEST recovery
**Verdict: OVERSTATED**

Two problems:

1. **Terminology not in paper.** "Contagion" appears **0 times**; "propagate"/"propagation" appears **0 times** in the paper. The paper uses "subversion" (belief moving away from correct), "convergence to the majority opinion / common misconceptions" (the latter quoting estornell2024multi in Related Works), and notes "debate alone does not guarantee convergence to the truth." The "contagion" framing and "propagate through belief updating" phrasing are the claimant's gloss, not the paper's language. Defensible as paraphrase of subversion dynamics, but presented as if it were the paper's vocabulary.

2. **"Only modest recovery" understates the result.** Table 2 (Decentralized MAD): MAD-vanilla avg 0.7332 (T=2) → MAD-Conformist 0.7625 / MAD-Follower 0.7629. On the **Arithmetics** column the recovery is large: vanilla 0.76 → Conformist/Follower **0.92** at T=2 (and 0.67 → 0.90–0.91 at T=5). The paper's own prose (§5.2): these strategies "**consistently outperform** the MAD-vanilla." The paper frames Conformist/Follower as a *meaningful, consistent* improvement — the abstract says targeted interventions "can **meaningfully enhance** debate effectiveness." Calling this "only modest recovery" contradicts the paper's characterization. (MAD-oracle is even stronger, ~0.82–0.83 avg, but it requires ground-truth access; Conformist/Follower are the realistic ones and still clearly beat vanilla.)

Direction (interventions help) is right; "only modest" is the overstatement — it minimizes a result the authors call meaningful and consistent, and the "contagion/propagate" vocabulary is imported.
