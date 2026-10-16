---
title: Fine zooms have no floodplains, so most lowland rivers count as confined and barely meander
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: med
found_by: pw405
blocked_by: []
relates: [PW-405, PW-404]
refs: [planet/zoom_fine.py, "_courses", "zoom 352c76 (scratch regen, 170672 -> 3453b8 -> 25 m)"]
---

## Description
PW-405 limits a meander train's swing by the valley floor's half width: where the parent's ground rises a couple of bankfull depths above the ground on the course. The fine landscape pass (stream-power profile from the imposed course) builds V valleys straight down to a 1-px channel. A floodplain never forms, even for a 300 m^3/s river at 0.04% slope. Such rivers come out "confined" and almost straight.

Example: 170672 -> 50 km @ 100 m (3453b8) -> 20 km @ 25 m. The 310 m^3/s river has a 0.04% bed and is alluvial and single-thread. Its parent floor is about 50 m wide, so it meanders only weakly: gentle sinuosity ~1.09 at q >= 10. On the open lowland of 3ac681 (980612 / b570c2), meanders do form.

Approach: along alluvial single-thread courses (the `_courses` classes), hold a flat floodplain at about bankfull level. Make it about the meander belt wide (2 x amplitude + w, at least ~10 w). The landscape pass then shapes hillslopes from the floodplain's edge. The planform's confinement test would then see the floor of a parent zoom made with this change.
- [ ] Watch the PW-389 3x3 block means: does the floodplain's missing volume go back onto the hills, or is it a drawn feature left out like gorges? Decide which.
- [ ] Lowland fine zooms show flat valley floors with meanders on them. Bedrock valleys stay V-shaped.
