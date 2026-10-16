---
title: "High-latitude seas get half of GPCP's rain (50-70 deg, both hemispheres), and Antarctica's margins still ~half their snow: the storm tracks bring no moisture of their own"
type: task
status: todo
parent: PW-013
subsystem: climate
effort: l
impact: high
found_by: polar-bundle
blocked_by: []
relates: [PW-015, PW-332, PW-313, PW-304]
refs: [planet/climate.py, tools/earth_check.py, tools/ice_probe.py, docs/review/audit/polar-bundle.md]
---

## Description
After the polar bundle (PW-332's vapour wind and ice-surface lift), Earth L6 at dT 0 still has the high-latitude
seas at about half of GPCP: sea precipitation 55-60S 433 mm vs 1154, 60-65S 356 vs 861, 50-60N 561 vs 1150,
60-70N 323 vs 886 (earth_check's ocean columns). Antarctica's margins sit at about half too (bed 0-500 m:
167 mm vs GPCP 364; 500-1000 m: 198 vs 420), and with them the PW-313 probe's last gap: at dT 0 the sheet still
loses ~12 margin cells per update (2.33% after 8 updates; with Antarctic snowfall x1.5 as a diagnostic it holds
at 965 cells, no loss after the 2nd update). The tropical land is too wet by about as much (0-20N land 2034 /
1403 vs GPCC 1721 / 746), since the global mean is renormalised to 1000 mm.

Why (measured, polar-bundle write-up section 3):
- Over open sea the kernel refills the air to `rh x qs(sst)` every iteration, so a sea's rain is the local
  rain rate times the local saturation: P ~ ls x qs(sst). Cold storm-track seas (sst 1-4 C) rain what they
  evaporate, ~0.4-0.6 of a 12 C sea's. On Earth the storms carry the subtropics' water poleward (P - E
  ~+300-500 mm/yr poleward of 50 deg) and rain ~2.5x more per unit of vapour than the tropics.
- The storms' eddy mixing is capped: `diff = clip(0.12 + eddy x B, 0, 1)` is already 1 in every storm track
  (B ~0.8-1.4), so `TUNE['eddy']` x3 changes nothing. At L6 that is one neighbour mix per ~4 h step (K ~2e5
  m2/s against ~1-2e6 for real storm tracks). Extra mixing passes (diagnostic) push vapour onto the
  continents (Antarctica's plateau too wet at 8 passes) but don't wet the seas.

What it needs is PW-015's moisture transport: storms that converge vapour into the storm track and rain it
there (a storm-track rain efficiency, or eddy moisture flux down the vapour gradient at the storms' scale),
then re-check the Southern Ocean, Antarctica's margins (PW-332's 100-500 mm) and the probe.
- [ ] Southern Ocean 50-65S and N Atlantic/Pacific 50-70N sea precipitation within ~30% of GPCP
- [ ] PW-313 probe at dT 0 steady near 3% over 8 updates without a snowfall multiplier
