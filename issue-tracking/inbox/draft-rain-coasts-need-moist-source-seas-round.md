---
title: "Rain inland: the import across the coasts only moves with supply; next round is moist source seas (PW-015 option A), then inflow depth + friction + ascent together"
type: task
status: needs-decision
parent: PW-015
milestone: v2
subsystem: climate
effort: xl
impact: high
found_by: lane120
blocked_by: []
relates: [PW-026, PW-1099, PW-1100, PW-1120, PW-1094, PW-1097, PW-1279]
refs: [docs/review/base-climate/rain-inland/diagnosis.md, docs/review/base-climate/rain-inland/candidates.patch, docs/review/base-climate/rain-inland/budget_L6_screens.txt, docs/review/base-climate/rain-inland/withtune.py, docs/review/base-climate/rain-inland/summ.py, docs/review/base-climate/rain-inland/ecsumm.py, docs/review/base-climate/moisture-budget/README.md, docs/review/base-climate/moisture-inflow-ascent/, docs/references/drag-sources-pw1120.md, tools/moisture_regions.py, tools/earth_check.py, planet/climate.py::_rain, planet/climate.py::_season_inputs, planet/climate.py::sea_uptake, planet/climate.py::monsoon_wind, planet/climate.py::inflow_share, planet/climate.py::compute, "Zhang et al. 2011 J. Climate 24:5167", "van der Ent & Savenije 2011 ACP 11:1853", "Bretherton, Peters & Back 2004 J. Climate 17:1517", "Schiro et al. 2016 JAS 73:4043", "Karger & Bumke 1996"]
---

## Description
In plain words: on Earth the model rains too much 1000-2500 km inland (Mongolia, the Great Plains, Russia) and too
little on the humid coasts (SE USA, the Pampas, India, Japan: about half). Lane 120 tried three sound fixes (three
strikes). Two only moved rain around inside the same continent. The third, surface friction over land, made every
monsoon coast a bit wetter, but it was too small to matter. The amount of rain a continent gets is set by how much
sea vapour crosses its coasts. The seas next to those coasts are too dry in the model (the Gulf and the W Atlantic
rain 0.4x and hold 0.8x the observed vapour). So the next fix has to make those seas moister first.

Screens (Earth, whole solves, diagnosis section 4):
- C1 (vapour above the winter inversion): W Europe 1148 -> 1098 (obs 910) and Russia 916 -> 902 (590). The import
  doesn't move.
- C2 (shower humidity gate): SE USA 708 -> 400 and the Pampas 396 -> 266, the wrong way.
- C3 (land-sea friction, fric_land 0.89 from Karger & Bumke's angle plus the land's 25-50 deg), L7: SE USA 719 ->
  809, Pampas 394 -> 430, SE China 1061 -> 1114, E Australia 551 -> 631, Sahel 2094 -> 2043, r 0.714 -> 0.718. But
  B 25.0 -> 24.2 and W Europe +29.
- C3 as PW-1099's partner: SE USA only 338 -> 366 (main 708).

Options:
- **A. A design round on supply** (lean). PW-015 option A: a boundary layer under the column, so the subtropical
  seas' surface air sits near 0.8 of saturation under a drier free troposphere. Add the storm-track seas' winter
  evaporation (a third of NCEP's in the model). Then judge, in one pass, PW-1099's inflow depth, PW-1100's ascent
  and lane 120's fric_land on top (all in the parked patches). Gate: land 40-50 N toward GPCC, B >= 25, r >= 0.70,
  SE USA and the Pampas not below main. Cost: l/xl, with the Earth screens first.
- **B. Merge fric_land 0.89 alone now.** Small and sound. Coasts +5-15%, r +0.004, but B -0.8, and it leaves the
  interiors as they are. A partial fix: against the no-temporary-fixes rule, unless the owner wants the coasts'
  step now.
- **C. Park rain inland** after the summer heat (PW-1279) and plant growth (D34), as the three-strikes rule says.
  Revisit with A.

- [ ] owner picks A, B or C
