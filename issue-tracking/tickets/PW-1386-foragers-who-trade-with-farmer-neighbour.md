---
id: PW-1386
title: "Foragers who trade with farmer neighbours: a capped top-up like the raiding share"
type: task
status: todo
parent: null
milestone: v2
subsystem: food
effort: s
impact: low
found_by: coordinator 11-02
blocked_by: []
relates: [PW-1379]
refs: ["planet/lineages/ladder.py::Ladder.line", "planet/lineages/ladder.py::Ladder.farmers_near", "planet/lineages/ladder.py::BARTER_CAP", "tools/peoples_robust.py::forage_land", docs/review/peoples/forager-trade/round1.md, docs/review/peoples/forager-trade/compare.py, "tests/test_lineages.py::test_foragers_trade_with_farmer_neighbours"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: some foragers live beside farming villages and trade forest goods (meat, honey, labour) for grain, as in the Congo forests or parts of SE Asia. Mechanically like the den peoples' raiding share (ladder.py RAID_*): a food share that grows with the farmers' density within reach, capped, here for forest foragers. Builds on the farm-or-forage choice; source the share first (the rainforest-foragers-and-farmers debate in the literature, not read yet).

## Updates
- 2026-11-03: Lane 146: sourced and built (ladder.py BARTER_*: cap 0.5 from Kitanishi 1995 p. 106 / Ichikawa 1983 p. 55; the half point and reach are judgements). Measured on 6 D&D robust runs against main: traded food 0.2-2.4% of forager peoples' food (most are coastal fishers or herders, which it does not top up), total people +0.01%, suite invariants hold. docs/review/peoples/forager-trade/round1.md.
- 2026-11-02: Planned right after PW-1385 lands (it builds on that choice); effort s once a share is sourced.
- 2026-11-02: Created.
