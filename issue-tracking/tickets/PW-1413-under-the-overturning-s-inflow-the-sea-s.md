---
id: PW-1413
title: Under the overturning's inflow the sea's winter swing is cut to a tenth, but OISST shows about half
type: task
status: todo
parent: null
milestone: later
subsystem: ocean
effort: s
impact: med
found_by: lane142
blocked_by: []
relates: [PW-593, PW-1381]
refs: ["planet/ocean.py::winter_half", "planet/climate.py::_sea_half", docs/review/base-climate/n-atlantic/round1.md, docs/review/base-climate/n-atlantic/seabox.py, docs/review/base-climate/n-atlantic/get_sst.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: where the warm Atlantic water flows north, the model's sea hardly cools in winter. The real sea
there cools about half as much as the open ocean does.

`ocean.winter_half` spreads the winter's cooling over the inflow layer (`moc_layer_m` 500 m), so under a full
inflow the winter half-swing is brine_m / 500 = 0.1 of its own. OISST v2 1991-2020 (Earth L6, `seabox.py`, model
own -> after the cut, against OISST's annual minus its coldest month, in C):

| | model own | after the cut | OISST |
|---|---|---|---|
| Nordic seas | 3.95 | 0.51 | 2.0 |
| NE Atlantic 50-60 N | 2.79 | 0.39 | 2.0 |
| NW Atlantic 50-60 N | 4.98 | 0.99 | 2.6 |
| N Pacific (no inflow; 2.63 after its small share) | 3.11 | 2.63 | 3.6 |

The 400-1500 m winter mixed layers (Holte et al. 2017, GRL 44, 5618) are late-winter maxima. Most of the cooling
happens while the layer is still deepening.

A separate depth `moc_winter_m` of 100 m (screened in lane 142) matches these. It moves the box's coldest month
12.8 -> 12.1 C and the sinking 12.5 -> 13.6 Sv, and leaves the rain where it was. The 100 m is fitted to OISST's
swing, not to a published cooling-season depth. Best done inside PW-593's mixed-layer rule (a summer and a winter
layer from the wind and the heating), not as a lone constant.

- [ ] the winter half-swing under the inflow within ~0.7 C of OISST's in the Nordic seas and the NE Atlantic,
  on Earth L6

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: ocean calibration against Earth sea temperatures; Earth is a plausibility anchor, not a target
- 2026-11-03: Lane 150: not attempted (no openable source for a cooling-season mixed-layer depth); round1.md suggests the cut apply only to the inflow's extra winter loss. Back of the line with PW-1411.
- 2026-11-03: Created from inbox draft draft-winter-half-cut-too-strong-under-inflow.md (found by lane142).
