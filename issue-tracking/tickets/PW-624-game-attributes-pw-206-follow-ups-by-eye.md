---
id: PW-624
title: "Game attributes (PW-206) follow-ups: by-eye scales, a fauna placeholder hazard, zoom travel at sea"
type: task
status: todo
parent: PW-184
milestone: later
subsystem: viewer
effort: s
impact: low
found_by: soilveg
blocked_by: []
relates: [PW-206, PW-103, PW-100, PW-649]
refs: [planet/gameattrs.py, viewer/index.html, viewer/zoom.html, "world 607540", "zoom 4f54cb"]
created: 2026-10-23
updated: 2026-11-03
---

## Description
PW-206's game attributes (`planet/gameattrs.py`) are built; what is left from it:
- The scales (travel's terms, the 0-5 saturations: grazing herb NPP / 250 g C, timber biomass / 40 t C/ha, fuel biomass / 30) are set by eye on the Earth world (model climate) and L6 world 607540, so prairie reads x1.2-1.5, temperate forest x2-3, swamp forest x4-5. The model's biomass is low on Earth's model climate (tropical rainforest median 28 t C/ha where Earth has ~150-200), so timber in the tropics reads "fair"; revisit if the vegetation's biomass is recalibrated.
- The "crocodiles" hazard is a placeholder keyed on climate and wet ground (coldest month >= 16 C with swamps, mangroves or a 1000 m3/s river); PW-103's fauna should replace it with the planet's own animals.
- The zoom viewer colours sea pixels on the ramp layers (travel 0 = blue, sightline 0 = dark green): mask them as the globe does.
- The world travel uses a cell's relief as roughness (1 + relief / 1500 m, capped x4), the zoom Tobler's function of the pixel slope; the two are not reconciled (a mountain cell vs its zoom's mean).
- Export: no feature kinds yet (e.g. impassable bog polygons, best timber stands); the layers are rasters only.
- [ ] mask sea in the zoom viewer's game ramps
- [ ] replace the crocodile placeholder when PW-103 lands

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: viewer nicety, not needed for the culinary goal
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-23: polish1 lane: the sea is already masked on the zoom's game ramps. zoom.html's RAMPS branch draws sea pixels with the depth ramp (since ca5fafc), and travel and sightline are RAMPS layers; screenshot docs/review/polish/viewer_368c45_travel_sea_masked.png. The first checkbox can be ticked. The by-eye scale review against named Earth places was not done.
- 2026-10-23: Created from inbox draft draft-game-attrs-followups.md (found by soilveg).
