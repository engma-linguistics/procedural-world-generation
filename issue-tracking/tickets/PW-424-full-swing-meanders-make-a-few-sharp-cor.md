---
id: PW-424
title: Full-swing meanders make a few sharp corners where they meet a valley bend
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: pw412
blocked_by: []
relates: [PW-405, PW-412]
refs: [planet/zoom_fine.py, _courses, planform, "zoom 352c76 switchback_px (386, 406)"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Floors (PW-412) give the meanders their full swing. Their offsets now turn with the axis smoothed over a quarter wavelength. Even so, the `planform()` metric still counts 5 switchbacks in 54 km on 352c76 (0.096/km). Before floors it counted 1 (0.027/km). They sit where a loop meets a bend of the valley or a tributary's mouth, e.g. px (386, 406). There a loop's limb runs back almost parallel to the one before and makes a hairpin corner at pixel scale.

The swing is already limited by half the valley's bend radius over one wavelength (`room`), but only through a min over nodes, smoothed by a Gaussian. Options:
- also limit the swing by the axis's curvature at the loop's apex (the bend on the outside of the valley's turn);
- or shift the phase so that a valley bend falls at a crossing rather than at an apex.

Low impact: 5 corners in 54 km, at 25 m/px.

## Updates
- 2026-10-16: Created from inbox draft draft-meander-sharp-bends-at-valley-bends.md (found by pw412).
