---
id: PW-1679
title: Fine zooms write 48 layers where their parent has 71, so the game and human-use overlays are blank on every zoom rung
type: task
status: done
parent: PW-1198
milestone: v1.0
subsystem: zoom
effort: m
impact: med
found_by: lane284
blocked_by: []
relates: [PW-1675, PW-1299, PW-516, PW-485]
refs: [docs/review/zoom/lod-rungs.md, "planet/zoom/fine.py::build", "planet/zoom/fine.py::save", "planet/zoom/regional.py::build", planet/humanuse.py, "zoom 2a4463", "zoom 44d6d6", "zoom 80880d", "zoom 61b06a", "zoom 0ce324", docs/proposals/nested_fine_zoom.md]
created: 2026-11-10
updated: 2026-11-10
---

## Description
**In plain words.** In the level-of-detail flow (section -> 500 km rung -> 30 km rung) every rung is made by the fine pass. It
writes 48 layers; the section it hangs from, and a regional zoom of the same size, have 71. Open a rung in the viewer and
the terrain, rivers, vegetation and satellite view are all there, but the 25 layers the owner's end goal (who eats what, where
people live and move) needs are empty or absent.

Measured by lane 284 (`docs/review/zoom/lod-rungs.md`): zoom 44d6d6 (rung 1, fine pass of 2a4463) has 48 layers, regional zoom
80880d of the same spot has 71. Missing on the fine zoom: barrier_island, building, coast_type, fertile, fertile_score,
fire_months, foraging, fresh_km, fresh_water, fuel, glacial_form, grazing, green_months, harbour, hazards, mud_months,
nav_hazard, pass, pass_height, river_nav, shore_form, sightline, spring, timber, travel. (The scratch zooms are deleted; rebuild
with `planet zoom 2a4463 --lat 35.36 --lon 135.52 --size-km 500 --res-km 0.5` against a copy of dba204's data.)

What breaks if never done: a person who zooms down to a 30 km or 500 km piece sees blank fuel, forage, grazing, timber, travel
and fertility overlays that the section above it shows, and anything reading those layers from a rung (the consumer repo
included) finds nothing. What to try: compute the human-use and game layers on the fine zoom from its own finer ground and water
(as `regional.build`'s last stages do), or at least carry the parent's value down by interpolation for the ones that do not
depend on fine detail (fertile, fuel, timber, grazing, foraging, hazards) and recompute the ones that do (pass, sightline,
travel, river_nav, harbour, shore_form, coast_type, glacial_form).
- [ ] a 500 km rung and a 30 km rung have all 71 layers the section has
- [ ] the viewer's layer list draws each of them on a rung without an error
- [ ] fine-zoom build time and RAM stay under ~2x the measured 34-53 s / 8-12 GB

## Updates
- 2026-11-10: Status todo -> done. Lane 285 merged (5d130c4f): fine zooms write 73 layers (71 + floor_m, valley_floor); docs/review/zoom/fine-layers.md.
- 2026-11-10: Created from inbox draft draft-fine-zoom-missing-layers.md (found by lane284).
