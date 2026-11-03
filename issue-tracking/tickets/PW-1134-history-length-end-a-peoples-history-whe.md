---
id: PW-1134
title: "History length: end a peoples history when cultures are mostly where they need to be, not after a fixed span?"
type: task
status: needs-decision
parent: PW-675
milestone: null
subsystem: culture
effort: m
impact: med
found_by: fun-lane-69
blocked_by: []
relates: [PW-675, PW-1122, PW-1124]
refs: [planet/lineages/techtree.py, planet/lineages/history/, docs/references/tech-catalogue/]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words: today every peoples history runs to the same present. The owner (10-30) suggested the history could instead stop
at the natural point where the cultures are mostly where they need to be: the food ways, crafts and towns the culinary
ethnography needs are in place. This draft only lays out the options; nothing was built (it touches the history runner, which
the tech tree only reads after the fact).

What the tech tree shows now (fun lane 69, 4 D&D runs x 2 draws, 547 techs): world firsts land near Earth's dates (farming
~12.5 kyr from the history's tamings, copper ~6.3, writing ~5.6, cities ~6.4 kyr ago). The average living people knows ~250 of
547 techs at the present, the best ~520. So by "the present" the leading peoples are at the late-medieval end of the tree and
others are far behind, which is what a fixed span gives.

Options:
- A: keep the fixed span (simplest; the era cap, meta.era, already stops the tree at the renaissance).
- B: stop when a target share of the living peoples (say half) know a target set of techs (for the food goal: cultivation or
  herding, boiling pots, salting or smoking, fermentation; or towns), plus a margin of a few kyr. The history would need to
  build the tech tree as it runs (it builds it after the fact today) or check a cheap proxy (the tamings and settlement tiers
  it already has).
- C: stop when the leading people reaches an era (e.g. classical or medieval), then let the others catch up for a fixed
  margin. Simple to test, but the tree's speed then sets the history's length.
- D: run the fixed span, but pick the "present" afterwards: the earliest stored moment that meets B's test. No change to the
  runner, only to which frame the briefs and the viewer call "now". Cheapest to try.

Lean: D first (it costs no simulation change and shows whether the stopping test is meaningful), B if it is.

## Updates
- 2026-10-30: Owner 10-30 D13: D first (pick the present afterwards); if nobody has crossed the finish line, extend the span instead.
- 2026-10-30: Created from inbox draft draft-history-ends-when-cultures-settle.md (found by fun-lane-69).
