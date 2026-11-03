---
id: PW-1385
title: "Farm or forage per cell: a people farms or herds a cell only where that clearly out-feeds foraging there"
type: task
status: in-progress
parent: null
milestone: v2
subsystem: food
effort: m
impact: med
found_by: Daniel 11-02
blocked_by: []
relates: [PW-1373]
refs: ["planet/lineages/ladder.py::Ladder.line", docs/review/peoples/density-ladder/ladder.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: today a people that knows crops farms all the farmable land in every cell it holds (ladder.py::line: farmable share farmed, grazable herded, only the rest foraged), so foragers survive only on marginal land. Real foragers also held on where wild food was rich enough that farming wasn't worth the extra work (salmon coasts, acorn woods). Daniel 11-02 agreed: a cell is farmed or herded only where that feeds clearly more people than foraging or fishing there, by a sourced margin standing for farming's extra labour; any people can have such foraging portions (humans did). Target picture: roughly 1500 AD, where the tech tree ends (foragers still holding large regions, rare but real in rich and marginal land). The kind's inclination stays as a small delay in learning crops (PW-1373). Source the margin before building (labour returns of foraging vs early farming); measure the forager share of land and people by biome on the robust suite.

## Updates
- 2026-11-02: Status todo -> in-progress. Daniel 11-02 picked A: rich wild land resists farming (where wild food per person is well above the usual forager level, crops are taken up much more slowly or only on part of the land), strength sourced from the Pacific Northwest and California cases. B (crowding drives farming) filed as an investigation, PW-1388.
- 2026-11-02: Lane 139 sizing: density against density never bites for farming. 0% of farmed people sit where the wild rung reaches half the farm density (farm 5-35/km2 vs forager 0.01-0.4, fisher <= 1.2). Real rich foragers stayed so on returns per person (work), not on people per km2, so the comparison has to be per-capita returns or labour, not density. Herding does overlap on cold/dry land (subarctic 68%, polar 49-63%, steppe 18-19%). Needs a design pass and Daniel before building.
- 2026-11-02: Created.
