---
id: PW-1342
title: "Matched land zoom: the coastline switches to the section's own at the ramp's middle (a jog where they differ)"
type: task
status: todo
parent: PW-1299
milestone: v2
subsystem: zoom
effort: m
impact: low
found_by: lane128
blocked_by: []
relates: [PW-1301]
refs: ["planet/zoom/match.py::coast", "planet/zoom/match.py::lakes", "planet/zoom/match.py::prepare", "planet/zoom/stage_terrain.py::coastline", docs/review/land-zoom/seams-round2.md, docs/review/land-zoom/seams.py, "zoom b710fd", "zoom 0852e2", "zoom 33a72a", "world dba204"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** A section built to match its neighbour takes the neighbour's coastline up to the middle of the
80 km blend strip, then its own. Where the two sections drew the coast a little differently, the coast has a small
jog at that middle line, 40 km inside the section. On the coast practice seam at 4 km/px (A b710fd, B matched 0852e2)
3.6% of points at +40 km disagree with the neighbour's coast (the line itself: 0.1%); on the other four seams it is
0-0.5%. Lakes switch the same way (`match.lakes`).

Seen only in numbers (`seams.py b710fd 0852e2 --owner --alone 33a72a`), not yet looked at in the viewer: first check
whether the jog is visible at 4 km and 1 km. If it is: blend the coastline indicator itself across the ramp
(`ind_n` towards a +-0.05 indicator of the neighbour's land, weight `m_w`) instead of switching at w = 0.5, so the
coast drifts from one outline to the other over the ramp; the heights already blend.
- [ ] look at the coast seam's ramp in the viewer at 4 km and 1 km
- [ ] if visible: coast mismatch at +40 km on the coast seam under ~1%, no new stubs or islands in the ramp

## Updates
- 2026-11-02: Created from inbox draft draft-land-zoom-coast-switch-mid-ramp.md (found by lane128).
