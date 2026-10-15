---
id: PW-033
title: "Time zoom on Earth: weak glaciation, no Laurentide or Fennoscandian ice"
type: task
status: todo
parent: null
subsystem: timezoom
effort: l
impact: med
found_by: timezoom
blocked_by: []
relates: [PW-038]
refs: [planet/timezoom.py, tools/earth_data.py, docs/proposals/glacial_timezoom.md, planet/icemass.py, planet/timezoom_kernels.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
On our model's Earth climate the time zoom reaches only −52 m at 150 kyr (LGM ~−120 m). Labrador and
Baffin summers are ~5 °C too warm, so no Laurentide inception; Tibet, Karakoram and the Altiplano grow
ice caps, and Cordillera and Alaska ice is too big. On the observed climate baseline there is no
Fennoscandian ice. Calibration target (from the spec): Laurentide/Fennoscandian-like ice and ~−100 m at
the cold peaks over ~150 kyr.

## Updates
- 2026-10-15: Merged inbox draft draft-earth-glaciation-hinges-on-snow-damping.md ("Time zoom on Earth: glaciation hinges on the lying snow's local damping (too much Siberia/Alaska, too little Fennoscandia)", found by icemb).
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
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Glacial time zoom.
