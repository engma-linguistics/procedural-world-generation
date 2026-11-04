---
id: PW-1115
title: "Greenland is too cold in every season (Summit 8 C too cold in summer, 16 C in winter): a diagnosis"
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: m
impact: med
found_by: lane57
blocked_by: []
relates: [PW-1095, PW-1050, PW-039]
refs: [tools/earth_check.py, planet/climate.py, planet/icemass.py]
created: 2026-10-30
updated: 2026-11-03
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
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Lane 67, the seasonal-lapse probe (probe only, scratch seaslapse.py: icemass._mean_year's bare ground under h m of ice gets its warmest month +SWING x h and its coldest -SWING x h, so the ice surface cools with height by LAPSE - SWING in summer and LAPSE + SWING in winter, the same annual mean). Source: Steffen & Box 2001 (JGR 106(D24): 33951, GC-Net 1995-1999): "The mean annual lapse rate along the surface slope is 0.71 C / 100 m, with monthly mean lapse rates varying between 0.4 C / 100 m in summer and 1.0 C / 100 m in winter"; Van As et al. 2014 (GEUS Bulletin 31: 83-86, PROMICE + GC-Net): the ice-sheet average near-surface lapse rate has a reversed annual cycle, winter values often above 10 C/km. SWING 2.5 C/km (4 / 9 C/km) on all ice: the Earth staircase's gap at dT -4 / -2 / 0 goes from 11.9 / 11.8 / 5.3 points to 8.0 / 3.9 / 1.5 (up-leg 10.1% vs down-leg 8.6% at 0, inside the acceptance), but the down-leg shrinks (15.7% of land at -6 vs 20.5%; LGM ~25%), and on Earth Greenland's warm month improves (-7.0 -> -2.4 C error; interior -8.5 -> -2.8; margins -1.8 -> -0.6) while its coldest month worsens (-13.9 -> -19.2) and Antarctica's interior warm month goes from +1.3 to +8.4 (its cold month +3.7 -> -3.4). The same swing scaled by the warmest month's melting share (1 - cold_share, as PW-1095's inversion): gap 10.2 / 9.5 / 2.4, down-leg 18.2% at -6, so it closes about half the dT 0 gap and little of the mid-leg one. Read: the summer gradient over ice is a real part of the persistence, and the GC-Net numbers support a gentler melt-season gradient, but as a lapse change alone it either breaks Antarctica's summer (on all ice) or does too little (on melting ice only). Not proposed as a change yet.
- 2026-10-30: Lane 67, the split (probe only: climate.compute on Earth L6, main c7f8c76f, against the NCEP fields in data/earth/L6.npz; scratch gl_split.py, lapse.py). Error = (1) the bare ground's air at the bed, taken up to the ice surface at LAPSE, against NCEP, of which (2) is the sheet's carried air, + (3) the ice surface's own terms. Greenland 65-80 N 50-25 W ice, warm month: -7.0 = (1) -2.7 [carried air -2.1] + (3) -4.4; coldest month: -13.9 = (1) -11.8 [carried air 0] + (3) -2.1. Interior (> 2500 m): warm -8.5 = -3.8 [-2.2] + -4.6; cold -14.3 = -12.3 + -2.0. Margin ice (< 1500 m): warm -1.8 = +1.1 [-1.3] + -2.9; cold -8.4 = -6.9 + -1.6. Neighbours are fine: bare land 60-80 N 100 W-0 warm +2.4, cold +1.8; the sea around Greenland warm +0.4, cold +1.6. Antarctica's interior has the opposite sign in (1): warm +4.3 [carried air -10.1], cold +5.7. So the winter error sits in the bare ground's air taken up to the surface, not in the surface rule, and the margins' summers (what sets a sheet's extent) are within ~2 C. Height dependence over the ice cells (regression on surface height and latitude), C per km, NCEP vs model: Greenland warm -3.1 vs -7.1, cold -5.6 vs -8.7; Antarctica warm -6.1 vs -6.8, cold -10.7 vs -6.7 (NCEP's 2.5 deg orography smooths this; read as a direction only). Lead: the model's ice surface cools with height by LAPSE (6.5) plus the thickness terms everywhere, while Greenland's observed summer gradient is about half that. That steeper summer gradient strengthens the height feedback that keeps big sheets alive (most of the staircase's gap, see below), but it is a lead, not yet a cause.
- 2026-10-30: Lane 67 (frozen-over diagnosis, PW-1091). Sheet persistence is the amplifier behind "frozen over". Earth on main, tools/ice_probe.py --stair (4 updates a step), share of land under ice: going down 10.0 / 11.3 / 14.9 / 20.5 / 27.6% at dT 0 / -2 / -4 / -6 / -8; coming back up 27.5 / 26.8 / 23.1 / 15.3% at -6 / -4 / -2 / 0. With the carried air off (probe only) the gap at -4 / -2 / 0 shrinks from 11.9 / 11.8 / 5.3 to 9.5 / 6.1 / 3.6 points, so most of it is the sheet's height and surface terms. On generated worlds (coasts judge, 36 L6 draws per arm, 300-988 Myr) the median iced land at dT -1..+1 is 0.09-0.11 before the coasts package (Earth today ~10.7% of land) and 0.13-0.17 with it, ~1.5x, and +0.04-0.06 at every dT from -4 to +1. Acceptance proposed (coordinator agreed): the staircase's up-leg back within ~1-2 points of the down-leg at dT 0, a plausibility anchor, not a fit; a cause fix only (Antarctica has the opposite sign).
- 2026-10-30: Created from inbox draft draft-greenland-all-season-cold-bias.md (found by lane57).
