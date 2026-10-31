---
id: PW-1225
title: "Herd production by prey size: the offtake reads Farlow's turnover at one 0.5 t head everywhere; small-grazer country should give more, elephant country less"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: low
found_by: lane-90
blocked_by: []
relates: [PW-1072, PW-991]
refs: [planet/lineages/history/megafauna.py, planet/lineages/prey.py, docs/review/dragon-food-chain/report.md]
created: 2026-10-31
updated: 2026-10-31
---

## Description
**In plain words.** The wild herds now feed the hunters by how fast they breed, not a flat tenth a year. But the model has no idea how
big the grazers are in a place, so it uses one cattle-sized animal everywhere. Real herds of small antelope breed faster than herds of
buffalo and elephants, so country of small grazers should feed a few more dragons and country of giants a few fewer.

Lane 90 tied `megafauna.OFFTAKE` to production (PW-1072): Farlow 1993's turnover 0.94 M^-0.28 per yr (eq. 6, p. 172) at prey.HEAD_T
(0.5 t: 0.165/yr), x the share of production the predators kill (0.45, from Farlow's 100:1-200:1 against 50:1, p. 176, over the carcass
share). Coe, Cumming & Phillipson 1976's 24 areas run from 0.085 to 0.26 a year (Table 1, pp. 344-345), lowest where elephants and
buffalo hold most of the biomass (their size classes' assumed P/B 0.05 / 0.20 / 0.35, pp. 343-344).

What would do it: a per-cell mean prey mass (from the vegetation: open grassland and savanna carry big grazers, forest and desert small
browsers; or from the giants and the herders' stock), then turnover at that mass. Needs a source for the size structure by biome.
- [ ] a sourced mean large-herbivore mass by biome or by biomass
- [ ] OFFTAKE per cell from it

## Updates
- 2026-10-31: Created from inbox draft draft-prey-size-field-for-herd-turnover.md (found by lane-90).
