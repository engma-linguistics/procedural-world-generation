---
id: PW-955
title: Worlds keep isolated deep 'sea' cells among polar high ground (world 2a7385, -82 S)
type: task
status: todo
parent: null
milestone: null
subsystem: surface
effort: s
impact: low
found_by: physics-lane-21
blocked_by: []
relates: [PW-844]
refs: [planet/world.py, planet/geo.py, "world 2a7385", "zoom 1ab4c4", docs/review/zoom/pw844/]
created: 2026-10-28
updated: 2026-10-28
---

## Description
Zoom 1ab4c4 of world 2a7385 (500 km at 1 km/px, centred -82.08, -122.91) contains twelve pits of sea water
(1-638 px). None of them touches the zoom's edge. Each sits inside 2.7-3.5 km high, ice-ringed ground, and the
world counts the coarse cell under the largest (about -4.4 km) as sea. Lane 21 fixed what the zoom did with
those cells (PW-844): their sea floor had been driven to -23 km, and 581 pixels were called harbours. The cells
themselves are still odd. A basin that deep, closed off from the ocean, would be a lake or a dry or ice-filled
basin, not open sea. It is also a sub-sea bed under grounded ice that `world_land` might not be reading as land.

What to try: list the sea cells of a few L7 worlds that have no sea neighbour, or whose connected sea is smaller
than a few cells. Find out whether they are beds under ice (land, by the `world_land` rule) or truly open
water. If they are open water, decide whether the run should fill them as lakes.
- [ ] a count of such cells on 3+ worlds, and what they are

## Updates
- 2026-10-28: Created from inbox draft draft-sea-pits-among-high-ground.md (found by physics-lane-21).
