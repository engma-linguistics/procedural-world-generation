---
id: PW-599
title: "Lineages: what the recent pass (last ~30 kyr at century steps) simulates"
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: lineages-lane
blocked_by: []
relates: [PW-103, PW-091]
refs: [planet/lineages/recent.py, docs/proposals/lineages.md, "recent pass 0a04f4"]
created: 2026-10-23
updated: 2026-10-23
---

## Description
`planet recent` (built) makes the finest time pass from a glacial time zoom: the time zoom's 2-kyr frames interpolated to 100-year steps, rain scaled from the source keyframe (or the finished world) by exp(0.07 dT), plus seeded variability acting on habitat only (red-noise global anomaly sd 0.35 C, tau 300 yr; regional cold spells and droughts ~1 per 6 kyr; a Younger Dryas-like reversal when the window holds a deglaciation). Ice and coastline are the time zoom's. Example: recent pass 0a04f4 (world 119973's time zoom 1224c2, last 30 kyr, 61 frames, 3.7 s at L6).

Options:
- A (built, lean): interpolation + variability. Cheap, consistent with the ice it came from, no physics-lane change. Centuries-scale ice (surges, fast retreat) can't show.
- B: re-run the time zoom's ice and climate at 100-yr steps over the window (true century ice; ~10x the time zoom's cost for the window; owned by the ice lane, parked until after v1, PW-470).
- C: A plus a full climate.compute every 2 kyr on the interpolated surface (better rain than the scaled keyframe's; ~1 min at L6).

Lean A now, C if the peoples' rain-driven habitat looks wrong on review. The episode rate (1 per 6 kyr gave 12 on one seed) may want tuning down.

## Updates
- 2026-10-23: Status needs-decision -> todo. Owner (2026-10-24): option C: interpolation + variability plus a full climate.compute every 2 kyr on the interpolated surface.
- 2026-10-23: Created from inbox draft draft-lineages-recent-physics.md (found by lineages-lane).
