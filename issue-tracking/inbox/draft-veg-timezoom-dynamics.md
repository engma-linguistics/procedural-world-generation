---
title: "Vegetation in the glacial time zoom (PW-187 step 7): dynamic cover with migration, refugia, frames; finished worlds start from it"
type: story
status: todo
parent: PW-184
subsystem: timezoom
effort: m
impact: med
found_by: veg
blocked_by: []
relates: [PW-187, PW-091]
refs: [planet/vegetation.py, planet/timezoom.py, planet/finish.py, docs/proposals/vegetation.md]
---

## Description
Step 7 of the vegetation proposal (section 3.5). `vegetation.equilibrium` already steps the cover equations (`_step`, implicit, with fire and a neighbour spread `diff`); the time zoom needs it in real years (500 yr steps) with migration instead of seeds everywhere: a PFT may establish only from neighbours that have it (100-500 m/yr, ~1 L6 cell per 200-1100 yr), new ice-free ground starts bare, potential NPP refreshed at each 10 kyr climate refresh. Record refugia (cells that kept forest through a glacial) for PW-103. Frames: vegetation and tree_cover per 2 kyr frame (41 MB/Myr at L6).
Today a finished world (PW-091, finish.py via timeline.world_from_frame with a state) starts its vegetation from the source run's keyframe tree cover and re-equilibrates to the time zoom's climate; with step 7 it should start from the time zoom's own vegetation at that kyr and not re-equilibrate (keeping the disequilibrium).
