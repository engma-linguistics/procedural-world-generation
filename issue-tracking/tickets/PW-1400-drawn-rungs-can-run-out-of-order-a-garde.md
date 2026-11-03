---
id: PW-1400
title: Drawn rungs can run out of order (a gardener denser than a bronze-age plough farmer)
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: peoples
effort: s
impact: low
found_by: lane 145
blocked_by: []
relates: [PW-1383, PW-1275]
refs: [planet/lineages/ranges.py, planet/lineages/ladder.py, docs/review/peoples/ranges/round1.md, tools/peoples_robust.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: with `meta.draw_ranges` on, the gardening number (published 2-20) and the bronze-age plough number (2.5-14) are drawn
separately. Seed 13 draws gardeners 12.7 and bronze ploughmen 6.9, so a people that takes up the plough loses density at that step. The
three plough stages are drawn together and stay in order, but gardening is not tied to them. The published ranges overlap, so a
real world could be either way; the question is whether the model should allow it.

Options:
- A. Leave it (the sources overlap; the plough's gain shows in the later stages and in the irrigation rung). Lean A: it only appears
  with the setting on, and the owner asked for the sources' ranges as they stand.
- B. Draw gardening and the bronze plough from one shared position in their ranges, as the plough stages share one.
- C. After drawing, raise the bronze plough to at least the gardening number.

Check on the robust suite (3 seeds x 2 worlds, ranges/round1.md) whether any people's density falls when it takes the plough.

## Updates
- 2026-11-03: Created from inbox draft draft-ranges-rung-order-under-draws.md (found by lane 145).
