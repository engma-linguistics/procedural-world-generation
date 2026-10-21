---
id: PW-519
title: Recessional moraine belts at ice-thickness contours are a heuristic; use the deglaciation history
type: task
status: todo
parent: null
milestone: later
subsystem: zoom
effort: m
impact: low
found_by: pw512
blocked_by: []
relates: [PW-512, PW-499, PW-470]
refs: [planet/zoom_glacial.py, "zoom a44e9f", "zoom 9213a8"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Where a sheet's margin is out of view (Ungava a44e9f is 100% iced), the zoom puts recessional moraines at fixed contours of the thickest ice (RECESS_ICE_M = 1100 and 1900 m) so there are dams to hold lakes (9 moraine-dammed lakes at Ungava). Real stands are set by the climate during the retreat, not by thickness; and in the Baltic zoom the same contours run as straight belts across the Scandes. The world doesn't store the retreat (PW-499: `wet_kyr`, when the ice left). When the imprint carries the retreat (the time at which each cell lost its ice), place the belts at the contours of that field instead, and drop the thickness levels.
- [ ] belts follow the retreat contours; Ungava still shows >= 3 moraine-dammed lakes

## Updates
- 2026-10-21: Created from inbox draft draft-glacial-recessional-moraine-contours.md (found by pw512).
