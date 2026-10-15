---
title: "Time zoom: an Eemian-like Earth start now loses almost all of Greenland in 8 kyr"
type: task
status: todo
parent: null
subsystem: timezoom
effort: s
impact: low
found_by: icemb
blocked_by: []
relates: [PW-114, PW-190]
refs: [planet/timezoom.py, planet/icemass.py]
---

## Description
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
