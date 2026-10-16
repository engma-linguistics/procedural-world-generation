---
title: "Vegetation: humid warm temperate forest turns into burning 'temperate scrub and thicket' under the shrubs' slow fuel (PW-234)"
type: task
status: todo
parent: null
subsystem: surface
effort: s
impact: med
found_by: vegbatch
blocked_by: []
relates: [PW-234, PW-220]
refs: [planet/vegetation.py, docs/review/vegetation/batch-2026-10-16.md]
---

## Description
Left after the sclerophyll summer-drought rule (owner decision C on the batch's draft). Since PW-234, shrubs' dead fuel decays at half the litter's rate and sclerophyll shrubs (SclS) survive 90% of fires. In humid climates SclS also stands in for the evergreen understory of warm temperate forests, and where those forests have a fire season, the shrubs' fuel feeds fire that kills the trees (TeBE 0.6, TeBS 0.3 survival) and the shrubs win: on the L7 world from run a1d3b9 @ 1000 Myr (keyframe), "temperate scrub and thicket" 602 -> 1910 cells (from warm temperate mixed forest and temperate woodland), mean tree cover 40.4 -> 37.1%; on Earth the Chaco (30-18 S, 66-56 W) has 11 thicket cells instead of 6, and obs forest (trees >= 60%) 48.7 -> 46.8 Mkm2.
What to try: the fire weather under a closed canopy (shade keeps the fuel bed moist, so a forest's fire season is shorter than the open ground's), or an understory shrub's fuel counted only where its canopy isn't shaded (its slow fuel builds in the open, not under trees). Check the savanna/forest boundary and the maquis (fire every ~25-50 yr, Mediterranean cells 127 on Earth) stay.
- [ ] L7 world tree cover back near 40% with maquis and Mediterranean cells kept
