---
id: PW-114
title: "Time zoom: Eemian-like Earth start melts Antarctica, not Greenland"
type: task
status: todo
parent: null
subsystem: timezoom
effort: s
impact: low
found_by: climfix
blocked_by: []
relates: [PW-034]
refs: [planet/timezoom.py, planet/icemass.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
After PW-034 (climfix: Eemian eccentricity 0.042, absorb_km 600) the Earth time zoom's start gives a
realistic total, +8.5 m at 8 kyr (real Eemian +6-9 m), but the split is wrong: Antarctica gives +8.0 m
and Greenland -0.35 m (grows) in the first 10 kyr. Real: Greenland ~+2 m, Antarctica (mostly the West
Antarctic sheet) ~+3-5 m. Greenland under +80-110 W/m2 of June sun at 65-75N barely responds: bright
snow takes 0.2 of the anomaly and the mix over the 600 km air mass is mostly sea. Antarctica's loss
comes from its spring months (Sep-Nov, +60-70 W/m2 at 70S under the Eemian orbit). Check the
seasonal lag and which months melt, and whether bare-ice margins (f_snow) respond enough in Greenland.
Measure: tools-free probe `TZ.simulate(TZ.source_earth(6), kyr=10)`, ice volume change by region.

## Updates
- 2026-10-15: Merged inbox draft draft-eemian-greenland-collapses.md ("Time zoom: an Eemian-like Earth start now loses almost all of Greenland in 8 kyr", found by icemb).
  Update to PW-114 after PW-190 (icemb). With the shared mass balance (Greenland's margins now melt in
  the full summer once their snow is gone, as observed) and `anchor=obs` (Earth's start cooling only
  where the model's summer on the ice is warmer than observed: Antarctica's coast), the Eemian-like start
  (`TZ.simulate(TZ.source_earth(6), kyr=20)`) peaks at +8.5 m at 8 kyr with Greenland 2.8 -> 0.1 Mkm3
  (~7 m) and Antarctica 23.1 -> 22.4 Mkm3 (~1.7 m), then regrows (Greenland 3.3 Mkm3 at 20 kyr). Real
  Eemian: Greenland ~+2 m (it survived), Antarctica (West Antarctica) ~+3-5 m. The split has reversed:
  Greenland is now too sensitive (~310 Gt/yr average loss for 8 kyr; the snow melting out on its margins
  raises the share of the insolation anomaly it feels, `absorb`), Antarctica too stable (its anchor holds
  its coast ~11 C colder than the model's bare climate).
  Check: Greenland's summer anomaly under the Eemian orbit (+60 W/m2 at 65N June x insol_k 0.25 x
  absorb), whether `absorb` should follow the summer snow cover at all, and West Antarctica's marine
  margin (calving).
- 2026-10-14: Created from inbox draft draft-timezoom-eemian-split.md (found by climfix).
