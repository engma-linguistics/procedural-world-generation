---
title: "Zoom flat high plateaus still 3-5x Earth's relief after PW-1462, and not from the detail amplitude"
type: task
status: todo
parent: null
milestone: later
subsystem: zoom
effort: m
impact: low
found_by: lane-189-pw1462
blocked_by: []
relates: [PW-1462, PW-1446]
refs: [docs/review/tectonics/mountains/lane189.md, docs/review/tectonics/mountains/lane189_measure.py, docs/review/tectonics/mountains/lane189_trial.sh, docs/review/tectonics/mountains/scout2.md, "planet/zoom/regional.py::land_amp", "planet/zoom/stage_terrain.py::ruggedness", "planet/zoom/stage_terrain.py::detail", "planet/zoom/stage_landscape.py::fit_setup", "world 899985"]
---

## Description
In plain words: since PW-1462 the zoom's rough detail follows how rugged the neighbourhood is. Even so, flat high ground in the zooms is still much rougher than on Earth. On world 899985, cells with under 300 m of local relief on its 3 and 5.5 km plateaus have their highest 4 km pixel 440 and 670 m above the cell's mean. Earth's figure for such cells is 130 m. Changing the detail strength (SUBCELL_K 1.2 to 1.8, a third less amplitude) only takes a fifth off that, so most of the excess comes from somewhere else in the zoom. If this is never done, zooms of flat high plateaus show a few hundred metres of hills that the world doesn't have, and their peak heights read 0.3 to 0.5 km high.

Measured by lane 189 (lane189.md §1), 1200 km zooms at 4 km/px, scratch builds now gone (rebuild with lane189_trial.sh):
- Z1 37.5S 143W: flat cells (relief 0-300 m) p75 1,435 m on main before PW-1462, then 685 / 667 / 557 m at K 1.2 / 1.5 / 1.8. Earth 128.
- Z2 37S 176.8E: 854, then 474 / 442 / 384 m. Earth 128.
- The lowland zoom (47.8N 22.1E) is about right: 231 m against 128 for flat cells, 411 against 554 for 300-700 m.

Candidates, cheapest test first: (a) the ruggedness's height term (`ruggedness`: `0.9 × smoothstep(600, 3500, elev)`) sets rug about 0.9 on any high ground. Try the zoom with it off on Z2 and look at the flat cells. (b) The landscape pass's valleys cut into a high plateau, and the mean-keeping lifts the ground between them. Compare the highest pixel against the cell mean before and after the landscape pass. (c) The base surface between cells. Write the diagnosis before any sweep.
- [ ] the source of the flat-plateau excess named with a measurement on Z1/Z2
- [ ] flat high cells within ~2x Earth's 4 km p75, lowlands unchanged
