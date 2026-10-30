---
id: PW-667
title: Feed the peoples' land cover (fields, pasture, burned grass, managed woods) back into the zoom's plants
type: task
status: done
parent: PW-103
milestone: v2
subsystem: zoom
effort: m
impact: low
found_by: anthro
blocked_by: []
relates: [PW-662]
refs: [planet/lineages/landuse.py, planet/zoom_vegetation.py, "run 8bac4d", "run c646ea"]
created: 2026-10-23
updated: 2026-10-29
---

## Description
PW-662's first version derives an anthropogenic overlay per peoples run (`meta.anthro`, layers `anthro_crop`, `anthro_pasture`, `anthro_burned`, `anthro_managed`, `anthro_people`, `anthro_tree_after`: cell fractions at the present, L7 cells) and tints the run's tree-cover view. A regional zoom of the same world still draws wild vegetation under the settled country.

Out of scope for PW-662; what to try: when a regional zoom is made for a world that has a peoples run (or `--peoples RUN`), sample the overlay at the zoom's pixels (cell fractions as the probability of a pixel being cropland, pasture, burned grass or managed wood, with a noise mask so fields form patches along the zoom's rivers and flat ground rather than speckle), then
- cropland pixels: bare field (crop PFT, no trees), the zoom's `fertile` score and flat ground deciding which pixels first;
- pasture and burned grass: trees removed in proportion, grass kept;
- managed woods: canopy thinned (the overlay's THIN of 30%), stand age reset;
- settlement density: a village-sized patch of bare ground near water and passes at a few people per km².
Keep it opt-in, written as a second vegetation layer or a flag on the zoom, so wild-vegetation zooms and their goldens stay as they are.
- [ ] a zoom of a settled region shows fields on flat fertile ground and woods thinned near settlement
- [ ] a zoom made without a peoples run is unchanged

## Updates
- 2026-10-29: Removed docs/review/lineages/anthro-zoom-*.png in cleanup; last present at 9861e2df.
- 2026-10-23: Fix (coordinator, 2026-10-24): fertile_score is stored as a percent and was read as 0..1, so FERT_MIN never applied and fertility swamped the village sites (villages ignored rivers). Now /100; villages are drawn weighted without replacement. Demo zoom 859e74 predates the fix and should be remade.
- 2026-10-23: Status todo -> done. Merged (7219756): planet zoom --peoples RUN; demo zoom 859e74 (1df1c3, run d489d0). Follow-ups PW-672..674.
- 2026-10-23: Created from inbox draft draft-anthro-feedback-zoom-plants.md (found by anthro).
- 2026-10-24: Built as an opt-in overlay (planet/zoom_peoples.py): `planet zoom WORLD --lat --lon [--size-km --res-km] --peoples RUN`. It is a zoom of its own (id carries the run), with a `land_use` layer (wild, cropland, pasture, burned grass, managed woods, settlement), `meta.peoples` and a viewer layer "Peoples' land"; the plants (nu), tree and plant cover, leaf area, npp, canopy height, fire return, vegetation type and biome follow it, and the satellite paints fields in parcels, pasture, burned ground and villages. A zoom without --peoples is byte-identical (checked: layers and pngs of 7e4258 against the base code). Demo zoom 859e74 (world 1df1c3, run d489d0, -36, 104, 1000 km @ 2 km); screenshots docs/review/lineages/anthro-zoom-*.png. Left as drafts: fine zooms, the viewer/API, soils and named types.
