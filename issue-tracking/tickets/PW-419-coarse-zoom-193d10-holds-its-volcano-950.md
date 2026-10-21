---
id: PW-419
title: Coarse zoom 193d10 holds its volcano ~950 m below top_m; fine zooms draw the cone over it
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: m
impact: med
found_by: pw395-volcano-form
blocked_by: []
relates: [PW-395, PW-394]
refs: [planet/zoom.py, planet/zoom_volcanoes.py, "zoom 193d10"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Zoom 193d10 (2 km/px) lists an active stratovolcano at 15.273, 15.445 with
top_m 3048 m, height_m 2266 m, but its summit pixel is 2092 m and its
neighbours 1800-1900 m: the cone (zoom_volcanoes: H exp(-x/r), r = H /
ARC_SLOPE = 3.8 km, pinned as young) has lost most of its volume by the end
of the zoom's pass (cell means, or the pass, take it down). A fine zoom can't
both keep that parent's means and stand a 31-degree cone to top_m: PW-395
draws the cone over the parent on its floor (top_m - height_m) and leaves it
out of the 3x3 means (drawn_cone_px ~7500 at 100 m; the means outside it are
kept). The fine zoom's mean ground is then ~6 m above the parent's.

Check where 193d10's cone volume goes (zoom.py's mean correction against the
world's cells, or the landscape pass despite `pin`), and keep the drawn cone
in the coarse zoom so nested zooms are consistent.
- [ ] a coarse zoom's pixel at a young volcano's summit is within ~10% of its height of top_m

## Updates
- 2026-10-16: Created from inbox draft draft-coarse-zoom-cone-below-summit.md (found by pw395-volcano-form).
