---
id: PW-326
title: "Zoom: reefs on continental shelves as terrain (reef crest near sea level, lagoon behind), not only as a habitat colour"
type: task
status: done
parent: PW-184
subsystem: zoom
effort: m
impact: med
found_by: coastal-life
blocked_by: []
relates: [PW-188, PW-097, PW-004]
refs: [planet/zoom_coastal.py, planet/zoom_volcanoes.py]
created: 2026-10-15
updated: 2026-10-16
---

## Description
Since PW-188 the zoom places coral reefs per pixel (`coastal_life` = 1) on warm, clear shelves shallower than the reefs' light depth, as planet-fixed patches covering ~25% x the water's suitability of that floor, and the satellite view colours them. The terrain doesn't change: a reef patch at 20 m stays at 20 m. Volcanic reefs are real landforms (zoom_volcanoes: fringing flats, barrier reefs, atoll rims at sea level). Non-volcanic reef coasts (Great Barrier Reef-like) would look right with the same treatment: reefs grow up to just below sea level (the run's reef rule builds carbonate to -5 m), with a fringing reef along the shore, or a barrier reef at the shelf break with a lagoon behind it, and patch reefs in between.

Sketch: from the reef pixels and the shelf geometry, raise reef pixels toward -1..-3 m (a flat top, a steep fore-reef), keep the coarse cells' mean depth by deepening the lagoon slightly; choose fringing vs barrier from the shelf width. Keep it in zoom_coastal, called before the satellite view. Mind the other zoom passes (cell means, coastline).
- [ ] reef pixels at reef-flat depth in the elevation layer, cell means kept
- [ ] a barrier reef with a lagoon on a wide warm shelf; a fringing reef on a narrow one

## Updates
- 2026-10-16: Status in-progress -> done. Done (af4b0a5): fringing/barrier/patch reefs as terrain, reef flats 1-3 m below sea, lagoon deepened to keep cell means.
- 2026-10-16: Status todo -> in-progress. Zoom batch 3 agent started.
- 2026-10-15: Created from inbox draft draft-zoom-reef-terrain.md (found by coastal-life).
