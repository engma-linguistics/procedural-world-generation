---
id: PW-137
title: "Viewer: show the overturning circulation (AMOC-style) and make gyres legible"
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-013]
refs: [planet/ocean.py, viewer/index.html]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner looked for AMOC-like circular ocean patterns and found only the surface-current arrows. The model has both: wind-driven gyres (climate.currents, Stommel) in the 'Ocean currents' overlay, and the thermohaline overturning (planet/ocean.py: salinity, winter density, sinking in polar seas, Stommel strength), but the overturning is not stored or drawn. Store sea-surface salinity, sinking sites/strength and overturning strength (Sv) in worlds (and keyframes if cheap); draw sinking sites as markers, the deep return flow as a dashed path or a schematic loop, and report the overturning strength in the info panel. Also check the currents overlay renders gyres as visible loops (arrow density/streamlines) on a few worlds.

## Updates
- 2026-10-14: Status todo -> done. viewerocean: worlds store salinity, sinking (Sv per cell) and meta overturning (sv, north_sv, south_sv, sites, schematic paths: ocean.loop_schematic). Viewer: salinity layer, 'Overturning (deep water)' overlay (sinking rings sized by Sv with labels, the warm surface inflow along the model's route, dashed deep return flow marked schematic, upwelling rings), overturning line in the info panel; ocean currents now drawn as streamlines (arrows while a run plays) so gyres read as loops. Earth 64fc00: 13.7 Sv (N 11.1, S 2.5): Nordic 7.0, Labrador 4.1, Ross 1.9, Weddell 0.6; none in the North Pacific. Demo world 9b8200 (run f59dd6 @ 1000 Myr): 30.9 Sv. Screens: docs/review/ocean/. Keyframes: draft.
- 2026-10-14: Created.
