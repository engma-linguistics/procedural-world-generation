---
title: "The finished N Atlantic is ~3 C too warm in the annual mean and ~5 C in winter; now that the rain sees it (PW-1364), its storm track rains 1.7x GPCP"
type: task
status: todo
parent: PW-015
milestone: v2
subsystem: ocean
effort: m
impact: med
found_by: lane134
blocked_by: []
relates: [PW-1364, PW-593, PW-589, PW-1362]
refs: [docs/review/base-climate/rain-supply/round2.md, docs/review/base-climate/rain-supply/seaparts.py, docs/review/base-climate/rain-supply/seaair.py, "planet/climate.py::compute", "planet/climate.py::sea_surface", "planet/ocean.py::winter_half", "planet/ocean.py::solve", tools/moisture_regions.py]
---

## Description
In plain words: the model's North Atlantic between Newfoundland and Ireland is too warm, most of all in winter.
The rain used to see a sea 6 C colder than the finished one, which hid this. Since lane 134's fix (PW-1364) the
rain sees the finished sea, so that box now rains and evaporates too much.

Earth L6, N Atlantic storm-track box (40-60 N, 60-10 W), `seaparts.py`:

| | model | NCEP |
|---|---|---|
| annual SST / 2 m air | 13.7 / 14.3 | air 10.7 |
| the overturning's share of the annual SST | +5.1 C | |
| monthly half-swing of the air | 1.92 | 4.64 |
| winter-half air | 13.1 | 8.0 |

The rain over the box after PW-1364 (`moisture_regions.py --level 6 --no-cf`):

| | P (GPCP) | E (NCEP) |
|---|---|---|
| Oct-Mar | 2765 (1651) | 1990 (1339) |
| Apr-Sep | 1760 (1057) | 1919 (610) |

The sea bands as a whole are closer to GPCP than before (40-50 N 1318 against 1300, 60-70 N 778 against 905); only
50-60 N overshoots (1480 against 1148).

There are two parts:
- the small swing, which is PW-593's one 50 m layer. `ocean.winter_half` also cuts the winter swing under the
  inflow to brine_m / moc_layer_m;
- the annual +3 C: the overturning's +5.1 over the latitude's sea may be a little large, or `moc_zonal`'s band
  take-off may be too small in the N Atlantic. Note that NCEP's air sits below the real SST in winter (cold-air
  outbreaks), and the repo has no observed SST to compare against.

What I'd try: PW-593 first (the swing), then re-measure. If the annual stays 2-3 C warm, look at the inflow's heat
loss (`moc_lambda`) against an observed SST climatology.

- [ ] N Atlantic storm-track winter-half sea air within ~2 C of NCEP on Earth L6
- [ ] its winter evaporation within 0.7-1.3x NCEP, with the humid coasts' and the interiors' rain ratios no worse
