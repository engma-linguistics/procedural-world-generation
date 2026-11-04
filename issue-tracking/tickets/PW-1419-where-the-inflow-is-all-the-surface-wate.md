---
id: PW-1419
title: Where the inflow is all the surface water, the sea adds sst0's own anomaly on top of the inflow's
type: task
status: todo
parent: null
milestone: later
subsystem: ocean
effort: m
impact: med
found_by: lane150
blocked_by: []
relates: [PW-1411, PW-265, PW-589]
refs: ["planet/ocean.py::solve", "planet/climate.py::sea_surface", docs/review/base-climate/nordic-seas/round1.md, docs/review/base-climate/nordic-seas/nordmap.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: where the warm Atlantic water makes up nearly all of the sea's surface, the model's sea should be at
that water's temperature. Instead it comes out 1.5-2 C warmer than the water, because the warmth the sea would have
anyway is added on top.

`ocean.solve.sst_c` and `climate.sea_surface` set sst = sst0 + carried(share x (t_in - t_eq)), less the latitude's
mean. With share ~1, mixing the surface water with the inflow would give ~t_in, i.e. sst0 + share x (t_in - sst0).
The t_eq base adds (sst0 - t_eq) once more.

Earth L6 on main 65e13f48 (`nordmap.py`, the main branch of the inflow; t_in, the inflow, against the model's sst):
- 59.8 N 9.8 W: 7.6 against 9.7;
- 62.0 N 8.2 W: 6.5 against 8.0;
- 66.6 N 1.4 E: 3.0 against 4.4;
- 70.6 N 8.2 E: 0.3 against 2.3.

This hides how cold the inflow arrives in the Nordic seas: it crosses the Greenland-Scotland ridge at 3.8 C,
carrying 118 TW against Tsubouchi et al. 2021's 305 TW. It also flatters the Nordic seas' SST.

The heat is conserved by `moc_zonal` (PW-265, PW-589), so a change here moves heat between places, not in total.
Expect the subpolar box to cool and to need PW-1411's mechanism with it. Screen with
`docs/review/base-climate/nordic-seas/screen.py`.

- [ ] decide whether the imprint should be share x (t_in - sst0); if so, screen it on Earth L6 against OISST
  (the 40-60 N box and the Nordic seas)

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: ocean calibration against Earth sea temperatures; Earth is a plausibility anchor, not a target
- 2026-11-03: Created from inbox draft draft-inflow-imprint-adds-on-sst0-anomaly.md (found by lane150).
