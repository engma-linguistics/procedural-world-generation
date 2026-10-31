---
id: PW-1229
title: Below-sea-level pockets inside a continent count as sea, so big rivers (the L8 world's largest) end in 1-7-cell inland puddles
type: task
status: todo
parent: null
milestone: v2
subsystem: hydrology
effort: m
impact: high
found_by: lane96
blocked_by: []
relates: [PW-171, PW-950]
refs: [planet/geo.py, planet/hydrology.py, planet/highlights.py, "world a16f5a", "world 2a7385", "zoom 652c1a", docs/review/l8-world/explore.md]
created: 2026-10-31
updated: 2026-10-31
---

## Description
In plain words: anything below 0 m counts as sea, even a few cells sunk 1-2 m into the middle of a continent with no
way out to the ocean. At L8 the world's biggest river runs into one of these pockets about 800 km inland, and the
viewer's highlight "Largest river (its mouth)" and the regional zoom 652c1a were built on it.

`geo.is_land` is `elevation > 0` (or ice); nothing checks that a sea cell is connected to the world ocean.
Measured (lane 96, read-only, flood fill over the grid's neighbours):
- a16f5a (L8, 100 Myr): 225 sea bodies besides the world ocean, 205 of them 1-3 cells, median floor -2 m; 638 cells
  (0.50 Mkm2). Of the 66 river mouths with flow >= 300, **21 end in these detached pockets** (45 in the ocean),
  among them the world's #1 (cell 480006, -3.1/83.6, a 7-cell pocket) and #4 (231567, -1.9/-128.3, one cell).
  Screenshot: docs/review/l8-world/explore/05_largest_river_ends_inland.jpg.
- 2a7385 (L7, 792 Myr): 41 detached bodies, 216 cells (0.67 Mkm2), median floor -1333 m: the deep PW-171 pits,
  drawn and treated as sea.
At L8 the pockets sit in very flat lowlands at the sea's height (6.3% of a16f5a's land is 0-10 m, Earth ETOPO1 on
the L8 grid 1.4%; see draft-continents-rise-with-the-sea), so 30 km cells resolve many 1-2 m dips that 60 km
cells average away. On Earth, ground below sea level and cut off from it is a lake (Caspian, Dead Sea) or a dry
depression (Qattara, Death Valley), never sea.

What I'd try: label sea as the connected component(s) of `elevation <= 0` that touch the world ocean (or any
body above a size floor, for real inland seas joined by a sub-cell strait); hand the rest to hydrology.lakes as
closed hollows (they fill to a lake or stay a dry pan by the water balance). One place (geo.is_land / world
finish) so the coast, highlights, peoples and zooms all agree. Helps L7 too (its 41 deep pits).
- [ ] no river with flow >= 300 ends in a sea body that isn't connected to the ocean (a16f5a, 2a7385 re-sliced)
- [ ] the largest-river highlight's mouth is on the ocean or on a lake

## Updates
- 2026-10-31: Created from inbox draft draft-below-sea-pockets-inside-land-count-as-sea.md (found by lane96).
