# Adversarial Fact-Check — arXiv 2509.23055

**Source:** "Peacemaker or Troublemaker: How Sycophancy Shapes Multi-Agent Debate"
Binwei Yao, Chao Shang, Wanyu Du, Jianfeng He, Ruixue Lian, Yi Zhang, Hang Su,
Sandesh Swamy, Yanjun Qi. AWS AI Labs / University of Wisconsin–Madison.
URL fetched and indexed successfully: https://arxiv.org/html/2509.23055v1 (v1, HTML, 36 sections / 84KB).

## Findings

### Claim 1 — Sycophancy harms accuracy via disagreement collapse; sycophantic configs below single-agent baselines
**Verdict: SUPPORTED, with one wording nuance (mild OVERSTATEMENT risk on "below").**

Direct support for the mechanism: "excessive sycophancy consistently harms performance by accelerating disagreement collapse, especially when both agents adopt highly conciliatory 'peacemaker' personas." Abstract: sycophancy "amplifies disagreement collapse before reaching a correct conclusion ... yields lower accuracy than single-agent baselines."

NUANCE: The body's concrete claim about the worst (homogeneous Llama3.3-70B) case is "no gain over single-agent baselines" — i.e. it matches the single-agent baseline, not strictly below it. The abstract's stronger phrasing "lower accuracy than single-agent baselines" is the paper's own framing, so the claim is faithful to the paper. But "performing below single-agent baselines" as a flat statement is slightly stronger than the body's per-config "no gain" wording. The paper supports it as an abstract-level conclusion; the strongest per-config evidence is "no gain," not a measured drop below. Treat "below baseline" as the paper's claim, not a precisely-quoted per-config number.

### Claim 2 — Pearson r=0.902 (debater) and r=0.639 (judge)
**Verdict: SUPPORTED — both values verbatim accurate.**

Debater NAR (negative agreement rate, = abandoning correct answers under disagreement) vs SS (sycophancy score): "We observe a strong positive correlation (Pearson r=0.902)." Figure 2(a) caption: "Debater NAR v.s. SS: r=0.902".

Judge DCR (disagreement collapse rate) vs SS: "We observe a positive correlation (Pearson r=0.639), suggesting that judges' disagreement collapse is partly driven by copying debaters' answers without sufficient independent evaluation." Figure 2(b) caption: "Judge DCR v.s. SS: r=0.639".

Both figures are over "all CommonsenseQA settings." Note: the claim describes 0.639 as "moderate" — the paper itself calls 0.902 "strong" and 0.639 only "positive" (no adjective), so "moderate" is a reasonable but author-supplied gloss, not the paper's word. Minor, not a misquote.

### Claim 3 — Mixing personas best; cap rounds to 2-3
**Verdict: SUPPORTED — both halves accurate.**

Persona mixing: "the best-performing configurations are not those with universally low sycophancy, but rather those that strike a balance between independence and cooperativeness, for example, mixing 'peacemaker' and 'troublemaker' roles. Such diversity allows debates to remain steerable while still preserving the adversarial tension necessary for accuracy gains."

Round capping (Appendix H): "Strategic round selection requires capping debate rounds to 2-3 substantive exchanges, as sycophancy intensifies in later rounds." Supporting finding: "sycophantic behavior not only persists throughout the debate process but actually intensifies in later rounds ... agents typically exhibit their lowest levels of sycophancy during the first round."

Caveat for downstream use: the all-troublemaker (both low-sycophancy) config was actually peak in the *heterogeneous* Qwen-Llama grid (78.95–82.06%, peak at both-troublemaker). The "mixing" principle is the paper's stated design principle; the raw grid peak in one cross-model setting was both-troublemaker. The claim reflects the paper's recommended principle correctly.

### Claim 4 — DCR up to 86.36% on CommonsenseQA with Llama
**Verdict: SUPPORTED — verbatim accurate.**

"In decentralized debates, homogeneous Llama3.3-70B shows the highest DCR (up to 86.36% in 2-agent CommonsenseQA) and no gain over single-agent baselines."
Precise qualifiers to preserve: it is the *decentralized*, *2-agent*, *homogeneous Llama3.3-70B* configuration — the single worst cell, not a typical/average DCR. Stating "up to 86.36%" (as the claim does) is correct; stating it as the general collapse rate would be overstatement.

### Claim 5 — Judge robustness achievable simply; moderate/fixed sycophancy adequate, no elaborate debiasing
**Verdict: SUPPORTED.**

"Judge Performance Is Robust Across Sycophancy-Controlled System Prompts ... controlling the judge's sycophancy via system prompts does not substantially affect system performance, particularly in three-agent debates ... accuracy ... fluctuating only slightly around 86–87% [CommonsenseQA] ... baseline performance aligns closely with performance at moderate sycophancy levels." Judge sycophancy was controlled levels 1–8 via system prompt.

The "not requiring elaborate debiasing" phrasing is an inference from "robust across levels / moderate level adequate" — the paper does not use the word "debiasing," but the conclusion (a simple/moderate judge setting suffices, judge tuning is not a high-leverage knob) is directly supported. Reasonable paraphrase, not a misquote.

## Summary
- r=0.902 and r=0.639: BOTH VERBATIM ACCURATE.
- 86.36%: VERBATIM ACCURATE (worst-case cell: decentralized 2-agent homogeneous Llama3.3-70B CommonsenseQA — preserve the qualifier).
- Only soft flag: Claim 1's "below single-agent baselines" is the paper's abstract framing; the strongest *per-config* body evidence is "no gain over" the baseline. Faithful to the paper, marginally stronger than the per-config number.
