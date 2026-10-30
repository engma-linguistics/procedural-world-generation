---
title: "Ore 'districts' cover ~46% of land: the mining threshold reads a deposit likelihood as a district"
type: task
status: needs-decision
parent: PW-856
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-72
blocked_by: []
relates: [PW-1116, PW-1131]
refs: [planet/lineages/mining.py, planet/lineages/land.py, planet/resources.py, planet/lineages/settlements.py, planet/lineages/techtree.py, "world 4360a3"]
---

## Description
In plain words. In the sim, "mining country" is nearly half the land, so being drawn to it means almost nothing. On
Earth, ore districts are rare and clustered. The peoples code treats any cell whose best ore good is 0.5 or more as an
ore district (mining.ORE_MIN = land.DISTRICT_MIN = 0.5). On world 4360a3 that is 46.5% of the land.

Where it comes from (lane 72, world 4360a3, shares of land):
- The resource layers (res_*) are each a per-cell likelihood that a deposit of that type lies in the cell. At L6 a cell
  is ~12,500 km^2, and porphyry copper alone reaches 0.5 on 10.8% of land.
- The goods take the best of several of these: `metal` is the best of gold, iron, copper, tin, nickel, bauxite and rare
  earths. So raw `metal` >= 0.5 already covers 35.7% of land, and the best ore good of all 38%.
- land._reach then carries each good one ring outward at 0.7 of its value, which adds about 8 points: 43.5% for
  `metal`, 46.5% for the best ore.
- At >= 0.75 the picture is Earth-like: the best ore covers 7.7% of land and `metal` 6.1%.

So the main cause is the threshold, not a broken layer. A likelihood of 0.5 that some deposit lies in a 12,500 km^2 cell
is plausible for any orogen; it is not a worked district. A smaller part comes from the layer definition: the max over
many deposit types, plus the one-ring reach. The reach is right for "a people settles around a mine", but wrong for
counting districts.

Who reads it: mining.ORE_MIN (settlements' mines, salt and ore miners in the brief, the history's land-use pull via the
goods), and techtree's deposit test (`deposit_min`).

Options:
- A. Raise ORE_MIN (mines and districts only) to 0.75 and count districts on the raw good, without the reach. The
  history's habitat pull is untouched, so no re-run. Settlements would have fewer deposit cells to choose from: the
  one-per-ring mine count drops (estimate 260-410 now, perhaps half), and colonies (COLONY_ORE) would follow.
- B. A: and also make the goods' ore pull read rich ore (see the companion draft on miners leaning to rich ore).
  This changes the history, so it waits for the next re-run.
- C. Keep 0.5. It reads as "ore-bearing country", and the one-per-ring rule already keeps the mine count down.

Lean: A now, B at the next history re-run. Owner check: is ~150-250 mining districts a world, each the best seam of a
~350 km ring, plausible? No source gives a world count. Mitterberg, the Great Orme, Hallstatt and Schwaz are each one
district on this reading.
- [ ] Owner: A, B or C
