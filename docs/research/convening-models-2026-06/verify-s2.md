# Adversarial Verification — arXiv 2511.07784

**Paper:** "Can LLM Agents Really Debate? A Controlled Study of Multi-Agent Debate in Logical Reasoning"
**Authors:** Haolun Wu (McGill / Mila), Zhenkun Li, Lingyao Li (University of South Florida). [Wu and Z. Li / L. Li contribute equally.]
**Source:** https://arxiv.org/html/2511.07784v1 — fetched and fully indexed (53 sections). ACCESSIBLE.
**Method:** Controlled study on the Knight–Knave–Spy logic puzzle (verifiable ground truth), six structural/cognitive factors (team size, composition, confidence visibility, debate order, debate depth, task difficulty).

## Findings

### Claim 1 — "MAD improves collective accuracy on logical reasoning, but improvement is bounded by the strongest individual reasoner; coordination cannot overcome weak reasoning foundations."
**Verdict: SUPPORTED (with one caveat).**

- Boundedness + coordination-can't-overcome — directly and almost verbatim supported. Discussion §7: "coordination mechanisms alone cannot overcome weak reasoning foundations, and that the ceiling of debate success is effectively bounded by the strongest participant." §6.1: "performance remains bounded by the strongest reasoner available."
- CAVEAT on "MAD improves collective accuracy": the paper does NOT headline a clean "debate beats single agent" result. Its framing is comparative across team compositions, and its whole thesis questions whether gains are "genuine debate or simply the effects of ensembling and majority voting." It does find larger teams help (regression: number of agents has a significant positive effect, p<0.001) and that wrong-consensus reversals drive accuracy. So "improves collective accuracy" is defensible but is a softer/more-qualified result in the paper than the claim's flat assertion implies. Not an error; mild risk of overstatement if read as "MAD reliably beats solo."

### Claim 2 — "Majority pressure suppresses independent error correction: weaker models in an incorrect majority almost never self-correct (gemini-2.5-flash-lite corrected only 3.6%), while stronger models corrected ~30-34%."
**Verdict: SUPPORTED (precision caveats — do not drop the qualifiers).**

Exact paper text (§6.2, "Majority pressure suppresses agents' independent correction"): facing an incorrect majority (MaW), "Stronger models like gemini-2.5-flash and gpt-5-mini show a moderate ability to correct the incorrect consensus (34.4% and 30.0% correction, respectively), while weaker models are almost entirely swayed by the group, with gemini-2.5-flash-lite (mix_A) correcting itself in only 3.6% of such cases."

Caveats an honest cite must keep:
- The 3.6% figure is **mix-conditional** — the paper writes "gemini-2.5-flash-lite **(mix_A)**" and explicitly flags "teammate effects," noting gemini-2.5-flash-lite "show[s] significantly different correction rates depending on the experimental mix." Citing "3.6%" as a flat property of the model drops the qualifier the authors deliberately attached.
- "~30-34%" is accurate but conflates two different models: gemini-2.5-flash = 34.4%, gpt-5-mini = 30.0%. The range is right; attributing it generically to "stronger models" is fine.
- Direction and magnitude of the claim are fully correct. The wording "almost never self-correct" matches the paper's "almost entirely swayed by the group."

### Claim 3 — "Model diversity provides consistent gains in debate stability/accuracy ONLY when strong reasoners are present; without them, diversity does not help."
**Verdict: SUPPORTED.**

§6.1: "Comparing Hom-Mix Strong with Het-Mix D indicates that diversity provides modest but consistent gains in stability and accuracy when strong reasoners are present. By contrast, when all agents are weak (Hom-Mix Weak), changing order, depth, or confidence visibility yields negligible benefit ... while diversity provides modest gains, it cannot make up for a team composed entirely of weak agents."
- One precision note: the paper says "**modest** but consistent gains." The claim says "consistent gains" and drops "modest." Minor — the conditional structure (only-with-strong-reasoners) is exactly right.

### Claim 4 — "Procedural knobs (confidence visibility, debate order, +rounds 1->2) had negligible/insignificant effects; initial accuracy and team size were the strongest predictors."
**Verdict: SUPPORTED.**

- Strongest predictors: §6.1 regression (R²=0.393) — initial smooth accuracy is "the most influential predictor" (β=0.600, p<0.001); number of agents "significant positive effect" (p<0.001). Matches "initial accuracy and team size were the strongest predictors."
- Procedural knobs negligible: §6.1 — "Debate depth, confidence visibility, and debate order remain insignificant." §7 — "structural factors such as team size, debate depth, or confidence visibility exert only limited influence."
- CAVEAT/internal tension: the claim lumps **team size** in with "strongest predictors" (correct) but the paper ALSO lists "team size" among the "structural factors [that] exert only limited influence" in the §7 Discussion. The regression treats number-of-agents as a significant positive predictor while the composition experiments frame team size as limited-influence. The claim picked the regression framing for team size — defensible, but the paper is not perfectly internally consistent on team size, so the claim's confident "team size = strongest predictor" slightly over-resolves a tension the paper leaves open. "+rounds 1->2" maps to "debate depth," which is insignificant — supported.

### Claim 5 — "When agents share similar training/biases, debate reinforces incorrect beliefs (echo chambers, premature consensus) rather than challenging them."
**Verdict: OVERSTATED — provenance problem.**

The "shared training/biases → reinforce incorrect beliefs / echo chambers" statement appears in the paper's **Introduction as cited prior-work motivation, NOT as this paper's own finding.** §1: "bias amplification and echo chambers are concerns (oh2025understanding; estornell2024multi): when agents share similar training or biases, debates can reinforce incorrect beliefs rather than challenge them (liu2025breaking)." That is the authors describing the literature's concern that motivates their study, attributed to other papers (Oh 2025, Estornell 2024, Liu 2025).

What THIS paper's own results support is the adjacent but distinct finding: "weaker teams often converge prematurely or follow persuasive yet unsound reasoning" (§7) and the majority-pressure suppression result (claim 2). "Premature consensus" is genuinely the paper's finding; the specific "shared training/biases cause echo chambers" causal mechanism is **borrowed framing**, not demonstrated here (the study varies model composition but does not isolate "shared training" as a tested variable producing echo chambers).

If the claim is presented as "the paper found X," it is OVERSTATED — attribute the echo-chamber/shared-bias mechanism to the cited prior work, and attribute "premature consensus in weak teams" to this paper.

## Summary table
| # | Verdict | Headline reason |
|---|---------|-----------------|
| 1 | SUPPORTED | Boundedness verbatim; "improves accuracy" is softer/more-qualified in paper than claim implies |
| 2 | SUPPORTED | Stats exact (34.4% / 30.0% / 3.6%); 3.6% is mix_A-conditional — keep the qualifier |
| 3 | SUPPORTED | Conditional exact; paper says "modest" gains, claim dropped "modest" |
| 4 | SUPPORTED | Insignificance + top predictors confirmed; team-size framing has a mild internal tension |
| 5 | OVERSTATED | Echo-chamber/shared-bias mechanism is cited prior-work motivation, not this paper's result |
