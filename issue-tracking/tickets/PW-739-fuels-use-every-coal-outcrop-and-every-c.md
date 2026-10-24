---
id: PW-739
title: "Fuels use every coal outcrop and every cell's own supply: coal known by a people's era and tech, fuels in trade, and the zooms"
type: task
status: todo
parent: PW-692
milestone: v3
subsystem: timezoom
effort: m
impact: med
found_by: fun7
blocked_by: []
relates: [PW-722, PW-714, PW-675, PW-661]
refs: [planet/lineages/fuels.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
`fuels.mix` (PW-722) is a crude, per-cell, present-only reading: the share of each fuel is its availability (0..1) times how good
it is to cook over (`PREF`), from the tree cover left, pasture and cropland, herd animals known, the world's peat thickness,
the staples' straw and the coal likelihood. What it leaves out, each a follow-up:
- coal is burned wherever the world has an outcrop (`res_coal` 0.3-0.7) and anyone settled there; it should need a people to know
  it (PW-714 outcrops, the tech tree PW-675 and era PW-690/PW-661); the preset era `renaissance` makes it fine today;
- fuels are not traded: a treeless coast far from coal and peat never imports charcoal or wood; a trade pass (PW-692 item 2) could move them;
- charcoal is a fixed share of the wood burned by dense settlement (smiths, towns); it should follow metal users and the miners' ores;
- no seasons (winter dung/peat stores vs summer brush), no heating-vs-cooking split, no cooking style (low slow dung fires vs
  hot wood fires) as a data row for the culinary pass;
- the zooms (PW-103) carry the people's run layers only through `zoom_peoples`; a fuel layer on zooms would need the same
  reading at 1-4 km/px;
- the per-biome table is a check, not a fit: steppe dung ~50%, forest wood ~50%, bog peat; `PREF` weights are judgement.
- [ ] coal known by era and tech; fuel trade; cooking-style row per fuel

## Updates
- 2026-10-24: Also add the fat fuels: seal and whale oil (arctic lamps), tallow and rendered fat (goliaths, PW-730), and bone where wood is scarce; tundra's 60% 'grass' should read heath and dwarf shrub.
- 2026-10-24: Created from inbox draft draft-fuels-coal-known-era-and-trade.md (found by fun7).
