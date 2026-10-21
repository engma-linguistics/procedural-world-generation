---
id: PW-428
title: "Time zoom viewer: the 65N July sunshine curve misleads when the cycling ice is southern; show insolation where the ice cycles"
type: task
status: done
parent: null
milestone: null
subsystem: viewer
effort: s
impact: low
found_by: iceq
blocked_by: []
relates: [PW-030]
refs: []
created: 2026-10-16
updated: 2026-10-16
---

## Description
In 98ee98 and 080df3 the cycling ice sits at 35-55S, yet the time zoom's chart shows 65N July sunshine. Pick the latitude and hemisphere of the ice that comes and goes (e.g. the area-weighted latitude of ice present only at glacial maxima) and show its summer insolation, or show both.

## Updates
- 2026-10-16: Created.
- 2026-10-16: Done (viewer lane). timezoom.cycling_ice_sun (end of simulate): the cycling ice = cells iced
  (> 1 m) at the frame of most ice volume but not at the frame of least; its hemisphere = the one with more
  of that area, its latitude = the area-weighted mean there. Each frame gets stats.insol_ice_summer_anom
  (mean of that latitude's two midsummer months, Jun-Jul or Dec-Jan, against the reference orbit, as the
  65N stat); meta.ice_cycle = {lat, area_mkm2}. The viewer's chart draws it solid with 65N July dashed,
  and the summary line shows both. When the cycling ice is within 3° of 65N, or a time zoom predates
  this (all current ones: remake to get it), the chart is as before. Checked on a scratch copy of 98ee98:
  cycling ice at 42°S, 13.8 M km²; its summer sun runs roughly opposite to 65N July (precession).
