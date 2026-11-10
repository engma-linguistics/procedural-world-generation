---
id: PW-1629
title: The zoom's tide-dominated delta cuts 4 mouths or 3 depending on a 4% change in the river's size
type: task
status: done
parent: null
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: lane263
blocked_by: []
relates: [PW-1043]
refs: ["planet/zoom/stage_landscape.py::drainage_tools", "planet/zoom/regional.py::_deltas", "planet/zoom/regional.py::_count_mouths", docs/review/pw1629/sweep.txt, docs/review/pw1629/delta_sweep.py, "tests/test_coast.py::test_delta_types_differ", "tests/test_coast.py::three_deltas", "tests/test_coast.py::_measures", "tests/test_zoom_water.py::water_world", planet/zoom/, "scratch: lane 263 delta.py (gone)"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: the zoom builds three deltas on one test river (river-, wave- and tide-dominated seas), and the test
asks the tide-dominated one for at least 4 mouths and at least 2 more than the wave-dominated one. Lane 263 (PW-1043, true
cell areas) made the same rain give a 4.4% bigger river there. Baseline: the same fixture (1200 mm of rain, L5) on main
a866c5ad gives 46,393 m3/s; on the PW-1043 branch it gives 48,457 m3/s.

| | river q m3/s | tide: mouths, rough, sea_near | wave: mouths, rough |
|---|---|---|---|
| main a866c5ad | 46,393 | 4, 4.29, 0.41 | 2, 0.84 |
| PW-1043 branch, same rain | 48,457 | 3, 4.52, 0.43 | 2, 0.67 |

Every other measure keeps its type and margin, but the tide mouths go from 4 to 3, so the test fails. To keep the
test as it was, lane 263 set the fixture's rain to 1149 mm (`test_zoom_water.water_world`), which gives the river its
old 46,400 m3/s. The assertion was not touched.

What breaks if never done: one count on one fixture decides the test, so any change that nudges this river by a few
percent fails it, or passes it by luck, and the next lane will tune the fixture again. The real question is whether
the zoom's tidal channel count jumps with discharge (and whether 3 or 4 mouths at ~47,000 m3/s is the honest answer).

What to try: build the tide delta at several discharges (e.g. 42-52k m3/s in 2k steps, re-rolled zoom seeds) and see
whether the mouth count is smooth or flips. If it flips, judge the test on the median over a few draws or a measure
that doesn't jump (sea_near, rough). Then put the fixture's rain back to 1200.
- [ ] the tide-delta test passes with the river anywhere in 44-50k m3/s, or the test states the band it holds for

## Updates
- 2026-11-10: Status todo -> done. Lane 268b: fixed as a mechanism in the zoom's distributary layout (planet/zoom/stage_landscape.py::drainage_tools make_branches); fixture rain back to 1200 mm (48,457 m3/s), assertion untouched.
  Diagnosis (sweep: the test fixture at 1050-1300 mm = 42,399-52,495 m3/s in 25 mm steps, zoom seeds 1-5, tide/wave seas; harness and both tables in docs/review/pw1629/): lane 268's reading-the-code guess was wrong. The target count nb is 8 at every discharge in the band (_deltas' two roundings never flip here), and _count_mouths' 5% threshold never bit either. What varied was how many of the 8 funnel heads the binary split tree (grow) happened to reach: before the fix (merge commit 2b4e94db, the zoom's delta code as on main 1090b13f) the tide delta cut 1-7 mouths, median 3, below 4 on 32 of 55 builds, by zoom seed as much as by discharge (seed 1, the test's: 3,4,6,4,4,2,3,3,3,3,3 across the band). Two causes: (1) a branch laid while its parent split was still unlinked (ov[s] was set only after all its children) could join its own ancestors' channel, which walk's joins() could not see, and loop back; the whole-delta loop check then took every distributary away (8 of 55 builds: 1 mouth, no apex); (2) funnel heads the tree didn't reach got no channel (the 'own branch' fallback served fingers only), and when it did, a fallback took 1/goals of a possibly small branch's water.
  Fix: link the split to each child while it grows on (joins() now sees the ancestors; no build on the sweep lost its distributaries); every unreached goal, finger or funnel, gets its own branch, off the nearest channel carrying at least twice its share (within 0.5 R of the nearest channel at all), taking 1/goals of the river (not of that channel), capped at half the channel. After: tide 4-8 mouths, median 6, 0 of 55 below 4 (seed 1: 7,7,6,7,7,4,6,6,6,6,6); wave 2 on all 55; river 4 on all 55 (types, rough and sea_near unchanged in kind). So the count now follows nb (Galloway weights and discharge) less what the ground blocks, not the split tree's luck.
- 2026-11-10: Created from inbox draft draft-tide-delta-mouth-count-brittle.md (found by lane263).
