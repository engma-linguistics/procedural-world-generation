---
title: "More, thicker ice on generated planets after PW-102: keep or tune ICE_FEEDBACK?"
type: task
status: needs-decision
parent: null
subsystem: climate
effort: xs
impact: med
found_by: climfix
blocked_by: []
relates: [PW-102]
refs: [planet/tectonics/earth.py, "run e960ee", "run b1eb73"]
---

## Description
PW-102's new ice rule (climfix) changes how much ice the main run carries. L6 seed 21, frames 100-1000
Myr, old (b1eb73) -> new (e960ee): ice 2.15 -> 4.04% of the surface (max 5.5 -> 10.4%), polar land
iced 28 -> 63% (polar deserts now covered, PW-032), mid-latitude land iced 5.6 -> 10%, tropical ice
cells 86 -> 17 per frame. Ice volume as sea-level equivalent: mean 25 -> 99 m, max 75 -> 332 m; per % of
the surface 12 -> 25 m (Earth today ~22: the old sheets were too thin). Sea level (with the tectonic
part) averages -186 m vs -94 m. The ice-albedo feedback in global_temperature amplifies whatever the
rule does, so the result is sensitive to ICE_FEEDBACK (share of a sheet's height that keeps it alive):
0.5 gave 1.17% ice, 0.75 gives 4.04%.
Options:
- A: keep 0.75 (Earth-like ice per land area, ~11% of land vs Earth's ~10%; thick sheets; deep icehouse lows).
- B: 0.6-0.65, to land between (needs an L6 run each; ~6 min).
- C: keep 0.75 but cap the albedo feedback or ICE_MAX lower (3 km) to trim the icehouse sea-level lows.
Lean: A (it matches Earth's ice per land area and thickness), check the L7 showcase look first.
