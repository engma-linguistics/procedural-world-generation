---
id: PW-1100
title: The rain kernel's large-scale rain doesn't see where the wind converges (no ascent term)
type: task
status: todo
parent: PW-015
milestone: v1
subsystem: climate
effort: l
impact: med
found_by: lane58
blocked_by: []
relates: [PW-1093, PW-1097, PW-026]
refs: [planet/climate.py, tools/moisture_regions.py, docs/review/base-climate/moisture-budget/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Real large-scale rain falls where air rises. Air rises where the low-level winds pile into each other
(converge): at fronts, in lows, where an onshore wind slows at a coast. The model's large-scale rain rate
(`_season_inputs`' ls) knows only the latitude belts (ITCZ, subtropical sinking air, poles) and the storminess. It
never looks at whether the wind converges. So vapour carried onshore or into a storm track rains wherever the
humidity gate opens, which is often far downstream.

Probe (lane 58, Earth L6, kernel re-run, temperatures held): ls x clip(1 + conv / c0, 0.3, 4). conv is the mean wind's
convergence, smoothed over 300 km (its 5-95% range is +-2.5e-6 1/s). Annual mm/yr, base / c0 2e-6 / 5e-7:
- sea 50-60 N: 947 / 1088 / 1085 (GPCP 1140)
- W Siberia winter: 534 / 415 / 232 (GPCC 368)
- land 50-60 N: 970 / 929 / 819 (582)
- land 40-50 N: 952 / 999 / 900 (537). Summer interiors converge in the model, so they keep raining.
- SE USA winter: 361 / 163 / 125 (1333). The model's winter wind blows offshore there (PW-1097).

So it is the right kind of term for the storm-track seas and the winter interiors. It needs:
- the summer inflow fixed (draft: land-sea inflow overshoots inland);
- the winter return flow fixed (PW-1097) before it can help the subtropical coasts.

The scale c0 needs an anchor. Synoptic-scale convergence of ~1e-6 1/s is from memory, unverified: it needs a source.
- [ ] a design note with candidate forms, each tried in one Earth solve, together with the inflow-depth change

## Updates
- 2026-10-30: Created from inbox draft draft-rain-kernel-no-convergence-lift.md (found by lane58).
