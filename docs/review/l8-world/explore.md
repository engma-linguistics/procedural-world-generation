# Exploring the L8 world (lane 96)

World `a16f5a` (L8, 655,362 cells of ~30 km, 100 Myr, seed 11, run `2c0c5d`) against the L7 seed-11 world `2a7385`
(792 Myr, older code: different continents, so only counts compare) and against **Earth**: ETOPO1 (the repo's
`data/earth/raw_etopo_bed.npz` / `raw_etopo_ice.npz`, 10 arc-minute) resampled onto the same L8 and L7 grids with the
land rule of `tools/earth_data._build`. Every Earth number below is measured from that data this session; none is
quoted from memory. Read-only throughout: no code changes, no sims, nothing rebuilt.

Open in your viewer: http://localhost:8765/viewer/?world=a16f5a.json

## In plain words

**Your spot is a flooded piece of continent, not a sunken plateau.** The light-blue sea east of Ratote sits on the same
continental plate as Ratote itself (plate 22: 17 Mkm² of continental crust, 69% of it dry land). It is old shield rock with
mud on top, 33 km thick, just like the land beside it, so it is a shallow sea *on* a continent, like Hudson Bay or the
inland seas that covered North America in the age of the dinosaurs. It flooded because this world's sea level has risen
312 m in 100 Myr: after the supercontinent broke up, the new oceans are young and hot and shallow, and the water had to
go somewhere. That part is plausible and looks great.

**The edge is too sharp, and that is a real gap, not just the big cells.** On Earth the sea floor falls from the shelf
edge to the deep ocean over a few hundred km: a slope and then a long apron of mud at its foot. Here it drops ~3.8 km
between two neighbouring 30 km cells: the last continental cell is 26 km of crust at -441 m, the next is 9 km of ocean
crust at -4,199 m. One coast cell in five has 3 km-deep water in the very next cell; on Earth, sampled on the same grid,
one in a hundred. The sea's middle depths (200-3,000 m) are 5% of this ocean and 18% of Earth's. The cause: when a
continent rifts, the model barely stretches the edge (the crust at the edge has hardly thinned) and then switches from
"continent" to "ocean floor" in one cell. That is ticket PW-950, and its first suggestion (thin the crust gradually over
50-200 km) is the fix. L7 has the same missing middle depths, so this helps the showcase too. L8 just shows it plainly.

**The world's "largest river mouth" is a puddle 800 km inland.** Anything below 0 m counts as sea, even a few cells
dipping 1-2 m below sea level in the middle of a continent with no way out. At L8 there are 225 such pockets, and 21 of
the 66 big rivers end in one, including the biggest (the highlight and the regional zoom 652c1a were built on it). A
cheap fix (only sea joined to the ocean counts as sea; the rest becomes lakes or dry hollows) helps L7 too: L7 has 41
such "seas", deep pits the model also draws as ocean.

**The sea rose and the land rose with it.** Through that +312 m rise the land share stayed ~34%, because the low ground
rose ~250 m too. The result is a lot of very flat land just above the water: 6% of the land is within 10 m of sea level
(Earth 1.4%). Probably partly crust and mud, but worth a cheap look, and it is a model thing that would show at L7 too.

**The giant inland sea in the north is gorgeous and probably passing.** A 1.15 Mkm² salt lake ringed by volcanoes. It grew
from 200 to 1,439 cells in the last 4.5 Myr: one of the run's giant flat hollows filling up (PW-300/PW-359), and it is
77% of all the lake area. Without it, L8's lakes are modest, not "40 times L7".

**What L8 genuinely adds:** a river web that branches like real drainage, many more closed basins (9.5% of the land drains
inland vs 2.3% in the L7 world), small islands in Earth-like numbers, ragged coasts with tidal flats and mangroves, and a
newly opening rift sea through the big continent that looks like the Red Sea. What it does not fix: islands of Sicily-to-
Iceland size are still rare (11 vs Earth's 44 on the same grid), and mountains are low, but that is the world's youth.

## Your spot, answered

Cell 316323 (-27.30, -88.17): -1 m, shale and mudstone over ancient shield, 1.6 km of sediment, 33 km crust, plate 22.
[viewer](http://localhost:8765/viewer/?world=a16f5a.json&lat=-27.30&lon=-88.17)

**What it is.** The continental-crust region containing it (connected cells with continental crust) is one block:
21,781 cells, **16.95 Mkm²**, lat -51..-9, lon -134..-40, all plate 22; 69% land (Ratote and Razukum), 31% sea. Elevation
p10/50/90 = -138 / +78 / +673 m, median crust 35.1 km, basement 71% craton, 28% orogen. The sea part is mostly 0 to -150 m.
So it is **not** a Kerguelen/Zealandia-style drowned block (those are continental fragments sitting a kilometre or more
down, separated from their mother continent); it is an **epicontinental (platform) sea on a whole continent**, the
Hudson Bay / Western Interior Seaway type. Shield rock under mud is exactly what such a sea floor is made of.

**Why it is flooded.** Sea level in run 2c0c5d climbs from ~0 (24 Myr) to **+311.6 m** (100 Myr); the ocean-basin part is
+323.9 m, close to the ±400 m limiter (`earth.SEA_TECT_MAX`). Ocean floor in a16f5a has a mean age of 26.7 Myr (L7 2a7385:
55.7). Young floor is shallow, so the sea spills onto the continents: the shelf share of the ocean went 2.1% (t=0) →
4.5% (t=100) and the submerged continent's median from -504 m to -145 m. The code comment cites about -100..+250 m for
Earth's Phanerozoic, so +312 m is on the high side (evidence added to PW-051), but a flooded platform at a highstand is the
right picture.

**Is the sharp edge plausible?** No, and it is mostly not the cell size. Across the continent-ocean crust boundary
(medians over the whole world):

| cell (signed hops from the boundary) | -3 | -2 | -1 (last continental) | +1 (first oceanic) | +2 | +3 |
|---|---|---|---|---|---|---|
| crust (km), L8 a16f5a | 33.3 | 31.5 | 25.9 | 9.0 | 8.4 | 8.2 |
| elevation (m), L8 | +30 | +3 | -441 | -4,199 | -4,326 | -4,400 |
| crust (km), L7 2a7385 | 29.0 | 23.0 | 19.0 | 10.0 | 9.0 | 8.0 |
| elevation (m), L7 | +22 | -826 | -1,701 | -3,769 | -4,052 | -4,134 |

For the spot's block: edge cells (inside) median -221 m and 29.3 km of crust; the ring of cells just outside is all
oceanic, median -4,238 m and 9.9 km. A 4 km drop over one 30 km step is ~130 m/km (~7.6°).

Hypsometry and margin shape against Earth on the same grids (`hyps.py` in the lane's scratch; numbers in PW-950's update):

| | a16f5a (L8) | Earth on L8 | 2a7385 (L7) | Earth on L7 |
|---|---|---|---|---|
| land % | 34.0 | 29.1 | 36.1 | 28.9 |
| shelf (0 to -200 m), % of ocean | 4.3 | 7.0 | 0.7 | 6.6 |
| 200-3000 m (slope and rise), % of ocean | **5.0** | **17.7** | 10.6 | 18.1 |
| 4000-5000 m, % of ocean | 48.1 | 32.0 | 29.2 | 32.0 |
| median depth 60 km offshore (m) | -2,380 | -325 | (60 km: -1,111) | (60 km: -127) |
| coast cells with >3000 m water in the next cell | **20.9%** | **1.1%** | 9.3% | 1.6% |
| ... within two cells | 41.3% | 5.0% | 32.1% | 10.0% |
| median distance coast → 3000 m depth | 90 km | 360 km | 180 km | 420 km |
| steepest-neighbour gradient on slope cells, p50 (m/km) | 60 | 29 | 29 | 20 |
| submerged continent: median depth | -154 m | | -1,516 m | |

(Earth's whole 10' raster: land 28.8%, shelf 7.45% of the ocean, so resampling barely moves the shelf share.)

Reading: the shelf share at L8 is close-ish to Earth's only because of the highstand. The margin is a cliff: the
200-3,000 m band is a third of Earth's, and the coast-to-abyss distance a quarter. The L7 world has a wider taper (older
code, eight times older margins with 3.4 km of sediment) but the same hollow middle (10.6% vs 18.1%).

**What is missing, in order of size (the tickets):**
1. **No necking zone.** `crust.rift_stretching` thins only crust thicker than 23 km at the opening boundary, and
   `stretch` stops at 22 km, then the edge switches from the continental to the oceanic isostasy formula
   (`isostasy.elevation`: `250 + 150·(t-35)` vs `ocean_depth(age) + 200·(t-7)`). The edge's recorded rift strain is ~0.04
   (β ≈ 1.04): the margins here are hardly stretched at all. Real rifted margins thin over a necking zone (PW-950 and docs/review/tectonics/crust/crust.md give 50-200 km; not re-read from a paper this session).
   → **PW-950** suggestion 1 (tapered stretching). It would turn the one-cell cliff into a 3-6 cell slope at L8 and
   2-3 cells at L7.
2. **No continental rise.** Sediment that passes the shelf is spread over ~1000 km of deep floor (overview §2.5); the
   first oceanic cell holds 0.59 km of sediment. There is no apron piled at the slope's foot. → part of PW-950 (its
   suggestion 2, measure what reaches the brink); I would add "pile the overflow at the foot of the slope first".
3. **Thermal subsidence and flexure** exist (McKenzie sag, flexural moats; PW-054/PW-284), but they act on the stretched
   crust, and there is barely any, so they don't shape this margin.
4. **Flank uplift** (PW-135) is the landward side of the same rift story; not visible here.

Resolution's part: L8 makes the cliff visible (the transition should be 3-6 cells wide and is one), but the same
physics gap is why L7's slope band is thin. **Fixing PW-950 helps L7 directly.**

## Findings

| # | finding | where | verdict | resolution or model | ticket / draft | helps L7? |
|---|---|---|---|---|---|---|
| 1 | Daniel's spot: a flooded platform on a whole continent (plate 22, 17 Mkm², 31% under a shallow sea), shield under mud | [-27.3, -88.2](http://localhost:8765/viewer/?world=a16f5a.json&lat=-27.30&lon=-88.17) | good | model (highstand) | PW-051 update | n/a |
| 2 | Continental edge is a one-cell, ~4 km cliff; slope and rise depths are a third of Earth's | everywhere; e.g. [-26, -86](http://localhost:8765/viewer/?world=a16f5a.json&lat=-26&lon=-86) | bad | model (no necking zone, no rise); L8 shows it | PW-950 update | **yes** |
| 3 | Sea level +312 m (young oceans after breakup), near the ±400 m limiter | whole world | off (high but explicable) | model | PW-051 update | yes |
| 4 | Land rose with the sea: land stays ~34%, 6.3% of land within 10 m of sea level (Earth on L8 1.4%), 49% below 200 m (27%) | interiors, e.g. [-3, 84](http://localhost:8765/viewer/?world=a16f5a.json&lat=-3&lon=84) | off | model | draft-continents-rise-with-the-sea-in-a-highstand | yes |
| 5 | Below-sea pockets inside land count as sea; 21 of 66 big rivers end in them, incl. the #1 "largest river mouth" ~800 km inland | [-3.1, 83.6](http://localhost:8765/viewer/?world=a16f5a.json&lat=-3.1&lon=83.6) | bad | model bug, exposed by resolution (L7: 41 deep pits drawn as sea) | draft-below-sea-pockets-inside-land-count-as-sea | **yes** |
| 6 | Giant closed salt lake, 1.15 Mkm², 174 m deep, ringed by arc volcanoes; grew 200 → 1,439 cells in 4.5 Myr; 77% of all lake cells | [44.9, 163.4](http://localhost:8765/viewer/?world=a16f5a.json&lat=44.9&lon=163.4) | cool, but transient | model (PW-300 pattern) | PW-359 update | yes |
| 7 | Lakes otherwise modest: 92 lakes, 432 cells (0.34 Mkm²) vs L7's 18 on 44 cells; 53 of 93 L8 lakes are single cells | many | fine | resolution | - | no |
| 8 | Inland drainage: 9.5% of land (5.1% to lakes, 4.4% to dry dead ends) vs 2.3% in 2a7385; overview §2.5 gives Earth ~18% | interiors | good | resolution (finer basins) | (PW-243 context) | partly: L7 can't resolve them |
| 9 | Rivers: tree-like networks, 2.7% of big-river steps go uphill >1 m (L7 4.2%, median 7 m vs 12 m) | e.g. [0, 80](http://localhost:8765/viewer/?world=a16f5a.json&lat=0&lon=80) | good | resolution | - | no |
| 10 | Small islands: 255 under 10,000 km² (Earth on L8 392); mid-sized (10k-100k km²) only 11 vs 44 | oceans | off | model (no microcontinents/mature arcs) | draft-few-mid-sized-islands | yes |
| 11 | Coasts: mangrove 2,455 and tidal-flat 2,147 coast cells (L7 347 / 140): warm, low, flooded shores | e.g. [-2.4, -55.8](http://localhost:8765/viewer/?world=a16f5a.json&lat=-2.4&lon=-55.8) | good | mostly model (highstand + warm lowlands), helped by finer coast | - | n/a |
| 12 | A young narrow rift sea splitting the big continent Hizam, Red Sea-like, with big rivers draining away from it | [0, 75](http://localhost:8765/viewer/?world=a16f5a.json&lat=0&lon=75) | cool | model | - | n/a |
| 13 | Mountains low: land >2 km 1.2% (Earth on L8 10.3%, L7 world 4.6%), peak 3,248 m | Hizam | off | age (100 Myr), not resolution | PW-846 (existing) | n/a |
| 14 | Peoples (b9edf5, current code): crisp borders, hobgoblins lead with 16% of land across west Hizam; 5,814 patches vs 1,582 on L7 57b95b (older code, so not separable) | [run b9edf5](http://localhost:8765/viewer/?run=b9edf5&layer=peoples) | fine | can't separate | - | n/a |
| 15 | 3D relief draws a regular lattice of diamond dimples over shallow seas (data has no such lattice: one-cell dips median 4 m) | [-26, -86 with 3D relief](http://localhost:8765/viewer/?world=a16f5a.json&layer=elevation&view=-26,-86&dist=1.45&relief3d=1&ex=10) | off | viewer | draft-3d-relief-diamond-lattice-on-shallow-seas | maybe |

Notes on method: cells are equal-area, so plain means are fair. "Coast" = land cell with a sea neighbour. Lakes =
connected `lake` cells. Detached seas = connected `elevation <= 0`, non-lake cells not joined to the largest sea body.
The L8 run's climate ran at L6 (`climate_level: 6`); the slice's climate is full L8. a16f5a and 2a7385 differ in age and
code, so only differences that are clearly resolution (counts of small things, network shape) are called resolution.

## Screenshots (`docs/review/l8-world/explore/`)

- `01_spot_flooded_platform_sat.jpg`: Ratote and the flooded half of its continent, true colour. Your spot is in the light-blue sea.
- `02_spot_step_relief.jpg`: the same coast in 3D relief (×10): shallow sea, then the cliff to the abyss in one cell. Also shows the diamond lattice (finding 15).
- `03_spot_crust_thickness.jpg`: crust thickness: the whole block is continental to its very edge, then ocean crust.
- `04_giant_salt_lake_sat.jpg`: the 1.15 Mkm² salt lake ringed by arcs (markers on).
- `05_largest_river_ends_inland.jpg`: Hizam with the rift sea on the left; the biggest river (in the 652c1a box) ends in blue "sea" hexes far inland.
- `06_globe_L8_sat.jpg` / `07_globe_L7_sat.jpg`: the two globes from the same angle (different continents: age and code, not resolution).
- `08_peoples_L8.jpg`: peoples on L8 (run b9edf5).

Scripts (scratch, deleted at the end): layer extraction streamed per line from the world JSON, Earth resampling
(copy of `tools/earth_data._build`'s elevation part, nothing written to `data/`), BFS over the grid's neighbour lists for
offshore profiles, components for lakes, islands and detached seas, playwright screenshots against a private
`planet serve --port 8796` (stopped).
