# Convening-models research — salvaged synthesis (2026-06-22)

## Findings

### Provenance & honesty caveat (read first)

The deep-research run (`wf_f2359f37-e10`) **completed with degraded fidelity**:

- **Fetch phase throttled:** only **7 of ~15** intended sources were fetched; the rest
  failed with "Server is temporarily limiting requests." The 7 that survived are
  **all LLM-multi-agent-specific** — the *human-deliberation*, *Delphi*, and
  *premortem* angles produced search hits but their sources were **not fetched**.
  → **Coverage gap: this corpus says nothing about human group-decision evidence.**
- **Verify phase fully throttled:** every 3-vote adversarial check failed to run
  (rate-limited). The harness logged each as `0-0 (3 abstain) ✗` and the synthesizer
  **mis-scored abstentions as refutations**, emptying `findings[]` and reporting
  "all 25 claims refuted." That headline is an ARTIFACT, not a result.

**Therefore:** the claims below are **extracted from primary sources but NOT
independently re-verified in this run.** Treat qualitative themes (convergent across
multiple papers) as well-supported; treat **specific statistics as [UNVERIFIED —
single-source]** and re-check before quoting.

### Sources fetched (7, all primary; arXiv + TACL)

| ID | URL | claims |
|----|-----|--------|
| S1 | https://arxiv.org/html/2508.17536v1 | 4 |
| S2 | https://arxiv.org/html/2511.07784v1 | 5 |
| S3 | https://arxiv.org/html/2509.23055v1 | 5 |
| S4 | https://arxiv.org/pdf/2509.05396 | 5 |
| S5 | https://arxiv.org/abs/2310.01798 | 3 |
| S6 | https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00713/... (When Can LLMs Actually Correct Their Own Mistakes) | 4 |
| S7 | https://arxiv.org/html/2602.09341v1 | 5 |

### Convergent themes (multi-source — design-grade signal)

1. **Naive multi-agent debate (MAD) often does NOT help, and can actively hurt.**
   Majority voting matches/exceeds debate (S1); degradation vs a no-debate baseline
   is "not a rare edge case" and on CommonSenseQA debate *always* harmed (S4);
   extended rounds degrade (S1, S4); procedural knobs (confidence visibility, order,
   +rounds) had negligible effect — initial accuracy & team size dominated (S2).
   Sources: S1, S2, S4. **Confidence: HIGH (4 independent papers converge).**

2. **Sycophancy / conformity / "disagreement collapse" is the dominant failure mode.**
   Agents abandon *correct* answers under majority pressure; weaker models in a wrong
   majority almost never self-correct while stronger ones do ~30% (S2); homogeneous
   personas collapse (Disagreement-Collapse-Rate up to 86% [UNVERIFIED] on Llama, S3);
   sycophancy↔abandoning-correct r=0.90 [UNVERIFIED] (S3); flips skew
   correct→incorrect, worst when the correct agent is isolated (S4).
   Sources: S2, S3, S4. **Confidence: HIGH.**

3. **Self-correction (reflexion / self-refine) needs EXTERNAL feedback.** Intrinsic
   self-correction (a model critiquing its own output with no external signal) is
   unreliable and can degrade performance; works only with an oracle/verifier/tool or
   trained-in correction (S5, S6). External grounding — independent lenses, retrieved
   evidence, a different-vantage judge — is categorically different and better (S5).
   Sources: S5, S6. **Confidence: HIGH.**

4. **LLM-as-Judge inherits sycophancy/position bias** (defaults to the majority even
   when the minority is better supported) (S7). Mitigation is cheap: a judge with a
   moderate/fixed sycophancy level is adequate — elaborate debiasing not required (S3).
   Sources: S3, S7. **Confidence: MEDIUM.**

5. **Structured agreement/divergence aggregation beats both majority vote and a judge.**
   Auditing a "Reasoning Tree" that explicitly represents where agent traces agree and
   diverge outperformed majority vote (~+5% [UNVERIFIED]) and LLM-judge (~+3%
   [UNVERIFIED]) across 6 architectures / 4 benchmarks (S7). Majority vote fails under
   correlated biases ("confabulation consensus") — more agents don't help if they
   share biases (S7). Source: S7. **Confidence: MEDIUM (single source).**

### What the research SUPPORTS (mitigations that worked)

- **Heterogeneous personas with a designated low-sycophancy DISSENTER** ("troublemaker"
  + "peacemaker") was the best-performing debate config (S3). → the counter-lens /
  devil's advocate is not decoration; it's the load-bearing element.
- **Cap interaction to 2-3 rounds** — later rounds add sycophancy, not accuracy (S3, S4).
- **Ensure a strong reasoner is present;** diversity helps ONLY then (S2).

## Design implications for `/advise` convening-model routing

**AGAINST building** a free-for-all "N agents debate for K rounds" convening mode —
that is the single most cautioned-against topology in this corpus.

**FOR (highest-value routing targets):**
1. **Independent-parallel-then-synthesize** (advisors give independent counsel, a
   synthesis step merges) — research-favored over iterative debate. *Already what
   `jixia` / `/advise` do* → validates the existing default; formalize, don't replace.
2. **Designated dissenter / devil's advocate** (the counter-lens, made explicit and
   low-sycophancy) — best-performing config. *Maps to `/advise`'s counter-lens and
   `areopagus` role structure* → strengthen the dissenter's prompt to resist agreement.
3. **Structured agreement/divergence aggregation** (the "Reasoning Tree" idea) — beats
   majority vote and judge. *Genuinely NEW vs our six* → candidate synthesis layer.
4. **External-grounding review** (lenses/evidence) OVER single-agent self-critique —
   avoid a self-refine convening mode; the advisor lenses ARE the external grounding.

**Caution on judge-decides modes** (`areopagus` verdict, debate-with-judge): judge
sycophancy/position bias is real; prefer structured divergence representation over a
single judge's ruling, or use a fixed-moderate-sycophancy judge.

## Bottom line

The strongest evidence-backed move is **not** adding new debate machinery — it is
**formalizing what we already have** (parallel-independent + explicit dissenter +
synthesis) and adding **one genuinely new structure**: a structured
agreement/divergence aggregation layer. Iterative multi-round debate should be
*deprioritized or omitted* as a routing target.

## Owed (to close the gap)

- Re-run verification when rate limits clear (the claims above are unverified-this-run).
- A second pass covering the MISSING angles: human-deliberation / Delphi / premortem
  evidence (none survived fetch) — needed before claiming those structures help or not.
