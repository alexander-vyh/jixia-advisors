# Problem Framing — advisor-convening-methods-v2

Confirmed with the user, 2026-06-16.

## Problem

The README names historical convening models (`Jixia`, `Seven Sages`,
`Areopagus`, `Junto`, `Parishad`, `Yushitai`), but the repo only has individual
Claude advisor agents. There are no concrete Claude/Codex methods, skills,
commands, or tool calls that let a session invoke those modes consistently, so
the modes remain conceptual and cannot be used, tested, or benchmarked in real
work. The historical representatives behind each convening story are also not
available as method-specific call targets, so the names cannot provide their
own source-grounded voices when that would be useful.

## Why now

The README makes the modes sound available, but they are not callable yet, and
the user wants to actually use them in Claude/Codex sessions instead of leaving
them as conceptual labels. That gap will keep causing confusion until the repo
either builds the methods or narrows the docs.

## Decision authority

The user (alexander-vyh). Solo personal-advisor repo; the user owns the what and
why.

## Behavioral population

Primary: Claude/Codex sessions, because they need a reliable way to invoke a
named convening method and dispatch the right advisor set. Secondary: the user,
because the user needs to choose or request the method at the right moment and
judge whether the output is useful in the moment. The default session
context must not load every historical representative; those representatives
are often irrelevant and should be available only through explicit method calls
or explicit representative selection.

## Riskiest Assumption

(Refined 2026-06-18: the methods are kept regardless of measured payoff — they have
intrinsic/craft value to the owner — so the earlier "earns reuse / better than ad
hoc" framing is dropped. See design.md Riskiest Assumption and Non-Goals.) The risk
is now **craft feasibility**: that the six methods can be made genuinely distinct
and usable rather than six labels over one generic wrapper, and that the three
institutional methods which default to historical reps can have those rep modules
authored into working lenses. Wrong when a method is a generic wrapper, or a
historical-default method has no functional roster. Known from the distinctness
validator + live-output fixtures + a non-empty-default-roster check, not from usage
volume.

## Success criteria

All six README methods (`Jixia`, `Seven Sages`, `Areopagus`, `Junto`,
`Parishad`, `Yushitai`) are callable from Claude/Codex, route to concrete
advisor sets, and produce *distinct* method-shaped synthesis rather than a
generic multi-agent pileup — every method (including the three historical-default
ones) produces a usable result on a real prompt. Each method can also call
source-backed historical representative agents from its own story on demand,
without loading those representatives ambiently. A lightweight invocation log
records which methods get used (curiosity, not a keep/kill gate).
