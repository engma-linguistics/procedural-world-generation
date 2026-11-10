# The split history on a refined L8 world (PW-1265, lane 267)

Daniel's 11-10 split: tectonics, ice ages, evolution, dispersal and languages stay on L7; the settled history (towns, states,
trade, war) runs on the finished world refined to L8. This note has the measured L7 and all-L8 tries (lane 266's first path),
the split's design, its conservation test and the split run, all on Earth-like A (world 899985, time zoom fc5311, dnd tree,
one try, seed 7) and its refined L8 world 5d09cc (lane 266 scratch root).

## 1. Measured: the whole history on L7 vs on L8 (lane 266's path)

Same code (this branch), Earth-like A, dnd tree, one try, seed 7. "History" is the try's own time (`meta.generated_in_s`);
"wall" adds the goods, the recent pass's full climates and every after-run stage (settlements, demes, cultures, gods,
languages).

| run | grid | history | wall | peak memory |
|---|---|---|---|---|
| ebd83a (on 899985, the L7 baseline) | L7, 163,842 cells | 1,238 s (21 min) | 1:08:22 | 11.6 GB |
| 025b98 (on 5d09cc, the split) | L7 to 12 kyr, then L8 (655,362 cells) | 3,316 s (55 min) | 1:56:41 | 35.5 GB |
| all-L8 (`--no-split`, lane 266's path) | L8 throughout | not measured | stopped by lane 267 at step 125/471 after 48:43 (15.2 GB) | |

The all-L8 run was skipped (3-4 h expected; optional in the brief). The split's history costs 2.7x the L7 one: its 121 L8 steps
take ~10 min per 25 steps against ~2 min per 25 coarse steps (progress lines, read by eye), so nearly all its time is the settled window. Its peak memory is 3x the L7 run's (35.5 GB against 11.6 GB), reached after
the history (the history alone peaked near 20 GB by `ps`); the wall time less the history (goods, full climates and every
after-run stage) is ~1 h against ~47 min on L7.

## 2. The cut

**The cut is the earliest drawn date of a first cultivation among the try's crops** (`history.handover.cut_kyr`: the largest
`animals.Stock.d0` over the crops this world has). Why there:
- Every settled mechanic in the code needs farmers. A crop can only be tamed at a step with `step.ago <= d0`
  (`animals.Stock.step`); a people's era leaves "forager" only once it takes a crop up (`history.growth._note_eras`); the
  live polities seat on sedentary heads, which are heads x the farm share of a non-forager people (`polity_live._heads`), and
  a dragon realm takes tribute only from cells with sedentary heads (`SEDENTARY_MIN`); the settlement ledger, trade and wars
  are made from the stored frames after the run, so they read the settled window's frames, which are all after the cut.
  So nothing a town, state, trade route or war reads exists before the cut, and everything it reads after it is on L8.
- The date is drawn when the History is made (Stock.__init__), so the cut is known before the run starts: no look-ahead, no
  second pass, the same for every grid.
- On Earth-like A seed 7 the cut is 12.0 kyr ago: sugar cane's drawn date, and the elves did first cultivate it at that very
  step in both the L7 run ebd83a and the split run 025b98 (wheat and barley follow at 10.7 kyr). Of the run's 471 steps, 350 run
  on L7 (20.3 Myr down to 12.5 kyr ago) and the last 121 (12.0 kyr ago to the present) on L8.
- A tree without crops never farms: the hand-over is then at the last step (the present), so the map is still on the
  world's grid. (A world whose peoples herd but never farm has no settled window in this model.)

## 3. The hand-over (`planet/lineages/history/handover.py`)

The run builds two recent passes: the coarse one on the world the refined world was made from (`meta.refined_from`, here
899985, with its own goods, rain, NPP and rivers) and the fine one on the refined world (lane 266's `recent.Pass` on the
world's grid, the time zoom's frames prolonged by `recent.finer`, the full climates on the zoom's L7 grid). Up to the cut
the History is exactly the L7 history of 899985 (same steps, same draws: the test checks the stored frames cell for cell). At
the first step at or after the cut, `hand_over` moves the History's state onto the fine grid and swaps in the fine Pass, the
fine goods and the fine world's steps for the rest of the run; the frames stored so far are put on the fine grid (each fine
cell shows its first parent's value: the coarse past as it was).

The grids nest (L8 = the L7 cells, same index, plus a cell on each L7 edge's midpoint; `nest.step`'s two parents per fine
cell). Each field by its kind:

| kind | rule | fields |
|---|---|---|
| a category | the fine cell's first parent (a kept cell: itself) | who leads a cell, contact holders, crop/animal routes, rung, polity owner, masks (`_last_held`, `_linger`), counts per cell |
| a quantity per area | the mean of the two parents (a kept cell keeps its own) | habitat shares (`_Kmat`, `_K_now`), fit, learned acceptance (`_Lm`, the learned country), a crop's or animal's knowledge (`rd`), density map (`_dmap`), contact presence, the brakes' K0 |
| a people's numbers | split by area, conserved exactly (below) | `h.p` for every people and megafauna line; overlays (a share of their hosts) take the mean |
| made again from the fine world | rebuilt, not carried | goods, the ladder's land (NPP, grazing, fish, fertile, ore, dens, water), the prey and sea-food fields, the landmasses (`Crossings`), the polities' neighbour and two-ring tables and site layers, cell sizes |
| landmass numbers in the record | renumbered: each coarse landmass to the fine landmass most of its cells carry | crossings reached, animals' and crops' landings, homelands, tamings |
| per-step caches | dropped, remade at the next step | the frontier cache, the present-epoch cache, overkill memo, density memo |

What is not per cell (the demes and cultures are made after the run; tech, attitudes, contacts' pair series, events,
tracks, eras, farm shares, every line's own numbers) carries over unchanged. Live polities (off by default, PW-1434) are
rebuilt on the fine grid with their non-cell state carried; at the cut none is seated yet, since they need farmers.

**Population conservation.** A people's heads per cell are presence (>= EST) x density x the grid's cell area (the history
counts every cell of a grid as equal: `geo.cell_area_km2`). `heads_split` shares each coarse cell's heads out by area in nest's
full weighting: the kept cell takes two half-slots, each midpoint round it one half-slot (a hexagon's heads: 1/4 to its own
fine cell, 1/8 to each of its six midpoints; a pentagon's 2/7 and 1/7). Each fine cell's presence is its heads over the mean of
its parents' densities and the fine cell area. A share that would fall under EST (a range edge's midpoint) would be counted as
nobody, so those heads go back to the parent's own fine cell. Totals are kept exactly per line:
`tests/test_lineages_split.py::test_heads_split_conserves_every_people_and_leaves_none_under_the_floor` (random presences,
densities and a thin line on L3 -> L4, rtol 1e-12), and the run records `meta.handover.people_before` / `people_after`.
The next step is the fine world's own: K, the ladder's density and the megafauna's local density are made on the fine land,
so cells the finer coast puts under the sea lose their people then, by the model, not by the move.

Equal levels: none of this runs (`run.run` only builds the fine pass when `meta.refined_from` names a world on a coarser
grid; `--no-split` keeps lane 266's all-on-the-world path).

## 4. The split run on 5d09cc

Run 025b98 (scratch root `l266/root`, world 5d09cc refined from 899985), against the L7 run ebd83a on 899985, same code, same
tree, try and seed. Both runs' towns are read on the same fine world 5d09cc (`docs/review/refine-l8/compare.py`), so an L7 town is judged on the
fine coast it would sit on.

**The cut and conservation.** `meta.handover`: cut 12.0 kyr, at step 350 (step ago 12.0); people before 15,167,457.52, after
15,167,457.52 (the same to 2e-9 people: the split conserves every line). These are the heads at the cut, when nobody farms.

**At the present** (baseline: ebd83a, the same world's history all on L7):

| | L7 ebd83a | split 025b98 |
|---|---|---|
| villages / towns / cities | 21,440 / 6,494 / 331 | 58,091 / 6,984 / 119 |
| towns and cities on the fine coast (the coast is 7.5% of the fine land) | 7.0% | 1.9% |
| ...on a navigable river of the fine world (37% of the fine land) | 30.4% | 36.0% |
| ...in the fine world's water | 0.95% | 0.00% |
| islands (< 0.3 Mkm2) with a town | 19 | 6 |
| peopled land share; lead peoples | 0.923; 33 | 0.916; 33 |
| people (all 46 lines, run.txt) | 1,069 million | 980 million (-8%) |
| humans; orcs | 694 M; 148 M | 564 M (-19%); 114 M (-23%) |

Pictures (top: the world; bottom: the boxed region; left L7, right split), `docs/review/refine-l8/side-*.png` with their
numbers in `side-*.json`:
- `side-river.png` (80-115E, 5S-25N, a big river valley): the plainest gain. On L8 the towns string out along the river's
  course and gather at its mouth (108E 13N); on L7 they are spread evenly over the basin, the river invisible. The interior
  between the rivers is emptier.
- `side-pass.png` (125-150E, 25S-5N, the neck between two land masses and the ranges behind it): towns line the narrow
  neck at 10S and the valleys inland follow the relief; on L7 they sit in a blob and dot the plateau. Borders between the
  peoples are finer-grained and follow the land.
- `side-coast.png` (80-40W, 50-25S, a coast with islands): breaks. The L7 run had dense towns and five cities on this
  peninsula; the split has a dozen towns, no city, and none on the offshore land. The thin land at 55-50W 35-28S that the L7
  frame carries is sea on the fine world.

**What improves:** towns follow rivers and relief (river share 30.4% -> 36.0%, at the river's share of the land; no town in
the water, against 0.95% of L7 towns that fall in the fine sea); the land, coasts and borders are drawn on 30 km cells (L7: 60 km).
**What breaks:** (1) towns shun the coast (1.9% of them on a coast that is 7.5% of the land; L7: 7.0%) and islands lose
their towns (19 -> 6); (2) cities fall from 331 to 119 while villages rise 2.7x: the ledger's tiers and footprints read
fixed rings and per-cell heads, so a quarter-area cell rarely makes a city. Both are the fixed-ring readings PW-1627 lists
(town footprints, coastal boat reach), now measured; (3) the present's people are 8% fewer (humans 19%), one draw only, so
not yet signal or chaos. The tech tree's town arms also warn "the ledger still moved after 3 rounds" on the split (not on
L7). Nothing absurd: no people in the sea, conservation exact, the map reads as the same world.

## 5. What it does not do (drafts)

- The ledger on L8 (coast, islands, cities): measured evidence for PW-1627, `issue-tracking/inbox/draft-l8-ledger-coast-cities.md`.
- The settled window grows fewer people on L8 (one draw): `issue-tracking/inbox/draft-l8-settled-window-fewer-people.md`.
- The all-L8 run (`--no-split`) was not timed: optional, 3-4 h expected.

## 6. After PW-1627's km rings and the refine's detail on the prolonged frames (lane 270)

Code 5bd8e407 (lane 270): the settled history's rings in km (TOWN_KM 60, CITY_KM 120, PIT_KM 60, COAST_BOAT_KM 120,
HEMMED_KM 120, the live history's ring table, ISLAND_FLOOR_KM2), and `recent.Pass.detail` (the split's prolonged L7 frames carry
the refined world's own elevation and temperature detail, so the settled window's present is the fine world's own coast).
Earth-like A, dnd tree, one try. Split run 727c35 on 69958b (899985 refined to L8) against the L7 run 2e0a95 on 899985,
**same code**; both read on the fine world 69958b with `compare.py` (box 80-40W, 50-25S, the coast-with-islands region of §4).
Scratch root `l270/root` (deleted after the lane). Column (b) is §4's split 025b98 on 5d09cc (older code, its own L7 run ebd83a).

| | (a) L7 2e0a95, same code | split 727c35 | (b) split 025b98, §4 (its L7 ebd83a) |
|---|---|---|---|
| villages / towns / cities | 22,399 / 6,170 / 283 | 57,473 / 5,228 / 244 | 58,091 / 6,984 / 119 (21,440 / 6,494 / 331) |
| towns and cities on the fine coast (7.5% of the fine land) | 7.3% | 4.2% | 1.9% (7.0%) |
| ...within ~60 km of the fine sea (13.2% of the fine land) | 14.8% | 8.8% | not measured |
| ...on a navigable river of the fine world | 34.4% | 34.6% | 36.0% (30.4%) |
| ...in the fine world's water | 1.1% | 0.0% | 0.00% (0.95%) |
| islands (< 0.3 Mkm2) with a town | 21 | 11 | 6 (19) |
| peopled land share; lead peoples | 0.923; 32 | 0.919; 33 | 0.916; 33 (0.923; 33) |
| people today (42 living lines, run.txt) | 1,043 million | 909 million (-13%) | 980 M (1,069 M) |
| humans; orcs (run.txt, two figures) | 660 M; 140 M | 430 M (-35%); 120 M | 564 M; 114 M (694 M; 148 M) |
| history; wall; peak memory | 1,267 s; 1:08:19; 11.3 GB | 3,544 s; 2:15:58; 37.5 GB | 3,316 s; 1:56:41; 35.5 GB |

The ~60 km band (`band.py` in the lane's scratch: towns by ring distance to the fine sea) checks that the coast share is
not just the narrower L8 coast cell: L7 towns sit at 1.1x the land's share of that band, the split's at 0.67x.

**Attribution** (the split run's ledger redone with `planet settlements 727c35 --set TOWN_KM=30 CITY_KM=60 PIT_KM=30`, the
old L8 ring counts, then restored; a control redo at the defaults reproduces the run's own ledger exactly). This redoes only
the ledger: the live history (polity_live's town and hemmed rings), the coastal boat reach and the island floor ran with km
in both, so it separates the ledger's rings from the coast fix, not every km change.

| split on 69958b | coast | islands with a town | cities | towns | villages |
|---|---|---|---|---|---|
| ledger at the old L8 rings (coast fix only) | 3.9% | 8 | 134 | 6,548 | 58,176 |
| ledger in km (as run) | 4.2% | 11 | 244 | 5,228 | 57,473 |

So the coast fix most likely carries most of the coast (1.9% -> 3.9%; §4's run is a sibling refine of the same world and a
separate draw, so this step is not a clean pair) and a little of
the islands (6 -> 8); the km rings carry the cities (134 -> 244: a city's hinterland is again ~120 km, so it gathers the
heads it did on L7) and the rest of the islands (8 -> 11), and thin the towns (6,548 -> 5,228: towns again stand ~60 km
apart, as on L7). Villages scale with the cell count by construction: 2.6x L7's on 4x the cells; reported, not tuned.

**Against the bar** (no worse than L7 beyond what the fine land changes): cities are close (244 vs 283, -14%), rivers and
water are as good or better. The coast is not: 4.2% on the coast and 8.8% within ~60 km, against 7.3% and 14.8% for the
same code on L7, and islands with a town 11 against 21. Not tuned toward L7 (no threshold moved). What remains is left on
PW-1630. One suspect is a grid-independent bug found on the way: the ledger's harbour bonus never fires on either grid
(`draft-ledger-harbour-on-sea-cells.md`), so ports lean on whatever else favours the coast, and that may read
differently at 30 km. The people today are 13% fewer on the split (humans 35%), against 8% (19%) in §4: still one draw
each (PW-1631).

## 7. Why the split has fewer people and fewer coastal towns (lane 272, PW-1631 / PW-1630)

Code 2a2876cd (PW-1640's harbour fix in). Earth-like A, dnd tree, one try. L7 run 732ed6 on 899985 against split run f465d8
on 9cf1c3 (a fresh L8 refine of 899985), same code; towns read on 9cf1c3 (`measure.py`, lane scratch), people per stored
frame and by km to the sea read on 9cf1c3 too (`profile.py`). Scripts named below are in the lane's scratch (deleted after).

| | L7 732ed6 | split f465d8 |
|---|---|---|
| villages / towns / cities | 22,493 / 6,209 / 286 | 57,634 / 5,245 / 245 |
| towns and cities on the fine coast (7.5% of the fine land) | 7.6% | 4.4% |
| ...within ~60 km of the fine sea (13.2%) | 15.2% | 9.1% |
| ...on a navigable river; in the water | 34.4%; 1.06% | 34.5%; 0.0% |
| islands (< 0.3 Mkm2) with a town | 22 | 11 |
| people today (run.json, every line) | 1,042 M | 912 M (-12%) |
| humans: people; held Mkm2; per km2 | 660 M; 85.0; 7.77 | 433 M; 81.4; 5.32 |

**PW-1631, people.** Humans hold about the same land (-4%) at two-thirds the density; the other peoples' totals move both
ways (dragonborn 2 M -> 81 M: they reached the plough on the split, fishers on L7; orcs -18 M). By way of life, over every
line: irrigation 162 M -> 80 M, agro-pastoral 171 -> 147, plough 624 -> 627. The per-frame totals cross more than once
(4 kyr ago 358 M vs 299 M; 1.5 kyr ago 673 vs 674; today 1,011 vs 890 summed on the fine cells), so part of any one
gap is the draw, but three draws now point the same way (-8% §4, -13% §6, -12% here) and a static estimate finds the
same size from the land alone. `ladder_static.py`: a farming, herding people at the medieval plough and Butzer's 150 BC
irrigation over all land reads 16.81 /km2 on 899985 and 14.38 on 9cf1c3 (-14.5%). Two causes:
- **The irrigated valley was a share of a cell** (ladder WATER_MAX 0.3 of a cell on the greatest rivers). An L8 river
  cell is half as wide, so the watered strip was half as wide: 3.32 Mkm2 watered on L7, 1.81 on L8, for the same rivers
  (cells with 500 m3/s or more: ~570,000 km of river on L7, ~604,000 on L8; the same peak discharge). Doubling the L8
  share (the same 18 km valley) takes the static estimate to 15.33 (-8.8%). Fixed (below).
- **Poorer farmland on the refine, from its soils** (lead 1, but not the slope). The fertile class falls 0.971 -> 0.868
  (-11%) over the land. The slope term removes nothing on either grid (`slope_diag.py`: under 0.1% of the score; slopes
  over 8 degrees on 0.02% and 1.2% of the land). `fert_diag.py` takes the score apart: with peat ignored the classes are
  1.376 (L7) and 1.431 (L8); with the soil depth floored at 1 m, 1.06 and 1.075. So the refine's soils carry it: peat
  over 0.5 m on 31.5% -> 40.1% of the land, soil depth mean 1.31 -> 0.99 m (25th percentile 0.56 -> 0.10 m).
  soils.erosion_rate goes as the square of cell_slope (relief over the node spacing), steeper on the finer grid. That is
  the refine's (surface), not the peoples' model: left as an inbox draft. It is the rest of the static gap (farm share
  0.480 -> 0.434).

Lead 2 (the spread's pressure decays per cell: `enter`, the sea factor and the crop front's `gap` are per cell while the
passes are per km) is a real grid dependence but not what costs people here: the humans' held land is within 4%, and the
split peoples more small islands, not fewer (`islands.py`: 297 of the fine world's 331 against 142 read through L7's
cells; sedentary people on them 4.8 M against 4.1 M). Not changed; inbox draft.

**PW-1630, coast.** Lead 3 holds, through time. By km to each run's own sea (`townband.py`), within ~60 km: L7 136 M
sedentary (6.09 /km2), 986 towns and cities (15.2%), 72 per 10 M sedentary; split 106 M (4.39 /km2, -28% against
-14% over all land), 500 (9.1%), 47 per 10 M. The town rule is not what shuns the coast: applied to the final frame
(`bestsite.py`, read-only) it puts 11.8% (L7) and 11.0% (split) of the best town sites within ~60 km, and the site
factor and the fishers barely move that. The gap is founded in the past (`townlife.py`): places ever a town or city in
the band 1,384 (L7) against 724, with the same fates (most still towns). The same rule on the past frames
(`bestsite2.py`): the band's share of the sedentary people 11.5% vs 7.7% 6 kyr ago, 13.9% vs 10.0% at 4 kyr, 14.8% vs 11.8%
at 2 kyr, 15.9% vs 13.8% today; its share of the best sites 3.6% vs 0.6%, 6.9% vs 2.6%, 9.4% vs 6.6%, 11.8% vs 11.0%.
Coastal towns follow the coastal farmers, and on L8 they came late. Three causes, the first two in the ladder:
- **The rich-wild resistance read the shore cell alone** (PW-1385 A: farmers take up rich wild land slowly). The fish good
  is 0.69 on L8's shore cells against 0.51 on L7's (the L7 cell averages the strip with the land behind it), so the L8
  shore read richer and farmed less. `rich_static.py`, the farmed share of the farmable land within 60 km of the sea after
  2 / 4 / 8 kyr of crops: L7 0.66 / 0.78 / 0.88, L8 0.55 / 0.71 / 0.86, L8 with the richness averaged over one ring 0.64 /
  0.79 / 0.91. Its cases are densities over whole domains (Calusa ~0.8 /km2 over a domain), so it is read over ~60 km now.
- the irrigated valleys above (river mouths and deltas are on the coast);
- the refine's soils (the fertile good within 60 km of the sea 0.539 on L7, 0.439 on L8).

Islands with a town (22 vs 11) are not short of people on the split (above); likely their size in cells (an L7 island
cell counts 3,600 km2 of land, often more than the island), not checked further.

**Fix** (3d21c18b): ladder.WATER_CELL_KM (the watered share is WATER_MAX of one L7 cell's width: x1 at L7, x2 on L8) and
ladder.RICH_KM / domain_mean (the richness averaged over rings_for(g, 60 km) - 1 rings: none at L7, one on L8). L7 is
unchanged by construction (the same arrays: tests/test_people_units.py). Not tuned toward L7: no threshold moved; the
soils are left to their owner.

### 7.1 After the fix (lane 272c)

Code 3d21c18b (ladder.WATER_CELL_KM and RICH_KM) on d17142c6's tree. Same world pair, same tree and seed, one try; the L7
rerun 3413e1 against 732ed6 and the new split 393622 against f465d8. Baselines: L7 732ed6 and split f465d8 (both code 2a2876cd,
table above); lane 270's 727c35 (code 5bd8e407) is the third old draw (909 M, humans 430 M).

**L7 is unchanged.** 3413e1 matches 732ed6 in every file of people, demes, cultures, settlements and layers, byte for
byte; gods, taboos and languages differ only in timings and the run id (checked by field).

| | L7 732ed6 (= 3413e1) | split f465d8 (old) | split 393622 (new) |
|---|---|---|---|
| villages / towns / cities | 22,493 / 6,209 / 286 | 57,634 / 5,245 / 245 | 58,820 / 5,721 / 271 |
| towns and cities on the fine coast (7.5% of fine land) | 7.6% | 4.4% | 5.2% |
| ...within ~60 km of the fine sea (13.2%) | 15.2% | 9.1% | 10.2% |
| ...beside a harbour (2.9%) | 3.39% | 1.97% | 2.49% |
| ...on a navigable river | 34.4% | 34.5% | 39.5% |
| islands (< 0.3 Mkm2) with a town | 22 | 11 | 13 |
| people today (run.json, every line) | 1,042 M | 912 M (-12.4%) | 984 M (-5.6%) |
| humans: people; held Mkm2; per km2 | 660 M; 85.0; 7.77 | 433 M; 81.4; 5.32 | 461 M; 81.9; 5.63 |
| people summed on the fine cells: 4 kyr / 2 kyr / 1.5 kyr / today | 358 / 626 / 673 / 1,011 M | 299 / 561 / 674 / 890 M | 308 / 599 / 720 / 958 M |
| sedentary within ~60 km of the sea (townband) | 136 M (6.09 /km2) | 106 M (4.39) | 119 M (4.85) |
| places ever a town or city: coast band / inland | 1,384 / 7,984 | 724 / 8,701 | 869 / 9,233 |
| band's share of the best town sites, 4 kyr / 2 kyr / today | 6.9 / 9.4 / 11.8% | 2.6 / 6.6 / 11.0% | 4.8 / 8.7 / 13.2% |

**PW-1631 (people): about half closed.** The gap to L7 goes from -12.4% to -5.6% in the run totals (-12% to -5% on the
fine cells today), the humans' from -34% to -30%. Not the whole: the rest is the refine's soils (draft
`draft-l8-refine-soils-thinner-peatier`), which the static estimate put at about half of the gap. One draw: the
earlier three (§4, §6, §7) were all within -8% to -13%, so -5.6% is outside their spread, but it is still one draw.

**PW-1630 (coast): partly closed.** Coast share 4.4% -> 5.2% (L7 7.6%), within ~60 km 9.1% -> 10.2% (15.2%), islands
with a town 11 -> 13 (22), harbour towns 1.97 -> 2.49% (3.39%). The band's sedentary density rose 4.39 -> 4.85 /km2 (L7 6.09)
and its share of the best sites now matches or beats L7's at the end (13.2% against 11.8%). What remains is a coast-only
shortfall in towns: places ever a town or city in the band 869 against 1,384 while inland has 9,233 against 7,984; towns per
10 M sedentary in the 0-30 km band 43 (L7: 72 for the 60 km band). Candidates (not done here): the refine's poorer
soils near the sea (fertile 0.439 against 0.539), the town rule's per-cell reads on a half-width coast cell. Inbox draft
`draft-l8-coast-towns-remaining-gap`.
