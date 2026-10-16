---
title: "Soils: peat outranks alluvium on active floodplains, so zoom rivers are lined with peat"
type: task
status: needs-decision
parent: PW-184
subsystem: surface
effort: s
impact: low
found_by: zoom-soils
blocked_by: []
relates: [PW-185, PW-331, PW-212]
refs: [planet/soils.py, planet/zoom_vegetation.py, docs/review/soils/zoom_river.png]
---

## Description
`soils.organic` grows peat on the whole flooded share (vegetation's `fw`, which includes the big rivers' floodplains)
and the classification tests peat before alluvium. In the zoom (PW-331) a big river's own pixels flood most (fw up to
0.75), so on humid worlds the pixels along a ≥ 300 m^3/s river are 19-35% peat and 43-69% alluvium (400 km zooms of
an L7 world, `tools/zoom_soil_check.py`, `mix_big_river_plain`), and the rivers show as dark peat ribbons
(docs/review/soils/zoom_river.png). On Earth active floodplains, where each flood lays fresh silt, are Fluvisols and
Gleysols; peat forms in backswamps, oxbows and beyond the levees, where no silt comes.

Options:
- (A) Keep: the 2 km river pixel includes its backswamps, and tropical peat swamps do flank big rivers.
- (B) The peat's input times (1 - alluvial share) in `organic` (silt buries and aerates the litter), for worlds and
  zooms alike; re-run `tools/soil_check.py` (peat area, PW-330) since world floodplain cells lose some peat.
- (C) Only on zoom pixels (the river pixel is the active floodplain there): no world change, but a zoom-only rule.

Lean B: one rule at both scales, small world change.
