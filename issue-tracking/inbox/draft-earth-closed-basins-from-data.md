---
title: "Earth world: inland drainage fell to 8% once the gorge dams went (PW-236); take closed basins from HydroSHEDS' sinks?"
type: task
status: needs-decision
parent: null
subsystem: hydrology
effort: s
impact: med
found_by: pw236-gorges
blocked_by: []
relates: [PW-236, PW-055, PW-054]
refs: [tools/earth_data.py, tools/earth_world.py, planet/hydrology.py]
---

## Description
PW-236 gave the Earth world (and earth_check) river heights from HydroSHEDS
(`earth_data.earth_outlets`), so gorge rivers no longer leave cell-mean dams. All the
target fake lakes drain, the real ones stay, but land draining inland (L6 Earth world,
excl. Antarctica) fell 11.6% -> 8.1% (earth_check's routing: 18% -> 15%). What drained
was fake per the data (HydroSHEDS inland share of the region in brackets): Sichuan /
upper Yangtze 1.76 Mkm2 (0.02), Mongolia's Hulun / Kherlen basin 1.25 (0.53, half of it
really closed: the Gobi and the Great Lakes Depression drain to their own sinks, which
the cell means don't resolve as hollows), Pannonia 0.46 (0.00), the Colorado Plateau 0.44
(0.14), Thar 0.34 (0.05), Junggar 0.16 (0.22), a Yenisei tributary 0.10 (0.00). So the
old 12% held partly for the wrong reasons; HydroSHEDS has ~22% of the cells mostly
inland. The coordinator's guard was "~12% stays".

Options:
- A. Accept 8% (the model's closed basins are what L6 cell means hold; PW-054 already
  tracks closed basins being too few on generated worlds).
- B. Earth only, data: also take the closed basins from HydroSHEDS' sinks
  (`hydrosheds_rivers(grid)["inland"]` is already cached per cell): cells that drain
  mostly inland there end their rivers (a `sink` input to lakes/route, as the outlet
  heights are an input). Sound (observed drainage, no named regions), a few lines in
  hydrology plus the Earth tools; would bring inland drainage to ~20% and make the
  Gobi, Great Basin, Arabia and the Sahara's sinks closed in the Earth world.
- C. Keep the outlet heights only where they open a basin HydroSHEDS also drains to
  the sea (as now) and look for why the Mongolian cells lose their closure (they are
  protected, but the closed lake they ended in, Hulun, now drains through the Argun).

Lean: B, since the Earth world is a data analogue and the closures are data too.
