---
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
refs: [planet/timezoom.py]
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
