---
id: PW-074
title: "Wave power: Southern Hemisphere westerly coasts too weak, N Atlantic too strong"
type: task
status: todo
parent: null
subsystem: coast
effort: m
impact: med
found_by: deltas
blocked_by: []
relates: []
refs: [planet/coast.py, planet/climate.py, tools/coast_check.py, docs/review/audit/coast-batch.md]
created: 2026-10-14
updated: 2026-10-16
---

## Description
Southern Hemisphere westerly coasts get ~half their observed wave power; the N Atlantic and NE Pacific
get ~1.5× too much. The storm tracks come mostly from land–sea contrast, so they're weak over the
Southern Ocean. Fix in the storm-track/wind model rather than by refitting constants.

## Updates
- 2026-10-16: Coordinator 2026-10-16: option B (surface wind in the climate that knows the surface; coast reads it). PW-075's enclosed-sea half and PW-296 fold into this.
- 2026-10-16: Merged inbox draft draft-wave-storm-winds-over-land-locked-seas.md ("Waves: where to weaken the storm winds that land-locked seas see (enclosed seas 3-6x too strong)", found by coast-batch).
  The coast batch looked for the enclosed seas' excess wave power (PW-075, PW-296). On the Earth world (L6, 2026-10-16): Baltic 33.5 kW/m (observed 1-6), Black Sea 28.5 (1-5), Gulf of Lion 29.3 (3-8), Nile coast 18.1 (2-6), North Sea S 31.6 (3-10). Enclosed-sea rms log error 1.61, bias +1.47; the 18 open-ocean rows are at rms 0.53, bias ~0.
  
  **It is the wind, not the wave growth.** Per-direction ray contributions show each enclosed-sea ray of only ~100-600 km fetch bringing 1-6 kW/m, because the wind along it is 11-13 m/s. Compared with rough climatological 10 m winds (ERA5/QuikSCAT maps, over the sea within 500 km), the wave-driving wind U = U_TRADE |wind| + U_STORM storminess is:
  - enclosed seas: Mediterranean 1.6-1.65x, Baltic 1.8x, North Sea 1.6x, Black Sea 2.0x;
  - NH open coasts 1.15-1.8x (Ireland 1.35, Portugal 1.7, Oregon 1.8, British Columbia 1.7);
  - SH open coasts 1.0-1.3x (SW Australia 1.0, Cape Town 1.0, S Chile 1.2).
  The calibration on open coasts splits the NH/SH difference (PW-074: NH open coasts ~1.5x too strong, SH ~0.55x). The enclosed seas are all in the NH and fetch-limited (power ~U^(7/3)), so they inherit the NH excess and add their own: storms keep their open-ocean strength over and behind land.
  
  **What a sound coast-side constant can't do** (open-ocean refit of U_TRADE/U_STORM each time):
  
  | change | open rms / bias | enclosed rms / bias |
  |---|---|---|
  | now (T_STORM 12 h, L_RECOVER 50 km) | 0.53 / -0.01 | 1.61 / +1.47 |
  | L_RECOVER 100 km (the ABL's inertial length U/f) | 0.53 / -0.04 | 1.55 / +1.40 |
  | L_RECOVER 200 km | 0.54 / -0.04 | 1.44 / +1.29 |
  | T_STORM 24 h | 0.69 / +0.04 | 1.28 / +0.98 |
  | T_STORM 36 h | 0.83 / +0.17 | 1.24 / +0.96 |
  
  A longer storm duration trades the open-ocean fit away; a sound recovery length barely moves the seas.
  
  Options:
  - **A. In coast._season_winds:** scale the storm part of the wind by the sea share along the storms' upstream path (westward along the jet) over a cyclone's filling distance (cyclones fill over land within ~1-2 days: ~1000-1500 km at ~10 m/s), then refit. A new length constant. It resembles the old 1200 km recovery the audit called a fit, and it would also cut NH open coasts in the lee of continents (Japan E, US East, Norway).
  - **B. In the climate (with PW-074):** a surface wind that knows the surface. The storm tracks come from land-sea temperature contrast, so they're strong over NH continents and weak over the Southern Ocean; surface roughness slows the wind over land and the seas it encloses. coast.py would then read a surface wind speed instead of building one from |wind| and storminess.
  - **C. Accept and document:** enclosed seas 3-6x too strong; their deltas lean wave-dominated (Po, Danube "wave").
  
  Lean B: the wind is the climate's, PW-074 already asks for the storm-track fix there, and A would be a stopgap (owner rule: no temporary fixes). PW-296 and PW-075's enclosed-sea half could be folded into B.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Coast.
