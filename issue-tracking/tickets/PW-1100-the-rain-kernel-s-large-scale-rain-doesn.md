---
id: PW-1100
title: The rain kernel's large-scale rain doesn't see where the wind converges (no ascent term)
type: task
status: todo
parent: PW-015
milestone: later
subsystem: climate
effort: l
impact: med
found_by: lane58
blocked_by: []
relates: [PW-1093, PW-1097, PW-026]
refs: [planet/climate.py, docs/review/base-climate/moisture-inflow-ascent/, tools/moisture_regions.py, docs/review/base-climate/moisture-budget/README.md]
created: 2026-10-30
updated: 2026-11-03
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
- 2026-11-03: Triage 11-03: v2 -> later: rain kernel is calibration polish and three strikes sends it to the back of the line (PW-1363)
- 2026-10-30: Owner 10-30 D11: moisture/monsoon-coast work parked for v2; an agent will find a downloadable drag source.
- 2026-10-30: Lane 62 round 1. In plain words: rain where the low-level wind converges now has a form with no
  tuned scale. It is the right kind of term for the winter storm tracks. But it doesn't rain the summer inflow at
  the coasts, and on its own it moves the dry-climate share the wrong way. Kept as a patch
  (docs/review/base-climate/moisture-inflow-ascent/: TUNE ascent, climate.convergence, _season_inputs' ascent), not
  merged: it rides with PW-1099's inflow depth once that has its coastal partner (coordinator 10-30).
  - Form: by continuity, the friction layer's converging air rises out of it with that layer's vapour. So the extra
    large-scale rain per unit of column vapour is inflow_share x max(convergence, 0) (1/s), on the same humidity
    gate, x (1 - sink) as the storm lift. The convergence is that of monsoon_wind's cross-isobar inflow, through
    the kernel's own faces. The zonal belts' ascent and subsidence stay itcz and sink. There is no c0, so the "~1e-6
    1/s" scale is no longer needed: the rate is the convergence itself (Earth L6: median ~0, 90% 3e-7, 99% 1.7e-6).
  - A variant on the whole land-sea wind's convergence (with the tropics' down-gradient flow) wetted the
    tropical heat lows' margins more (B 23.9) and was dropped.
  - L6, obs / main / ascent alone: N Atlantic storm track Oct-Mar 1651 / 1197 / 1379, N Pacific 1465 / 1214 /
    1335; sea 40-50N 1285 / 1010 / 1067, 50-60N 1140 / 947 / 985; W Europe 911 / 1147 / 1103; European Russia 590 /
    909 / 891; W Siberia Oct-Mar 368 / 534 / 518; summer and the monsoon coasts about unchanged (SE USA 642,
    Pampas 413). Costs: B 25.2 -> 24.3, r 0.721 -> 0.705, exact 38.4 -> 37.5. The B lost is the subtropical heat
    lows' margins (S Africa ~570k km2, N Africa ~290k, Australia, S America; draft on the sink mask).
  - With the inflow depth (PW-1099) it changes little. The summer convergence sits at the heat lows' centres, not
    the coasts, because the wind has no land-sea friction contrast.
- 2026-10-30: Created from inbox draft draft-rain-kernel-no-convergence-lift.md (found by lane58).
