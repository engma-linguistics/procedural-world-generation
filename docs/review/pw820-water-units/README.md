# PW-820: culinary water thresholds in physical units (scout 242)

## In plain words

The food side of the model decides who has fish runs, salt licks, salt-carrying rivers, lake fisheries, islands without
land predators, and how far a coast's or a mine's good reaches inland. Each of those used a number counted in grid cells:
"a river carrying 3 cells' worth of runoff", "a lake of 1 to 6 cells", "an island of 3 cells or fewer", "one ring of
cells inland". A cell is 12,452 km² at L6, 3,113 km² at L7, 778 km² at L8 and 195 km² at L9, so the same planet got a
different answer at each level: at L6 a river needed about 1,180 m³/s for a fish run, at L7 about 296 m³/s, and after a
refine to L8 it would need only about 74 m³/s.

The fix states every one of them in m³/s, km² or km, at the value it already had at L7 (the showcase level), so L7
worlds keep their answers and L6, L8 and L9 now ask the same physical question. Where a real-world figure exists it is
cited; where the grid sets a floor (a river or lake smaller than one cell can't exist on the grid) that is said.
Lowering a threshold to the real-world figure would loosen it, so those go to the owner as a decision, not into code.

## Inventory (before)

`flow` is the world layer of accumulated runoff in cells × m/yr; `hydrology.discharge` turns it into m³/s
(1 unit = 394.6 m³/s at L6, 98.6 at L7, 24.7 at L8, 6.2 at L9). One neighbour step is 120 km at L6, 60 km at L7.

| Where | Constant | Old (cell units) | L6 meaning | L7 meaning | Used for |
|---|---|---|---|---|---|
| lineages/seafood.py | RUN_FLOW | 3.0 flow, ramp top 30 | 1,184 / 11,840 m³/s | 296 / 2,959 m³/s | a river large enough for an anadromous run |
| lineages/seafood.py | RUN_LOSS | 0.96 kept per cell upstream | e-fold 2,950 km | e-fold 1,474 km | how far a run carries upstream |
| lineages/seafood.py | LICK_FLOW | 2.0 flow | 789 m³/s | 197 m³/s | a river big enough to cut sodium clays bare (mineral lick) |
| lineages/seafood.py | LAKE_CELLS | 1 to 6 cells | 12,452 to 74,700 km² | 3,113 to 18,680 km² | a lake from a poor to a full fishery |
| lineages/seafood.py | `_sea_to_coast(..., 2)` for fish_sea and whales | 2 rings | 240 km | 120 km | how far offshore a coast's fish and whales are read |
| lineages/salt_reach.py | RIVER_FLOW | 2.0 flow | 789 m³/s | 197 m³/s | a river counts as a cheap salt route |
| lineages/land.py | `_reach` | 1 ring | 120 km | 60 km | a point-like good (ores, salt, fish, coasts) reaches the country around it |
| lineages/ladder.py | WATER_FLOW | 5 to 200 flow | 1,973 to 78,900 m³/s | 493 to 19,730 m³/s | a river with a floodplain to water farms, to the greatest rivers |
| coastform.py | ISLAND_CELLS | ≤ 3 cells | ≤ 37,360 km² | ≤ 9,340 km² | an island free of land predators (seabirds, seals haul out) |

Already level-safe (not changed): `_salt_km` and `salt_reach.reach` (hop × spacing × km), SHELF_M (metres of depth),
`salt_sea`'s one ring (the sea next to the coast: adjacency, not a distance), crossing.py (quantile and km).

Found but out of scope (people mechanics, not water; one draft): ladder.RAID_REACH = 2 rings and BARTER_REACH = 1 ring,
compose.REACH_CELLS = 10, demes.MIN_CELLS = 40 and ADAPT_MIN_CELLS = 20, animals.OVERLAP_MIN = 3, history CHAIN_CELLS = 4.

## Diagnosis

1. The flow thresholds are the clear bug: at L6 they ask for a river four times bigger than at L7. A refine to L8/L9
   would make them four and sixteen times easier, so fish runs and licks would spread over every small stream.
2. The grid sets a floor. A single L6 land cell already sheds ~100 m³/s on its own (12,452 km² at ~0.25 m/yr of runoff),
   so a threshold under ~200 m³/s cannot be asked the same way at L6 and L7: L7 resolves smaller rivers that L6 cannot
   draw. The L7 values (200-300 m³/s) sit just above that floor, which is why they are kept rather than lowered to a
   salmon-stream figure.
3. Area thresholds have the same floor: a lake or island can't be smaller than one cell. A one-cell L6 landmass is
   12,452 km², bigger than the 9,340 km² island rule, so a straight conversion would remove every predator-free island
   at L6. The island rule therefore keeps a one-cell floor ("one cell, or under 9,400 km²").
4. Distances in rings: one ring inland is 60 km at L7, 120 km at L6; L6 cannot do half a ring, so it stays at one ring.
   The fix matters for L8/L9, where the same 60 km is two and four rings.

## Real-world anchors (fetched and read)

- Lake fisheries: FAO, *Models for estimating potential fish yields of African inland waters* (CIFA, ~1992),
  https://www.fao.org/4/u6650e/U6650E07.htm: catch = 8.32 × area^0.92 (t/yr, km², 71 lakes and reservoirs, R² 0.93);
  a 100 km² lake ~585 t/yr, a 1,000 km² lake ~4,900 t/yr. So lakes far smaller than the model's poor-fishery 3,150 km²
  carry real fisheries; the model's lakes start at one cell, so this is a needs-decision draft (lowering would loosen).
- Salmon rivers: Swift 1977, USGS OFR 77-422 (https://www.usgs.gov/publications/preferred-stream-discharges-salmon-spawning-and-rearing-washington):
  five salmon species spawn across 84 reaches of 28 ordinary Washington streams, i.e. runs do not need large rivers.
  L'Abée-Lund, Vøllestad & Beldring 2004 (Trans. Am. Fish. Soc., doi 10.1577/T03-108.1, abstract via search): salmon in
  158 Norwegian rivers of a wide range of mean discharge. Neither gives a minimum discharge; both say real runs reach
  rivers well under 300 m³/s. The 300 m³/s here is a grid floor (point 2), marked JUDGEMENT.
- No fetched source gives a predator-free island size, a run's upstream e-folding distance, a lick-forming discharge, or
  a floodplain-farming discharge: those are JUDGEMENT at their L7 values.

## The change (after)

| Constant | New | Exact L7 equivalent of the old | Source |
|---|---|---|---|
| seafood.RUN_Q | 300 to 3,000 m³/s | 296 to 2,959 | JUDGEMENT (grid floor; real runs reach far smaller rivers, Swift 1977) |
| seafood.RUN_EFOLD_KM | 1,475 km (per step: exp(-hop/1475)) | 1,474 | JUDGEMENT |
| seafood.LICK_Q | 200 m³/s | 197 | JUDGEMENT |
| seafood.LAKE_KM2 | 3,150 to 18,700 km² | 3,113 to 18,680 | JUDGEMENT (FAO: 100 km² lakes already fish ~585 t/yr; draft) |
| seafood.SEA_REACH_KM | 120 km (rings_for: 1 at L6, 2 at L7, 4 at L8) | 120 | JUDGEMENT |
| salt_reach.RIVER_Q | 200 m³/s | 197 | JUDGEMENT |
| land.REACH_KM | 60 km (1 ring at L6 and L7, 2 at L8, 4 at L9) | 60 | JUDGEMENT |
| ladder.WATER_Q | 500 to 20,000 m³/s (log ramp) | 493 to 19,730 | JUDGEMENT |
| coastform.ISLAND_KM2 | ≤ 9,400 km², or a single cell | 9,340 | JUDGEMENT |

Every new value is the old L7 value rounded the tightening way (a river must be a little bigger, a lake a little bigger,
a run carries 1 km further in 1,475): nothing is loosened at L7. At L6 the flow rules ask for a quarter of what they did
(the same m³/s), the island rule shrinks from 37,360 km² to one cell, and the sea's fish and whales are read one ring out
instead of two. At L8/L9 everything is held to the L7 physical value instead of loosening four- and sixteen-fold.

## L6/L7 (and L7/L8) agreement on the same ground

Same ground: an L6 world and `planet refine` of it to L7 (the L7 terrain keeps each L6 cell's land and mean height, and
the climate is run on the L6 grid; rivers, lakes and islands are redrawn on the L7 cells). Also the showcase world 899985
(L7) refined to L8. All under a scratch PLANET_DATA. Regions are 150 pseudo-cultures: the coarse land split by the
nearest of 150 random land cells (seed 1), each fine cell taking its parent's region (about the size of a peoples run's
cultures: 207-264 per world). "agree" is the share of regions where both levels say the same (holds the good or not).
Script: `tools/water_units_check.py <coarse> <fine>`; numbers from main cbc86bdf and this branch.

| pair | good | regions coarse/fine main | branch | agree main | branch |
|---|---|---|---|---|---|
| 4360a3 L6 / ab32aa L7 | fish run | 98 / 119 | 119 / 119 | 0.833 | 0.907 |
| | strong run (>0.3) | 53 / 79 | 76 / 79 | 0.773 | 0.913 |
| | lake fishery | 8 / 30 | 8 / 30 | 0.813 | 0.813 |
| | full lake fishery (>0.6) | 1 / 21 | 8 / 21 | 0.867 | 0.873 |
| | sea fish (>0.3) | 99 / 111 | 97 / 111 | 0.893 | 0.893 |
| | salt lick | 100 / 127 | 122 / 127 | 0.820 | 0.940 |
| | salt within 100 km | 132 / 145 | 141 / 145 | 0.913 | 0.973 |
| | predator-free island | 15 / 16 | 14 / 16 | 0.927 | 0.933 |
| 28442c L6 / b89340 L7 | fish run | 116 / 123 | 131 / 123 | 0.833 | 0.893 |
| | strong run | 57 / 68 | 66 / 68 | 0.793 | 0.920 |
| | lake fishery | 19 / 36 | 23 / 36 | 0.873 | 0.860 |
| | full lake fishery | 3 / 31 | 19 / 31 | 0.813 | 0.867 |
| | sea fish | 92 / 95 | 91 / 95 | 0.940 | 0.933 |
| | salt lick | 92 / 109 | 113 / 109 | 0.847 | 0.893 |
| | salt within 100 km | 128 / 139 | 131 / 139 | 0.927 | 0.947 |
| | island | 14 / 13 | 12 / 13 | 0.953 | 0.967 |
| 899985 L7 / b81df5 L8 | fish run | 135 / 131 | 135 / 134 | 0.907 | 0.980 |
| | strong run | 101 / 113 | 101 / 101 | 0.853 | 0.960 |
| | lake fishery | 16 / 20 | 16 / 20 | 0.960 | 0.960 |
| | full lake fishery | 8 / 16 | 8 / 9 | 0.947 | 0.980 |
| | sea fish | 121 / 127 | 121 / 129 | 0.947 | 0.933 |
| | salt lick | 132 / 146 | 132 / 131 | 0.907 | 0.940 |
| | salt within 100 km | 149 / 149 | 149 / 149 | 1.000 | 1.000 |
| | island | 57 / 37 | 57 / 60 | 0.827 | 0.967 |

Tolerance (tools/water_units_check.py `TOL`): the lowest branch agreement per good over the three pairs, rounded down to
0.05: fish run 0.85, strong run 0.90, lake fishery 0.80, full lake 0.85, sea fish 0.85, salt lick 0.85, island 0.90.
Main fails five of the seven on at least one pair (fish run, strong run, full lake, salt lick, island); the branch passes all.
One region seed only: treat a 0.02-0.03 swing as noise.

What still differs, and why (not units):
- Lake fishery presence (0.81-0.87 either way): L7 draws lakes L6 cannot (a lake is at least one cell). The full-fishery
  count moves towards L7 (L6 1 -> 8 and 3 -> 19 regions against L7's 21 and 31).
- Land share is not comparable across levels for line features: a river or lick cell is a whole cell, so at L6 the same
  river covers four times the land (fish-run land share L6 0.33 against L7 0.15 on the branch, 0.15/0.15 on main only
  because main's L6 threshold was four times higher). Per-region (per-culture) answers are the right comparison.
- Sea fish is read 120 km offshore at L7 and L8 but still one 120 km ring at L6 (it was two, 240 km): slightly fewer L6
  coasts pass, no change in agreement.

## Before and after on stored peoples runs (L7, read-only)

Cultures on the last frame holding each good on any of their land cells (goods recomputed from each world; nothing written):

| run (world) | cultures | fish run | strong run | lake | full lake | sea fish | lick | salt ≤100 km | island |
|---|---|---|---|---|---|---|---|---|---|
| 07c755 (899985) | 264 | 217 | 138 | 32 | 21 | 164 | 188 | 243 | 68 |
| 3e0eb4 (dba204) | 260 | 210 -> 209 | 126 | 27 | 17 | 166 | 175 | 235 | 54 |
| de1cc6 (2762ba) | 209 | 166 | 121 -> 120 | 31 | 24 | 143 | 156 | 192 | 50 |
| 216848 (94cc8e) | 207 | 160 | 108 | 36 | 11 | 140 | 153 | 191 | 33 |

L7 is unchanged but for two cultures that lose a run at the 296 -> 300 m³/s rounding (the tightening side). There are no
stored L6 peoples runs; the L6 effect is the region table above. Seven Meals is untouched (no preset or tree changes).

## Also found (not changed)

- people mechanics in rings or cells: ladder.RAID_REACH (2) and BARTER_REACH (1), compose.REACH_CELLS (10), demes.MIN_CELLS
  (40) and ADAPT_MIN_CELLS (20), animals.OVERLAP_MIN (3), history CHAIN_CELLS (4) (draft filed).
- planet/language/inputs.py RIVER_FLOW = 50 says "m^3/s as stored", but `flow` is cells x m/yr (50 units is ~4,900 m³/s at
  L7). Language lane; in the same draft.
