---
id: PW-189
title: "Glacial isostasy: ice sheets load and depress the crust; rebound after melt (instant in the run, relaxing in the time zoom)"
type: task
status: done
parent: null
subsystem: tectonics
effort: s
impact: high
found_by: daniel
blocked_by: []
relates: [PW-104, PW-091]
refs: []
created: 2026-10-14
updated: 2026-10-15
---

## Description
Owner: top of the queue. Ice presses the crust down by about ice_thickness x rho_ice/rho_mantle (~0.3); after deglaciation it rebounds over ~10 kyr (mantle relaxation), which is why Hudson Bay and the Baltic are seas and why raised beaches exist. Main run (4 Myr steps): include the ice load in isostasy (effectively in equilibrium at that step). Glacial time zoom (kyr steps): relax toward equilibrium with a ~3-10 kyr timescale (with lithospheric flexure smoothing, ~100s of km), so post-glacial seas, proglacial lakes and raised shorelines appear. Check: depression under a 3 km sheet ~800-900 m; Hudson Bay-like rebound rates (~1 cm/yr).

## Updates
- 2026-10-15: Status in-progress -> done. Merged (ice): isostasy.ice_load (0.28 x ice, ~150 km flexure); instant in the run (sim.ice_sink), 3 kyr relaxation in the time zoom; bed-under-ice layer; ~1 km dips under 3.5-3.8 km ice, rebound ~1-2 cm/yr. Demo: run 981d58, time zoom 1a08e7, finished world 38b7d5.
- 2026-10-15: Status todo -> in-progress. Overnight agent, worktree ice.
- 2026-10-14: Created.
