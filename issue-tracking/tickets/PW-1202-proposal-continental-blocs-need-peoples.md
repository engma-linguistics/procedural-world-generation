---
id: PW-1202
title: "Proposal: continental blocs need peoples born apart and a home-ground edge; today every mammal people is born on one cradle continent and only humans leave it"
type: story
status: needs-decision
parent: null
milestone: v2
subsystem: peoples
effort: l
impact: high
found_by: lane84
blocked_by: []
relates: [PW-1180, PW-1181, PW-1184, PW-888]
refs: [planet/lineages/history/origins.py, planet/lineages/history/dispersal.py, planet/lineages/crossing.py, planet/lineages/samples/dnd.toml, docs/review/peoples-why/report.md]
created: 2026-10-31
updated: 2026-10-31
---

## In plain words
You want whole continents held by different sets of one to five peoples. Today the continents are blocky, but almost all the blocs
are human. On world 4360a3 (dnd, 8 seeds) humans lead 6-9 of the 10 continents and are at least 5% of the people on all 10. The
other blocs are always the same mix (kobolds, kenku, gnomes, dragonborn) on the reptile stem's own continent and two or three smaller
ones. Every mammal people (orcs, dwarves, halflings, hobgoblins, goblins, bugbears, tabaxi, leonin) is born on the same cradle continent
in 7 or 8 runs of 8. Only the humans leave it, by boat, and they then win the contest wherever they land.

## Description
Measured (lane 84, docs/review/peoples-why/report.md, section 2):
- Base dnd, 8 seeds: continents >= 1 Mkm²: 10; human-led 6-9; per continent the peoples making 90% of its people: median 2; distance
  of a continent's mix from the world's (half the summed share differences, people-weighted): 0.25-0.35.
- Humans without boats (sea_share 0.05, no seafaring trait on humans and their groups; 3 seeds): human-led continents 3-4 of 9, the
  distance 0.39-0.49, human share 67% -> 58%, human range 73 -> 46 Mkm².
- Why the mammal peoples share a cradle: a split founds inside, at the edge of or beside its parent's range (origins.py:265-321); the
  'across the sea' option weighs 0.6 x K x the crossing's reach and rarely wins. The root rule (origins.py:149-158) is the one rule
  that puts peoples apart, which is why the reptile/avian continent exists.
- Why humans get everywhere: sea_share 0.6 (seafarers 0.85, explore 0.8; dnd.toml:706, 769); long crossings land on any landmass the
  people does not yet hold where it has room (crossing.py:196); then the contest rules (PW-1180) and the stacked groups favour them.

Options (they stack):
- A. Allopatric splits: splits already go through `_by_landmass` (origins.py:302), but only over the landmasses their score
  reaches, and country across the sea weighs 0.6 x K x the crossing's reach, so the parent's own landmass nearly always wins. Give
  the 'across the sea' landmasses a real share of the draw (by habitable area, as for roots, times a reach that falls off more
  gently), so sister peoples are often born on different continents ("elves of the south").
- B. Home ground: a people that has held a landmass long weighs a newcomer's load more (an incumbency edge that grows with time held),
  so landings make coastal enclaves instead of takeovers.
- C. Late deep-sea craft for everyone: open-sea crossings only from a late date (the Austronesian and Norse scale is Holocene), straits
  and land bridges before.
- D. Authored homelands: a `start_land` / `start_near` hint per people (exists, origins.py:21-46), used in the preset.
Lean: A + B as rules (general for any tree), then check whether C is needed; D only for the preset's story.

## Updates
- 2026-10-31: Created from inbox draft draft-continental-blocs-cradle-and-sea.md (found by lane84).
