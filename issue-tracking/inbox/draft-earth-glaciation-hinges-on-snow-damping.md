---
title: "Time zoom on Earth: glaciation hinges on the lying snow's local damping (too much Siberia/Alaska, too little Fennoscandia)"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: med
found_by: icemb
blocked_by: []
relates: [PW-033, PW-190]
refs: [planet/icemass.py, planet/timezoom.py, planet/timezoom_kernels.py]
---

## Description
Since PW-190 (icemb) the run, the time zoom and the zoom share one surface mass balance
(`icemass.py`): while the year's snow lies, the summer's warmth above the annual mean is damped by
`SUMMER_DAMP` x (`LOCAL` + (1 - `LOCAL`) x the sheet's cover within ~1000 km). Greenland's and
Antarctica's present balance want little damping at Greenland's scale (its margins melt, as observed),
but Earth's time zoom only glaciates with a local share `LOCAL` = 0.3 of the damping (0.18 in all):

| local damping (x 0.6) | Earth 150 kyr fall | Laurentide / Fennoscandia / Siberia / Alaska (Mkm3) |
|---|---|---|
| 0 (sheet cover only) | ~0 m | - |
| 0.135 (summer_damp 0.45) | -26 m | 4.3 / 1.0 / 1.3 / 1.4 |
| 0.18 (shipped) | -100 m | 14.2 / 2.4 / 11.5 / 7.3 |
| 0.3 (LOCAL 0.5) | -178 m | 20.1 / 18.1 / 16.9 / 7.7 |

On the observed climate (`baseline=obs`) Earth barely glaciates at all (-3..-10 m), so the knife edge is
not just the model's warm Labrador (PW-033). Real LGM: Laurentide ~30, Eurasian ~7-8 Mkm3, little ice
in Siberia, Alaska mostly ice-free. Siberia's model precipitation (283 mm vs 352 observed) is already
low, yet it glaciates: dry snowfields keep their snow too long once damped.
Ideas: the snow-albedo feedback on a cold orbit's snowfields belongs to their area (a large region
snow-covered all summer), which the sheet cover only counts once there's > 1 m of ice; count lying
snow in the cover; or vegetation/sea-ice feedbacks (tundra replacing forest), which inception models
need.
- [ ] Earth's 150 kyr time zoom reaches -100..-130 m with Laurentide and Fennoscandian ice and little
  in Siberia, without making generated planets' run ice larger
