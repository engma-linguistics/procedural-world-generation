---
title: Static prey (herbivore) biomass from absolute NPP, livestock included, feeding natural megafauna density and people density
type: story
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: [PW-833, PW-957, PW-963, PW-724, PW-207, PW-836]
refs: [planet/gameattrs.py, docs/proposals/megafauna-scaling.md, docs/references/megafauna/README.md]
---

## Description
Owner 2026-10-28 (megafauna side session). Nothing in the model knows how much prey there is. The game layers in gameattrs.py are relative 0-5 scores, but raw absolute NPP exists. Build one static field, computed once per cell, with **no predator-prey cycles** (owner: "just fit to what should work"):

1. **Wild herbivore biomass, t/km2**, from absolute NPP: the grazing-layer NPP (herb plus browse) through a published fit. Candidates are McNaughton et al. 1989 (Nature) and Coe, Cumming & Phillipson 1976; verify the papers first. Forest NPP is mostly wood, so forests hold less than savanna, as the grazing layer already says.
2. **Livestock counts as prey** where peoples herd or farm. Dragons are thinking creatures: they take cattle-sized prey readily, and later use tribute and kobold thralls. Prey therefore rarely limits dragons near peoples. Persecution does: the pressure term in PW-957 and PW-963.
3. **Megaherbivore overkill.** Wild big-herbivore biomass drops where small folk hunt densely, after their arrival (the real late-Pleistocene pattern; Sandom et al. 2014). It persists in country hostile to small folk: tundra and the mammoth steppe, high mountains, the open sea. There frost, cloud and storm giants herd or tend it (PW-724; culinary-dnd's frost giants are mammoth-steppe herders and whalers). Hill giants live among small folk, so they herd ordinary stock and raid. Overkill must not drive dragons to zero.
4. **Natural predator density** from prey. Carbone & Gittleman 2002: carnivores per 10 t of prey = 89.1·M^-1.05. Dragons use their ecological mass. For a 3.2 t dragon:

   | prey biomass | example country | natural density |
   |---|---|---|
   | 0.1 t/km² | desert | 1 per ~5,400 km² |
   | 1 t/km² | temperate forest | 1 per ~540 km² |
   | 5 t/km² | bison-era prairie | 1 per ~110 km² |
   | 10 t/km² | rich savanna | 1 per ~54 km² |

   Giants use the same rule by way of life.
5. **The same productivity base feeds people density** (PW-833, owner-approved): density = way-of-life factor × f(absolute NPP).

Cheap: arrays per cell, no time-stepped ecology.
