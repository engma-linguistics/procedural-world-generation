---
id: PW-1629
title: The zoom's tide-dominated delta cuts 4 mouths or 3 depending on a 4% change in the river's size
type: task
status: todo
parent: null
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: lane263
blocked_by: []
relates: [PW-1043]
refs: ["tests/test_coast.py::test_delta_types_differ", "tests/test_coast.py::three_deltas", "tests/test_coast.py::_measures", "tests/test_zoom_water.py::water_world", planet/zoom/, "scratch: lane 263 delta.py (gone)"]
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
- 2026-11-10: Created from inbox draft draft-tide-delta-mouth-count-brittle.md (found by lane263).
