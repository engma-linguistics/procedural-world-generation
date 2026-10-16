---
title: "World soils: a coastal or hill-side cell's slope counts the drop to its steepest neighbour, sea floor included"
type: task
status: todo
parent: PW-184
subsystem: surface
effort: s
impact: med
found_by: zoom-soils
blocked_by: []
relates: [PW-185, PW-331, PW-330]
refs: [planet/soils.py, planet/vegetation.py, tools/zoom_soil_check.py, "world bc049f (keyframe a1d3b9 @ 1000 Myr, not kept)"]
---

## Description
`soils.mineral` takes each cell's slope as `vegetation.relief(grid, elev) / spacing`: the height difference to the
steepest neighbour, sea cells included. A delta or coastal lowland cell at 5 m beside a 300 m deep shelf cell reads
~5.5 m/km, as steep as hill country, so it erodes like hills (E ~ slope^2) and gets young brown or thin soils instead
of old or alluvial ones. Seen in the zoom soil checks (PW-331, `tools/zoom_soil_check.py`): on 400 km zooms of two L7
worlds the cells beside the sea agree with their own pixels' soil group on only 3-65% of the pixels (river mouths at
-1.4,-108.4 on a seed-21 keyframe world and -11.6,-20.8 on showcase run a1d3b9 @ 1000 Myr: coarse cells thin or young
brown, their flat pixels red tropical and alluvium); a lowland cell beside a plateau has the same problem on land
(cells at 15 m next to 430 m read 6.8 m/km).

Try: the slope to land neighbours only, with the sea counted at sea level (`relief(grid, np.maximum(elev, 0))`), or the
mean rather than the maximum drop to the neighbours. It moves world soils (and the Earth check, PW-330: re-run
`tools/soil_check.py`); vegetation's `flooded()` uses the same relief for its flat share and may want the same fix.
- [ ] coastal lowland cells no longer read steep; soil_check re-run and numbers in docs/overview.md section 2.21
