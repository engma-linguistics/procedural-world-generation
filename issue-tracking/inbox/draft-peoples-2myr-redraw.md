---
title: Do the peoples' numbers shift on a 2 Myr time zoom? Compare over re-rolled tries
type: task
status: todo
parent: null
milestone: v1.0
subsystem: peoples
effort: m
impact: med
found_by: lane280
blocked_by: []
relates: [PW-1661]
refs: [docs/review/timezoom/two-myr.md, planet/lineages/history/steps.py, planet/timezoom/cycle.py, tools/peoples_robust.py, "run 0b3439 (December A)", "scratch runs b74691 and 580f8c (lane 280, deleted after measuring)"]
---

## Description
In plain words: v1.0's time zoom is now 2 Myr (PW-1661), so the peoples' history gets twice the detailed ice-age climate.
On one world and one try each, the peoples at the present came out quite differently on the 2 Myr zoom than on the 1 Myr
zoom (same code, same world December A, dnd tree): 908 M people against 571 M (+59%), dwarves 80 M -> 5 M, kobolds
5.4 M -> 0.6 M, halflings 15 M -> 117 M, humans 103 M -> 53 M. No line appeared late and the same 42 lived, but one try per
arm cannot tell the span's effect from the try-to-try swing, and the two zooms' presents differ in climate (the zooms part
from their first frames: `timezoom.cycle.Index` takes its sunshine thresholds as percentiles over the whole span).
If never done: v1.0's peoples numbers may carry a bias from the longer glacial window (more glacial-epoch steps from
1-2 Myr ago, with hunts, goods and crossings on) that nobody has measured.

What to try: 3-4 tries each (or `tools/peoples_robust.py`-style draws) on a 1 Myr and a 2 Myr zoom of the same L6/L7
moment, and compare each people's share and the total over the draws; if the 2 Myr arm is outside the 1 Myr arm's spread,
look at what the glacial epoch adds from 1-2 Myr ago (tabaxi, giantkin, the sapiens nodes of the hominid, goblinoid,
feline and avian stems).
- [ ] per-people share and total people, 1 Myr vs 2 Myr, over >= 3 draws each, same code
- [ ] a verdict: inside the draw spread, or a named mechanism to fix
