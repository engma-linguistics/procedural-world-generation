---
title: How much land does a person clear? Land-per-person constants and the farming densities behind the cleared shares
type: task
status: needs-decision
parent: PW-103
milestone: v2
subsystem: surface
effort: s
impact: low
found_by: anthro
blocked_by: []
relates: [PW-662, PW-650]
refs: [planet/lineages/landuse.py, "run 8bac4d", "run c646ea"]
---

## Description
PW-662's overlay turns people per km² (presence x density x area, split by way of life from the [[use]] table) into land cover with Earth-pre-industrial land-per-person constants (`landuse.CROP_KM2` 0.007, `HERD_KM2` 0.15, `MEADOW_KM2` 0.01, `BURN_KM2` 0.10, `WOOD_BASE_KM2` 0.003, `WOOD_USE_KM2` 0.03). They are a plausibility anchor, not a fit.

What the first numbers say (see docs/proposals/lineages.md, "Peoples change the land"): the showcase worlds hold ~330-360 M people (about Earth in 1000 AD) on 170-190 Mkm² of land, so cropland comes out at ~1-2% of the land and pasture below Earth's, with the densest cells at only ~20 people/km² (humans 10, halflings 12, farmers 12 per km² of full habitat). Earth's farmed river plains and lowlands reached 30-100 people/km² before industry. So clearing is population-limited: it follows from the `density` knobs the owner set, not from the land constants.

Options:
- A (lean): leave as is. The overlay shows where peoples live and farm; the cleared share rises if the farming densities do.
- B: raise farming densities on prime land (e.g. a `density` bonus for `agricultural` peoples on class 3-4 farmland: intensification) so a few lowlands reach 40-60 /km² while the world total stays near today's. That changes the peoples' numbers and the spread; a PW-650 knob, and the owner's call.
- C: make the constants planet-relative (scaled to the world's own best farmland yield, as `land.goods` does for goods) instead of Earth-shaped.
