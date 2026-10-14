---
id: PW-010
title: "Zoom synthesis batch 1: great escarpment, caprock plateau/cuestas, lava plateau"
type: story
status: done
parent: PW-005
subsystem: zoom
effort: l
impact: high
found_by: daniel
blocked_by: [PW-009]
relates: [PW-021]
refs: [planet/zoom.py, docs/review/falls/, "plan_next@bdc967f: Known issues → Highlights"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Synthesise terrain for the first classes, so the land itself steps up into a plateau above the
escarpment and waterfalls emerge where rivers cross the scarp.

Merged known issues this should fix:
- **Falls are scaled down to fit under the coarse ground (`falls2`):** median fit 0.34; only 2 of 47
  reaches keep full height. Big rivers show ~50–150 m falls; only steep mountain fronts keep 250–550 m.
  Full heights need the land to step up into a plateau above each fall.
- **The escarpment shows only as the fall and gorge**, not as stepped country; the 1-px gorge is hidden
  under the preview's wide river line.

## Updates
- 2026-10-14: Status todo -> done. zoomland1: planet/zoom_landforms.py class dispatch (SYNTH: target/relief/strata hooks, smooth class weights); escarpment (scarp at e*, lowland, re-entrants; designed falls take the scarp), caprock (benches, mesas; cuestas with dip), lava plateau (stepped valley walls). 800c99, 11 zooms: falls >=30 m 44->154, >=100 m 16->77; escarpment designed lips 28->178 / 107->271 m class; cell-mean rms within ~1 m (caprock +7 m). Demo zooms b2165d 366f51 6a4870 9e2ba9 2bd5d8 3bdcbb 041c03; docs/review/landforms/zoom_*.
- 2026-10-14: Created from the landform-classes epic; merged two falls known issues (falls2: falls scaled to fit under coarse ground; falls: escarpment shows only as fall and gorge).
