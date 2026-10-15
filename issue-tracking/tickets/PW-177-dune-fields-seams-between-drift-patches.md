---
id: PW-177
title: "Dune fields: seams between drift patches, network dunes, unresolved barchans"
type: task
status: todo
parent: PW-096
subsystem: zoom
effort: m
impact: low
found_by: zoomland3
blocked_by: []
relates: [PW-012]
refs: [planet/zoom_landforms.py, "zoom:2d1537", "zoom:e14044", "zoom:ee587f"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-012's Dunes synthesiser draws the big dunes (draas) at least 5 px
apart on planet-fixed ~200 km patches oriented by the sand drift. Left:
- where two patches meet the crests switch over a narrow wandering seam;
  where transverse and linear weights mix (RDP/DP ~0.75) the two patterns
  cross-hatch (zoom 2d1537, upper right): real mixed regimes make network
  or crescentic-linear dunes, which could be drawn instead;
- barchans are 0.1-0.5 km: a 0.5 km zoom shows only exaggerated crescents
  (ee587f: low and faint); a nested fine zoom (PW-129) would be the place;
- star dunes are radial-armed peaks on a lattice, all alike; their arms
  could follow the wind modes;
- dunes don't interact with the rivers that cross the erg (no blocked
  wadis or interdune lakes) nor climb the hills' windward sides.

## Updates
- 2026-10-14: Created from inbox draft draft-dune-detail.md (found by zoomland3).
