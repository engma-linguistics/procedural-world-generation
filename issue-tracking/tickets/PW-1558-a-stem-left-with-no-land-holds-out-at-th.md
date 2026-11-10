---
id: PW-1558
title: A stem left with no land holds out at the world's best cell; that hidden jump is what gives leonins, goblins, hobgoblins and halflings their room on af2677
type: task
status: in-progress
parent: null
milestone: v5
subsystem: peoples
effort: m
impact: high
found_by: lane228
blocked_by: []
relates: [PW-1184, PW-1152, PW-1181, PW-1182]
refs: ["planet/lineages/history/dispersal.py::_hold_out", "planet/lineages/history/origins.py::_origin_split", "planet/lineages/history/origins.py::_take", "planet/lineages/history/model.py::_advance", tools/peoples_robust.py, docs/review/peoples/origins-spread.md, "planet/lineages/history/origins.py::_founders_room", "planet/lineages/history/dispersal.py::_refuge_cell", "branch lane269b (lane 269 suite and probes; scratch outputs deleted)", "lane 228 numbers: exports/lane228/ in the lane worktree (after/, base2/)", "world af2677 (time zoom f2201f)"]
created: 2026-11-08
updated: 2026-11-10
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
- [x] no stem refuge lands further than ~20 x FOUNDER_KM from its last land; no dnd land people under 0.5 Mkm2 in any robustness-suite run
  (owner D72 C, 2026-11-10; drow and troglodytes stay known problems, see inbox draft-troglodytes-extinct-every-dnd-run-af2677). Evidence:
  docs/review/peoples/origins-spread.md (suite vs main fdb11199, mechanism G: every dnd land people at 0.50 or above). Re-check pending after
  merging main (it touched planet/lineages/); the 22-run suite was not re-run in the merge lane.

## Updates
- 2026-11-10: Status needs-decision -> in-progress. Owner D72 = C (11-10): bar is no dnd land people under 0.5 Mkm2 in any robustness-suite run; drow/troglodytes known problems; demography test rewritten to a density comparison. Lane 269f merging lane269b.
- 2026-11-10: Status todo -> needs-decision. D72 on the desk (11-10): lanes 269-269e evidence (vs main fdb11199): founding-patch fix cuts dnd under-1 runs 29 → 9, all dnd land peoples ≥ 0.50; floor-at-birth arm 8, changes all Seven Meals runs. Options A birth rule / B keep 1 with exceptions / C bar at 0.5 (lean). Branch lane269b f8157b07 (card text in its inbox draft).
- 2026-11-10: Lane 269/269b (branch lane269b, not merged): a land split whose landmass lacks a founders' country of its habitat is founded at the nearest free country (`_founders_room`, `_refuge_cell`, reach now checked in km). Full suite vs main 673436c0 (af2677, arm now, 22 runs): the islet stranding is gone (tabaxi median 0.12 -> 8.1 Mkm2, hobgoblin min 0.14 -> 24.6, leonin min 0.11 -> 0.51, halfling min 0.05 -> 0.46); dnd brittle 7 -> 5, worst swing 2,210x -> 110x; Seven Meals identical; picks <= 7,911 km. **Floor not met**: leonin (dnd-j2 0.51) and halflings (4 runs, 0.46-0.54) still under 1 Mkm2, and goliaths now under 1 in 17 of 22 runs (main 5), firbolgs in 3 (main 0). Diagnosis (docs/review/peoples/origins-spread.md, "Why the rest fall short"): those are founded on a crowded 20 Mkm2 continent, not islets, and sit at the history's own loser floor of ~0.5 Mkm2 (PW-1182); no landmass room count at founding separates them from splits that thrive. D71's 1 Mkm2 needs PW-1182's mechanism (or a ruling on that floor); the goliath regression must be fixed before this branch merges.
- 2026-11-10: Owner D71 (11-10): bar is now a 1 Mkm2 floor in every suite run (not main's median). Lane 233 left a couple of nudged runs at ~0.1 Mkm2 (leonin, halfling): those are what's left. Queued after lane 266 (which touches demes MIN_CELLS).
- 2026-11-09: Lane 233 (12f38974) merged: refuge within LAST_LAND_REACH x FOUNDER_KM (8,000 km) of the last land, in a free country at least one founders' country in size; refuge distance median 9,795 -> 1,876-3,280 km; jitter brittle 9 -> 4; leonin swing 998 -> 84. Range bar (measured against the teleport) not met; asked on the desk (D71).
- 2026-11-08: Created from inbox draft draft-stem-refuge-teleport-carries-peoples.md (found by lane228).
