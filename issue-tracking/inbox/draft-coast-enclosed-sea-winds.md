---
title: "Waves in enclosed seas 3-5x too strong once the wind recovers off land in ~50 km (PW-272)"
type: task
status: todo
parent: null
subsystem: coast
effort: m
impact: med
found_by: fix-coast-zoom
blocked_by: []
relates: [PW-075, PW-272, PW-270]
refs: [planet/coast.py, tools/coast_check.py, docs/review/audit/fixes-coast-zoom.md]
---

## Description
After PW-270 (gust moment) and PW-272 (L_RECOVER 1200 -> 50 km, LAND_SLOW 0.5 -> 0.3) and the
U_TRADE = U_STORM = 7 m/s refit on the open-ocean coasts, coast_check (L6) has the enclosed seas far
too strong: Baltic 29.8 kW/m (1-6), Black Sea 26.5 (1-5), Gulf of Lion 26.9 (3-8), Nile coast 16.8 (2-6),
North Sea S 29.1 (3-10); enclosed-sea rms log error 1.56, bias +1.4 (main: 0.82 / +0.2, held down by
the 1200 km recovery, which also cut open-ocean waves near every coast). PW-075 is the older ticket for
the same symptom; this may be merged into it.

Likely cause: the wind these seas see is the climate's large-scale wind and storminess, the same over
land-locked water as over the open ocean (the storm tracks over Europe in winter), and a fetch of a few
hundred km at 15-25 m/s still builds a big sea. Candidates, simplest first:
- surface wind over a sea hemmed in by land: the climate's mean wind over land is slowed by roughness
  (a land-share-weighted reduction of the upwind wind over ~500-1000 km, a property of the wind field,
  not of the waves' recovery);
- check the effective fetch: rays across a narrow sea that run along it reach far, and the cos^2
  spreading may overweight them.
Don't bring back a long L_RECOVER.
- [ ] enclosed-sea rows within 2x at most coasts without moving the open-ocean rows
