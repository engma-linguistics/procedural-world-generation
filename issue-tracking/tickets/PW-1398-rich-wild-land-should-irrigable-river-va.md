---
id: PW-1398
title: "Rich wild land: should irrigable river valleys in dry land be exempt from the foragers' hold?"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: peoples
effort: s
impact: low
found_by: lane 141
blocked_by: []
relates: [PW-1385]
refs: ["planet/lineages/ladder.py::rich_keep", "planet/lineages/ladder.py::Ladder.line", "planet/lineages/ladder.py::WATER_MAX", docs/review/peoples/density-ladder/rich-foragers.md, docs/review/peoples/density-ladder/rich_foragers.py, docs/review/peoples/density-ladder/wild_overlap.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: since lane 141 (PW-1385 A), rich fishing waters keep part of their farmable land with foragers or fishers, a part
that shrinks over the millennia a people knows crops. On the robust suite (14 D&D runs, against main 4ae5191c at the same seeds)
farmed people fell 12% in deserts (781 to 688 million pooled) and 11% on steppe, more than in temperate land (4%). Some of that is
fish-rich rivers in dry land, which are exactly where irrigation farming began on Earth (Nile, Mesopotamia, Indus) and where
farming took everything. The rule compares the wild only with ordinary foraging, not with what the farm there would feed; an
irrigated valley feeds 30-240 people per km2 (Butzer), so the pull to farm it is far stronger than on rain-fed land.

Options:
- A: leave it (as built): a few desert-river fishers are plausible (Earth's Pacific coast of Peru fished anchovies beside farming
  valleys).
- B: exempt the watered share of a cell (ladder.water) from the hold once the people irrigates: irrigation farms in full.
- C: weigh the hold by the farm's own yield (the farm rung over the plough rung), which needs a sourced per-hour return for irrigation.

Lean A for now; B is a one-line change if the viewer shows empty river valleys beside irrigating peoples.

## Updates
- 2026-11-03: Created from inbox draft draft-rich-wild-irrigated-valleys.md (found by lane 141).
