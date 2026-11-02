# Religion stats, round 1 (PW-1311)

## In plain words

Fifteen peoples runs: 12 new ones made for this (the stock D&D and Seven Meals trees, seeds 1-3, on the two L6 worlds 4360a3 and af2677;
kept in scratch, not saved) and the three stored L7 runs b4d502, a24559 and 3c1caf (read only, their tech trees rebuilt in memory so they
have the faith steps). 2,738 living cultures in all. The tables below are made by `tools/religion_stats.py report`; this summary is mine.

- **Individuation is not a bell curve, it is steps.** Each faith tech sets a ceiling (burial 0.2, temples 0.45, kingship 0.6, high god 0.9),
  so the leading gods pile up just under each: 18% of cultures stop at burial spirits (about 0.2), 15% have temple powers, 46% kingship
  gods, 21% are on their way to a high god (0.75-0.85; none has reached 0.9 yet, the high god arrives late and individuation follows in
  ~3 kyr steps). Nobody is left at bare spirits: every living culture in these runs has at least burial. Chart: religion_stats_individuation.png.
- **Spells are common, which slice 1 did not intend.** Slice 1 said a people with temples and kingship but no high god would have one
  spell-granting god. In fact the kingship ceiling (0.6) is over the spell line (0.5) for every god whose devotion is near the leader's, so
  68% of cultures have three or more spell-granting gods, and 48% of all living gods grant spells. That follows from the tiers Daniel approved; whether
  spells should need more than "kingship" is a question for him (draft filed).
- **Pantheons are a narrow bump at 6.** Mean 6.1, median 6, range 2-14; 54% of cultures have exactly 6 (the 3 founding beings plus the
  smithing, death and ancestor powers that bronze and burial bring to nearly everyone). The 45 cultures with only 2 include storm giant
  cultures (the first examples in the odd-cases table; why they lost a founding god is not yet looked into). Chart: religion_stats_pantheon.png.
- **Taboos: 16 per culture** (median 16, 6 to 24; a near-normal spread). Every culture has food and kinship taboos; 95% the post-partum
  taboo (EA036 says 98% of societies have one); totemic taboos are the rarest (18%), rank, sumptuary and caste rules come only with
  kingship (68%, 64%, 35%). Chart: religion_stats_taboos.png.
- **Faiths are not cultures.** 106-236 faiths ever per run, 41-106 living; a living faith holds 2.7 cultures on average (median 1, largest 13-55).
  Conversions per run: 19-124. 6% of faiths ended while their cultures lived on (all converted or broke away); 81 living faiths span 3 or
  more peoples (a stem's faith carried down the culture tree, or spread by conversion).


## Leading god's individuation per culture (the tier it reached)

| tier | cultures | share |
|---|---|---|
| none | 0 | 0% |
| spirit (<0.15) | 0 | 0% |
| burial spirits (0.15-0.33) | 498 | 18% |
| temple powers (0.33-0.53) | 399 | 15% |
| kingship gods (0.53-0.75) | 1263 | 46% |
| high god (0.75+) | 578 | 21% |

All living beings: 16677; median individuation 0.49; 48% grant spells.

## Pantheon size (living beings per culture)

mean 6.1, median 6, min 2, max 14; cultures with no gods (no spirit ritual): 0.

| beings | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cultures | 0 | 0 | 45 | 43 | 127 | 340 | 1470 | 435 | 166 | 75 | 30 | 4 | 2 | 0 | 1 | 0 |

## Taboos per culture

mean 16.0, median 16, min 6, max 24.

| kind | cultures with one | share | rules in all |
|---|---|---|---|
| food | 2738 | 100% | 9851 |
| kinship | 2738 | 100% | 5604 |
| purity | 2605 | 95% | 3662 |
| postpartum | 2595 | 95% | 2595 |
| place | 2542 | 93% | 3486 |
| speech | 2538 | 93% | 3542 |
| time | 2436 | 89% | 3409 |
| women | 2181 | 80% | 3065 |
| rank | 1863 | 68% | 2593 |
| sumptuary | 1739 | 64% | 2389 |
| resource | 1038 | 38% | 1449 |
| caste | 950 | 35% | 1343 |
| totemic | 505 | 18% | 713 |

## Faiths

| run | tree | cultures | faiths ever | living | founded | schisms | conversions | died out with no followers | largest now (cultures) |
|---|---|---|---|---|---|---|---|---|---|
| 03fc60 | seven_meals | 155 | 146 | 63 | 95 | 51 | 62 | 10 | 13 |
| 308bcd | dnd | 144 | 106 | 53 | 64 | 42 | 29 | 6 | 17 |
| 3c1caf | stored | 332 | 236 | 103 | 107 | 129 | 124 | 19 | 44 |
| 4e53b6 | seven_meals | 148 | 133 | 56 | 94 | 39 | 50 | 7 | 23 |
| 52a691 | dnd | 146 | 104 | 41 | 71 | 33 | 57 | 15 | 22 |
| 91e886 | dnd | 145 | 130 | 63 | 73 | 57 | 35 | 11 | 18 |
| 9720b3 | seven_meals | 147 | 133 | 64 | 87 | 46 | 51 | 11 | 17 |
| 9c6749 | dnd | 175 | 136 | 69 | 81 | 55 | 39 | 10 | 22 |
| a24559 | stored | 305 | 189 | 106 | 83 | 106 | 54 | 5 | 39 |
| b4d502 | stored | 298 | 205 | 95 | 101 | 104 | 20 | 4 | 55 |
| c5f83a | dnd | 157 | 159 | 66 | 94 | 65 | 35 | 10 | 25 |
| dd778e | seven_meals | 141 | 131 | 51 | 95 | 36 | 40 | 7 | 16 |
| f25339 | dnd | 132 | 114 | 51 | 78 | 36 | 19 | 6 | 14 |
| f4a4c3 | seven_meals | 148 | 133 | 62 | 90 | 43 | 84 | 10 | 17 |
| f992e1 | seven_meals | 165 | 151 | 72 | 93 | 58 | 72 | 10 | 25 |

Living faiths hold 2.7 cultures on average (median 1, max 55).

## Odd cases (counts, with up to three examples each)

| case | count | share of cultures or faiths | examples |
|---|---|---|---|
| three or more spell-granting gods in one culture | 1858 | 67.9% | first aarakocra of the east of Ramuhos (5, 03fc60); first antelope-kin of the north of Taroma (5, 03fc60); first cervid-kin of the south of Taroma (5, 03fc60) |
| 22 taboos or more | 47 | 1.7% | first kobolds of Kagus (22, 03fc60); first dragonborn of the east of Ramuhos (22, 03fc60); steppe kobolds of the north of Kagus (23, 03fc60) |
| 8 taboos or fewer | 15 | 0.5% | first blue dragons of the north-west of Taroma (8, 03fc60); first storm giants of the south of Kagus (8, 308bcd); first elves of the east of Taroma (8, 308bcd) |
| fewer than 3 living gods (a culture is founded with 3) | 45 | 1.6% | storm giants of the south of Shuthetroth (2, 03fc60); storm giants of the north-west of Kagus (2, 03fc60); storm giants of the south of Thobro (2, 03fc60) |
| 12 or more living gods (the cap is 15) | 3 | 0.1% | first lizardfolk of the south of Munin (14, 3c1caf); desert lizardfolk of Luki (3) (12, 3c1caf); savanna lizardfolk of Munin (2) (12, 3c1caf) |
| a living faith across 3 or more peoples | 81 | 3.7% | the mountain faith of first aarakocra of the east of Ramuhos (5 peoples, 03fc60); the mountain faith of first stone giants of the north-west of Kagus (4 peoples, 03fc60); the desert schism of first antelope-kin of the north of Taroma (3 peoples, 03fc60) |
| a faith whose core moved twice or more | 148 | 6.7% | the fire faith of first cervid-kin of the south of Taroma (03fc60); the river faith of first black dragons of the west of Taroma (03fc60); the forest faith of first goblins of the east of Taroma (03fc60) |
| a faith that ended while its cultures lived on (all converted or broke away) | 141 | 6.4% | the hunt faith of first merfolk of the east of Taroma (03fc60); the river faith of first black dragons of the west of Taroma (03fc60); the sun faith of first blue dragons of the north-west of Taroma (03fc60) |

Charts: `religion_stats_individuation.png`, `religion_stats_pantheon.png`, `religion_stats_taboos.png`.
