---
title: Necking-zone margins (neck_km, rise) soften the margin cliff; judge them over a second roll before switching them on
type: task
status: todo
parent: null
milestone: v2
subsystem: tectonics
effort: m
impact: med
found_by: lane100
blocked_by: []
relates: [PW-950]
refs: [planet/tectonics/crust.py, planet/surface.py, docs/review/tectonics/margin/report.md, docs/review/tectonics/margin/diagnosis.md]
---

## Description
In plain words: lane 100 made rifts stretch the edge of the continent before the ocean opens (a necking zone) and
made sediment settle at the foot of the slope. It is on the lane's branch but switched off, because a short climate
check showed 3 of 11 worlds dipping below 100 ppm CO2 for a while, against none without it. That could be chance.
Running the same check again with fresh draws says which.

What is on the branch (both off by default, so main's outputs are unchanged): `crust.necking` (param `neck_km`, km of
necking zone; lane 100 tried 200) and the continental-rise rule in `surface._offshore` (param `rise`, 0/1).
Screens (docs/review/tectonics/margin/report.md, L6 seeds 1-3, 600-1000 Myr): coast cells with >3 km of water in the next
cell 23% -> 15% (Earth on L6 3.5%), 200-3000 m share of the ocean 12.3% -> 14.7% (Earth 19.6%), coast-to-3000 m
~250 -> ~300 km (Earth 600); L7 seed 1: 20% -> 9% and 8.0% -> 10.1%; land % falls 0.4 points at L6 (paired judge,
moved) and 3.4 points on the one L7 seed. Paired judge (v1-finish-16 draws, roll 0.0005, 11 of 18 draws per arm):
soft pass 9/11 -> 10/11; frozen, boiled, ocean loss 0 in both; CO2 crash (pCO2 < 100 ppm after 300 Myr, lane 92's
working definition) 0/11 -> 3/11 (minima 85, 69, 82 ppm, all recovering to 122-249 ppm by the end). The source and sink
references don't move, and no direct mechanism is known (the new-floor count feeding the CO2 source is unchanged).

What to do: run both arms (`base` = main, `on` = neck_km=200, rise=1 as defaults) over all 18 draws at rolls 0.0005 and
0.001 (docs/review/base-climate/v1-finish-16/paired.sh), tally with docs/review/v1-cut/tally.py. If the CO2 crash count
stays above main's, find the mechanism before switching on; if not, switch both on and update the goldens. Best done
together with the foreset-slope draft (draft-clinoform-front-has-no-foreset-slope), since the shelf front is what still
makes the cliff.
- [ ] CO2 crash count not above main's over two rolls, with the other hard bars still at 0
- [ ] soft pass count not lower than main's

## Update (lane 100c, 2026-11-01)
Lane 100c ran the full 18x2 paired L6 judge with necking + rise + sea-floor creep (`neck_km=200 rise=1 slope_k=1000`)
against main (docs/review/tectonics/margin/report.md, round 3). CO2 crash (below the plants' compensation point,
tools/hard_bar.py): 0/36 in both arms. The secondary pCO2 < 100 ppm count: 3/36 main, 6/36 on; one draw went under
60 ppm. Frozen, boiled and ocean loss: 0 in both. Soft pass: 29/36 main, 26/36 on (McNemar p 0.55). Late dT -2.2 C and
land -2.9 points, both moved. The judge can't tell necking's share of this from the creep's: see
draft-sea-creep-alone-judge.
