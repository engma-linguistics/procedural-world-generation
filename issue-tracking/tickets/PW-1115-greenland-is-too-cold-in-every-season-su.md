---
id: PW-1115
title: "Greenland is too cold in every season (Summit 8 C too cold in summer, 16 C in winter): a diagnosis"
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: m
impact: med
found_by: lane57
blocked_by: []
relates: [PW-1095, PW-1050, PW-039]
refs: [tools/earth_check.py, planet/climate.py, planet/icemass.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. On the real Earth, the model makes Greenland far too cold all year round, not only in winter. The
inversion fix (PW-1050 (b)) had warmed Greenland's summers, but mostly on the inland ice, which never melts. That
was hiding part of this cold error, not fixing its cause. PW-1095 now keeps the inversion all year where the ice
never melts, so the error shows again in summer.

earth_check L6 after PW-1095 (C; model vs NCEP 1981-2010):

| | annual | coldest month | warmest month |
|---|---|---|---|
| Greenland region (65-80 N, 50-25 W) | -28.7 vs -21.4 (-7.3) | -46.9 vs -33.0 (-13.9) | -11.4 vs -5.0 (-6.4) |
| Summit GL (3177 m) | -35.6 vs -26.8 (-8.8) | -54.0 vs -39.7 (-14.3) | -18.3 vs -8.1 (-10.2) |

Before PW-1095 (main 347b4374): Summit's warmest month was -16.3, its coldest -56.0. Antarctica's interior has the
opposite sign (annual mean +5.6 C too warm, PW-039), so the cause isn't the shared ice-surface rule (lapse rate,
ICE_COOL, damping). Those apply the same way on both sheets.

Diagnosis to do (probes only, no tuning): split Summit's error into (1) the bare ground's air at the bed
(c["ground"]) against the observed air, after the lapse rate; (2) the sheet's own carried air (icemass.air_mass,
Greenland ~0.3-0.5); (3) the ice surface's own terms. Likely candidates: too little heat carried north over the
North Atlantic or Baffin Bay, the sea ice around Greenland in winter, or the carried air's footprint (SHEET_KM
1000 km) on a sheet ~1000 km wide. Earth is a plausibility anchor here, not a target.
- [ ] Written split of Summit's and the region's summer and winter error into the parts above
- [ ] A physical candidate (or a "leave it" with the reason), sent to the coordinator before any change

## Updates
- 2026-10-30: Created from inbox draft draft-greenland-all-season-cold-bias.md (found by lane57).
