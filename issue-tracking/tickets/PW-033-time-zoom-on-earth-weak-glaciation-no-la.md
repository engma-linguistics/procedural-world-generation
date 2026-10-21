---
id: PW-033
title: "Time zoom on Earth: weak glaciation, no Laurentide or Fennoscandian ice"
type: task
status: todo
parent: PW-470
subsystem: timezoom
effort: l
impact: med
found_by: timezoom
blocked_by: []
relates: [PW-038]
refs: [planet/timezoom.py, tools/earth_data.py, planet/icemass.py, planet/timezoom_kernels.py]
created: 2026-10-14
updated: 2026-10-20
---

## Description
On our model's Earth climate the time zoom reaches only −52 m at 150 kyr (LGM ~−120 m). Labrador and
Baffin summers are ~5 °C too warm, so no Laurentide inception; Tibet, Karakoram and the Altiplano grow
ice caps, and Cordillera and Alaska ice is too big. On the observed climate baseline there is no
Fennoscandian ice. Calibration target (from the spec): Laurentide/Fennoscandian-like ice and ~−100 m at
the cold peaks over ~150 kyr.

## Updates
- 2026-10-20: pw460: both diagnosed causes (margin height, insol_k) confirmed in the zoom: margin-only obs reaches -82 m with a Laurentide to 44.9 N. Blocked on the run deglaciating (PW-461).
- 2026-10-20: pw033: diagnosis in docs/review/audit/PW-033-diagnosis.md, no fix merged. The glacials are precession heartbeats (300 -> 314 -> 326 kyr: +3 -> -45 -> -12 m), and no sheet survives a warm half-cycle. Ranked: (1) margin cells melt at edge_h 408 m against the cell's ~900 m Nye mean (edge_h 900: -98 m; with baseline=obs a 5.0 Mkm2 Laurentide to 46.6 N), but it is shared with the run and the zoom alone breaks the consistency test (-46 m); (2) insol_k 0.25 is ~3x the seasons' 0.08-0.09 C per W/m2 (0.10: -62 m); (3) the overturning sinks 4 Sv in Baffin Bay, the Norwegian Sea freezes, and Fennoscandia is -18 C in January (its ice is a cold-bias artefact); (4) E Canada is winter-dry and summer-warm (Labrador snowfall 236 vs 408 mm). Mass-balance physics (DDF 3/8, refreeze, Ohmura-consistent snowline) and Hudson Bay are fine. Needs-decision drafts for (1) and (2), climate/ocean drafts for (3) and (4).
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
