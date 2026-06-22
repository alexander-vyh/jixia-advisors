## Findings

# `/advise-full` Interaction Flow Design

**Author:** UX Researcher agent  
**Date:** 2026-06-22  
**Scope:** Turn-by-turn interaction flow — friction, cognitive load, decision architecture  
**Not in scope:** Visual/typographic styling (separate agent); information structure/content layout (separate agent)

---

## Core Design Principles (derived from the UX role brief + research)

1. **Pull, not push.** The menu should answer "what would you change?" not force the user to read a wall of options first.
2. **Default is the answer.** The classifier's pre-selected choice must be visible immediately and actionable in ONE reply.
3. **Progressive disclosure.** Complexity appears only when the user reaches for it — not as a tax on users who don't want it.
4. **Dissenter is structural, not optional.** The research is clear: the devil's advocate / counter-lens is the load-bearing element of accurate deliberation. It must be surfaced as a named, visible component — not buried in a roster list.
5. **Two-round max on debate modes.** The research shows iterative debate degrades past round 2 (S1, S3, S4). The flow must not expose "more rounds" as an upgrade path — it signals the wrong thing.

---

## The Three Entry Points to Understand

Before the flow: the user's mental model of "why am I typing `/advise-full` instead of `/advise`?"

| User's intent | Right path |
|---|---|
| "Just handle it" | `/advise` (not this skill) |
| "I trust the recommendation but want to see what it picked" | `/advise-full` — should reach GO in 1 reply |
| "I want a different convening structure" | `/advise-full` — override MODEL only |
| "I want different advisors for this specific question" | `/advise-full` — override ROSTER or AGENTS |
| "I have no idea, just pick something" | `/advise-full` — vague path → redirect to default + go |

The flow must serve all five without penalizing the first three with the complexity of the last two.

---

## Recommended Flow

### Turn 0 — Skill Entry

The user types `/advise-full [optional: their question text]`.

If the question text is present, the classifier has already run. If absent, the first turn IS the question collection — but that is upstream of this design.

Assuming question is in hand:

---

### Turn 1 — The One-Screen Offer (THE critical turn)

The model emits ONE block of text with this structure:

```
I'll run [SEVEN SAGES / areopagus / jixia / ...] with [modern / historical] advisors.
Dissenter: [name or role] will hold the counter-lens.

Ready? Hit enter to go — or tell me what to change:
  model / roster / advisors
```

**Design decisions in Turn 1:**

- **Three lines of state, one prompt.** The user sees what was chosen without reading a menu. Total reading load: ~15 words of actual content.
- **The dissenter is explicitly named.** Not "a devil's advocate exists" — the named dissenter role is surfaced. This makes the research-backed structure visible and builds trust in the deliberation quality. It also signals: "this is not a naive consensus machine."
- **The call to action is one keystroke.** Enter / affirmative reply = GO. No forced choices.
- **Override is invited, not gatekept.** The three override targets (model / roster / advisors) are named as words, not menus. The user types what they want to change; the model handles disambiguation.
- **No model list, no roster list, no agent list up front.** These appear only if the user asks for them.

**What Turn 1 does NOT show:**
- The full list of six convening models
- The roster of advisor names
- Round counts, synthesis method, or any operational detail
- Explanations of what each model does

That information is available on request but costs zero attention by default.

---

### Happy Path: User Accepts Default

**User reply:** enter / "go" / "yes" / "looks good" / [blank]

**Model action:** Start the advise run immediately. No confirmation, no recap.

**Total turns to GO:** 1  
**Total reading required:** ~15 words  
**Cognitive load:** minimal — the user recognized the structure and made one non-decision

---

### Override Path A: User Changes the Convening Model

**User reply:** "use areopagus" / "try the junto" / "what models are available?"

**Model action (for "use areopagus"):**
```
Switching to Areopagus. [Updated dissenter display if different.]
Ready? Enter to go — or change roster / advisors.
```

One confirmation, same one-line prompt, same one-keystroke GO.

**Model action (for "what models are available?"):**
```
Six options:
  jixia — parallel independent + synthesis (current default)
  seven-sages — ...
  areopagus — structured verdict with dissenter
  junto — socratic rounds
  parishad — ...
  yushitai — ...

Pick one, or enter to go with jixia.
```

After their pick, return to the one-line offer format with updated state.

**Cognitive load note:** The list of six is a 6-line table-like display. It is not a wall of text because each model name is ONE descriptor, not a paragraph. The user is scanning, not reading.

**Deliberate omission:** Do NOT show round counts or debate depth options. The research (S1, S3, S4) strongly cautions against iterative multi-round debate. Exposing "rounds: 2, 3, 4?" as a knob trains the wrong mental model and tempts the user toward the topology most likely to produce sycophantic drift.

---

### Override Path B: User Changes the Roster

**User reply:** "use historical advisors" / "switch to historical" / "I want modern executives"

**Model action:**
```
Switching to historical representatives. Dissenter: [updated name].
Ready? Enter to go — or change model / advisors.
```

One line updated, same one-keystroke GO.

If the user asks "what's the difference?":
```
Modern: current-day practitioners and executives (relevant lived context)
Historical: institutional representatives across eras (broader epistemic range,
            harder to pin down contemporary relevance)

Tip: historical rosters tend to surface longer-horizon considerations.
Enter to keep modern, or say "historical" to switch.
```

Short, non-judgmental, actionable. The tip is a nudge toward the research-backed use case, not a mandate.

---

### Override Path C: User Picks Specific Advisors

**User reply:** "I want specific advisors" / "show me who's in the roster" / "can I pick?"

**Model action:**
```
Current roster (modern):
  [Name] — [one-line role]
  [Name] — [one-line role]
  [Name] (dissenter) — [one-line role]
  ...

Remove or add by name, or enter to go as-is.
```

Display: roster as a short vertical list, dissenter marked explicitly. The user can say "remove X" or "add someone who focuses on Y."

**Cognitive load note:** This is the highest-friction override path — it's the one where the user genuinely wants to curate. It's also the least common. Putting this behind "I want specific advisors" rather than surfacing it by default is the key load-reduction move.

---

### Vague User Path: "Just Pick Something Good"

**User reply (at the question stage):** "just pick something good" / "you choose" / "I don't know, surprise me"

**Model action:** Do NOT present a menu at all. Respond as if the user had accepted the default:

```
Running with [classifier's pick]. Dissenter: [name] holds the counter-lens.
[Start run.]
```

This is a pull path. The user explicitly opted out of the decision. Honoring that means skipping even Turn 1's one-line offer and just going. The model picked; the dissenter is named so they know the structure; run starts immediately.

**Rationale:** The "just pick" signal is explicit consent to delegate. Presenting a menu anyway breaks the implicit contract of `/advise-full`'s default experience and treats the user's decision as incorrect.

---

## Where Defaults Live

| Element | Default source | Displayed at Turn 1? |
|---|---|---|
| Convening model | Classifier's output | Yes — named explicitly |
| Roster policy | Classifier's output (inferred from question domain) | Yes — named as "modern" or "historical" |
| Specific advisors | Model-determined for chosen convening | NOT shown (behind override path C) |
| Dissenter | Structurally included in all modes | Yes — named as a role |
| Round count | Hard-coded to 2 max; not exposed as a knob | Never shown |
| Synthesis method | Model-determined | Never shown |

**Key design choice:** Round count and synthesis method are deliberately hidden. They are operational details that the research shows users will mis-use (adding rounds adds sycophancy, not depth). Hiding them removes a tempting but harmful knob.

---

## The Three Biggest Cognitive-Load Risks

### Risk 1: The Menu Lands Before The User Knows They Want One

**What goes wrong:** The skill presents all three override dimensions (model + roster + agents) as a structured form on the first turn. The user has to read, parse, and decide before they know if they even want to change anything. Cognitive tax paid before any value received.

**Mitigation (baked into the design):** Turn 1 shows the *conclusion* of the menu (what was chosen), not the menu itself. The menu appears only if the user reaches for it. The first turn's cognitive demand is "do you agree with this?" — one bit of information, not a six-option decision tree.

### Risk 2: The Dissenter Is Invisible Until It Matters

**What goes wrong:** The user gets a panel result without understanding the adversarial structure. They see five advisors agreeing and one dissenting. Without the Turn 1 setup naming the dissenter as structural, the dissent reads as noise or a disruptive agent, not the load-bearing counter-lens the research identifies it as.

**Mitigation:** Name the dissenter explicitly in Turn 1. Not as a caveat — as a feature: "Dissenter: [name] will hold the counter-lens." This primes the user to value the dissent rather than discount it. It is the single most important trust-building move in the flow, and it costs one line of text.

### Risk 3: The "Full" In `/advise-full` Implies Menu Complexity

**What goes wrong:** A user types `/advise-full` expecting a richer experience, then sees a three-line offer. They wonder if the skill loaded correctly. The brevity feels like a bug, not a feature.

**Mitigation:** The one-line offer format must feel *confident*, not sparse. "I'll run X with Y advisors. Dissenter: Z holds the counter-lens. Ready?" reads as a capable system presenting its conclusion, not a system that ran out of things to say. The difference is tone and specificity — naming the model, naming the roster type, naming the dissenter by role. That density of named specifics reads as considered, not truncated.

A secondary mitigation: if the user replies with confusion ("that's it?"), the model should make the expansion explicit: "That's the recommended path. Say 'what models are available?' to see all options, or 'show roster' to pick specific advisors." Reveal the depth on demand; do not preload it.

---

## Anti-Patterns to Avoid

- **Do not show a 6-item model menu on Turn 1.** It is high cognitive load for users who don't need it (the majority).
- **Do not expose round count as a selectable option.** The research is unambiguous: more rounds degrades quality. A "rounds: 2 / 3 / 4" dropdown signals the wrong value proposition.
- **Do not make the dissenter opt-in.** Structural dissent is the research-backed load-bearing element. Making it optional trains users to skip it, reducing deliberation quality. It is always on; the user can name a different dissenter agent, but cannot remove the dissenter role.
- **Do not confirm after confirmation.** After the user says "go," start immediately. An "OK, starting now..." intermediate message is interaction cost with zero value.
- **Do not present the vague-user with a menu.** "Just pick something" is a release; treat it as one.

---

## Summary: The Single-Keystroke Contract

The entire flow is built around one contract: **a user who trusts the classifier reaches GO in one reply.** Every design choice — three-line offer, named defaults, hidden menu, named dissenter — serves this contract. The override paths are real and available but cost nothing to users who don't reach for them.

The dissenter surfaces on Turn 1 because it is structural and trust-building, not because it requires a decision.
