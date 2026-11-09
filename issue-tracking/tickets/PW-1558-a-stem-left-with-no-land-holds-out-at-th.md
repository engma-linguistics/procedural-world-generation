---
id: PW-1558
title: A stem left with no land holds out at the world's best cell; that hidden jump is what gives leonins, goblins, hobgoblins and halflings their room on af2677
type: task
status: todo
parent: null
milestone: v5
subsystem: peoples
effort: m
impact: high
found_by: lane228
blocked_by: []
relates: [PW-1184, PW-1152, PW-1181]
refs: ["planet/lineages/history/dispersal.py::_hold_out", "planet/lineages/history/origins.py::_origin_split", "planet/lineages/history/origins.py::_take", "planet/lineages/history/model.py::_advance", tools/peoples_robust.py, docs/review/peoples/origins-spread.md, "lane 228 numbers: exports/lane228/ in the lane worktree (after/, base2/)", "world af2677 (time zoom f2201f)"]
created: 2026-11-08
updated: 2026-11-08
---

## In plain words
When a new people branches off, it takes the land at its birthplace from its parent stem. If the stem was small, that can take all of
it. The stem is then rescued by a "refuge" rule, but the rescue picks the best land anywhere in the world, so the stem silently jumps
to another continent, and its later daughters (leonins, goblins, hobgoblins, halflings) are born there, on empty land. Lane 228 made
the rescue stay near the stem's last land. On world af2677 those four peoples then started squeezed among their neighbours and stayed at
about 0.1 Mkm2 instead of 11-46 Mkm2, and humans took a third of all people. So the jump is wrong but currently load-bearing; the
change was reverted.

## Description
`_hold_out` (dispersal.py) refuges a stem with splits to come when it holds under 3 cells; with no presence at all its search area is
`np.ones` (the whole world), so the refuge lands at argmax K anywhere. A daughter's founding take (`_take`, D20) empties a small stem,
so on af2677 this fires in every dnd run (lane 228: all 7 dnd base/jitter runs changed when the search was limited to the last land).
Lane 228's measured effect of limiting it (af2677, dnd seeds 7 and 10, main -> near-last-land refuge): leonin 27.5 -> 0.11 Mkm2 and
39.7 -> 1.6; goblin 11.4 -> 0.10 and 12.1 -> 0.10; hobgoblin 10.8 -> 0.12 and 45.8 -> 1.6; halfling 0.55 -> 0.03 and 12.0 -> 0.03;
human share 0.002 -> 0.33 and 0.13 -> 0.32. The af2677 jitter brittle count fell 11 -> 7 only because those peoples sat at the share
floor in every run. On 4360a3 only 1 of 12 runs changed.
What to try: keep the refuge near the stem's last land (exp(-d / FOUNDER_KM), as `_origin_fallback` does) but score it by free room
(K less what rivals take, as an arrival's `_rivals_here` pocket), so a squeezed stem holds out at the nearest country it can actually
live in; or let the founding take leave the stem the cells outside the founders' own country. Judge on the suite's af2677 dnd runs.
- [ ] no stem refuge lands further than ~20 x FOUNDER_KM from its last land; leonin/goblin/hobgoblin/halfling ranges on af2677 dnd
  not below main's median

## Updates
- 2026-11-08: Created from inbox draft draft-stem-refuge-teleport-carries-peoples.md (found by lane228).
