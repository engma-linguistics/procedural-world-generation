# Open niches: why rich land holds no dragons (PW-1024, fun lane 50)

Step 0 of PW-1024, the diagnosis gate: what the probes found, and the plan for the owner's ruling (a mix of A and B), written before any sweep (sections 1-3). Section 4 adds the paired sweep's results; its plain summary is first.

The scripts are in this folder:
- `diag.py`, `diag_read.py`, `gap.py`, `occ2.py`: the diagnosis;
- `sweep.sh`, `compare.py`, `kind_country.py`, `maps.py`: the sweep, with its outputs `compare.txt` and `kind_country.txt`.

Run them with `PYTHONPATH=. uv run python ...` from the repository root.

## In plain words

- **The "46% at 25 kyr, 16% now" fall is mostly a change of which cells are counted, not dragons retreating.** "Rich land no people holds" is a different, smaller set of cells now than 25 kyr ago: the peoples moved into most of the old set. On the *same* cells, dragon occupancy falls more gently (30% to 16%, or 46% to 32%), and the cause there is climate. These cells warm and dry through the Holocene, so the one kind that lived there, brass dragons, loses habitat. The dragons' range dynamics are fine. Wherever some kind's habitat allows it, 80-90% of the cells hold a dragon, at every era.
- **On world 2a7385 the "rich empty" land is partly an artefact.** In half of it the time zoom's present climate gives about 70 mm of rain a year. The world itself gives about 570 mm there, and the prey comes from the world's rain. So the land is "rich" in prey but a desert to every habitat. A draft ticket covers the mismatch.
- **The real gap is warm, open grassland, not mainly cool plains.** On three worlds, 15-30% of rich land is land that no dragon kind's habitat reaches. Almost all of it is open grassland or parkland. It sits in warm-temperate climates (Köppen Cwa and Cfa, a median of 20-22 °C, 800-1,650 mm of rain). Cool continental plains (5-15 °C, 400-900 mm) are only 1-7% of the gap: such land is rare on these worlds. The owner's widening of gold dragons (cool open steppe) closes most of the gap, because gold then holds open grassland at any temperature from 5 to 32 °C. On world 1df1c3 the gold dragons died out long ago, so there only ecological release can fill the gap.
- **Plan.** A: widen blue, gold and copper (the strong fits) and give the edge fits a "tolerates" tier. B: ecological release, raising a kind's habitat in rich land next to its range when no rival kind holds it. Both are small and each knob is named.

## 1. The 25 kyr to present contraction

Inputs:
- lane 45b's saved run (`data/review-inputs/l45b/save2/run/ERAS.npz`, 2a7385 roll 7000);
- three new diagnosis runs on the main tree at 2cdf9641 (2a7385/7000, 1df1c3/7000, e71172/7001). `diag.py` saves each megafauna kind's presence P and habitat K at 60, 30, 25, 20, 15, 10, 7, 5, 3, 2, 1 and 0 kyr, with the climate and the peoples' density.

"Rich empty" is the peer review's class: land with prey of at least 3 t/km² and fewer than 0.02 people per km².

**(a) The class changes members.** From the l45b save (`occ2.py`):

| Fixed set of cells | Occupied at 25 kyr | at 10 kyr | now |
|---|---|---|---|
| rich empty at 25 kyr (345 cells) | 46% | 42% | 32% |
| rich empty now (190 cells) | 30% | 22% | 16% |

- Only 136 cells are in both sets.
- 61% of the 25 kyr set is peopled now.
- The cells left empty now were the less dragon-held ones even 25 kyr ago (30% against 46%).

So about half of the 3x fall is selection. The like-for-like fall is about 1.5-1.9x.

**(b) On fixed cells the habitat shrinks; occupancy given the habitat does not.** From the diagnosis runs, on the present's rich empty cells of 2a7385/7000 (797 cells under the current tree):

| kyr ago | occupied | some kind's K >= EST | occupied where K allows | best K | T °C | env rain (median) |
|---|---|---|---|---|---|---|
| 25 | 0.38 | 0.44 | 0.86 | 0.39 | 16.4 | 88 mm |
| 10 | 0.36 | 0.42 | 0.87 | 0.37 | 15.7 | 86 mm |
| 3 | 0.34 | 0.40 | 0.85 | 0.36 | 18.3 | 81 mm |
| 0 | 0.27 | 0.34 | 0.81 | 0.30 | 19.1 | 70 mm |

- The only kind of any extent there is brass. Its held share falls from 0.32 to 0.24 as its K falls (mean 0.29 to 0.23).
- The other two worlds show the same thing: occupied-where-K-allows is 0.67-1.00 at every era.

The contraction is the climate moving the brass dragons' range, with the rest of the decline being set membership. It is not range dynamics (no pressure: 0.00-0.03 there) and not a lag in dispersal.

**(c) The rain mismatch.** On 2a7385, the rich empty cells have world rain of 319 / 571 / 1,037 mm (10th / 50th / 90th percentile). The time zoom's present climate gives 35 / 70 / 109 mm there.
- 843 land cells (1.4%) have world rain above 600 mm and env rain under 200 mm.
- Of the rich land no dragon can live in on 2a7385, 47% has world rain more than 3x the env rain.
- On 1df1c3 and e71172 that share is 5-6%, about the land-wide share.

The prey (`ps.graze_npp`, from the world) and the habitats (env rain, from the time zoom's climate) read different climates. That is a defect of its own, not part of PW-1024 (draft `draft-time-zoom-rain-vs-world-rain`).

## 2. Where the open niche is

From `gap.py`, at the present: rich land (prey >= 3 t/km²), whoever lives there, where no dragon kind's K reaches EST.

| World | Rich land, cells | Dragon-held | No kind can live there | Peopled share of that gap | Gap climate (median) | Köppen of the gap | Open (treeless) | Cool plains share of gap |
|---|---|---|---|---|---|---|---|---|
| 2a7385/7000 | 9,517 | 56% | 15% | 64% | 20.3 °C, world 800 mm | Cwa 87%, Cfa 7% | 52% | 1% |
| 1df1c3/7000 | 13,520 | 35% | 30% | 98% | 21.9 °C, 1,271 mm | Cwa 65%, Aw 22%, Cfa 11% | 96% | 7% |
| e71172/7001 | 7,458 | 38% | 19% | 95% | 21.2 °C, 1,649 mm | Cwa 70%, Cfa 27% | 94% | 2% |

- The gap is warm-temperate, dry-winter and humid-subtropical open grassland and parkland.
  - Gold dragons cover only Köppen Aw (`prefers = ["savanna"]`).
  - Green dragons need forest.
  - Brass dragons need 18 °C and under 700 mm.
- On 1df1c3 the gold dragons are absent altogether at 25 kyr and now, and their habitat is not computed. Their Aw is in the gap.
- Most of this land is peopled. There the peoples press the dragons down anyway, but presence (and so the map, and the count at the pressed density) still needs a kind that can live there.

## 3. Plan

### A: widen kinds by hand (owner's guidance, a design note, not a source)

Strong fits get widened ranges or more preferred country:
- **blue:** temp [14, 40] to [4, 40]; rain [60, 600] to [60, 800]; prefers desert plus **BSk** (cold steppe: dry shortgrass and storm country). Tolerates open grassland.
- **gold:** temp [16, 32] to [5, 32]; rain [500, 1500] to [400, 1500]; prefers savanna plus **open** (open grassland at any temperature in range: the cool steppe and, on these worlds, the warm Cwa/Cfa grassland that is the main gap).
- **copper:** temp [10, 30] to [5, 30]; prefers hills plus a new place tag, **breaks**. That is open, dry-ish (under 1,100 mm) country with relief of at least 2 m per km to a neighbour (about 120 m over a 60 km cell), under the mountains. Badlands are far finer than a cell, so breaks is a proxy: about a third of the open land under 1,100 mm on 2a7385.

Edge fits get a new spec field, `tolerates = [places or climates]`, for megafauna. In those places, and in the kind's own country just past its comfort range, the habitat is TOLERATE_K = 0.5 times the climate fit on a range widened by EDGE_C = 5 °C, EDGE_OCT = 0.5 octaves of rain and EDGE_ELEV_M = 1,000 m of height. The better of this and the plain habitat is taken, so nothing is lowered.
- green: tolerates open (forest-steppe, parkland);
- silver: tolerates steppe and open (the elevation margin lets them range down onto high steppe);
- bronze: tolerates wetland (there is no river or lake tag yet; draft);
- brass: tolerates open (hot dry margins);
- white: tolerates steppe and open (the harsh northern steppe).

Red and black are unchanged (poor fits).

At 0.5 the tolerated country counts as reachable for scatter and for the coverage target, as the own country does.

### B: ecological release, three candidate forms

1. **Habitat release (picked).** In a cell outside the kind's habitat tiers, the habitat is lifted to at most RELEASE_K = 0.3 x the edge climate fit x a prey factor x open.
   - The prey factor is 0 at or below the land's median wild prey and 1 at RELEASE_PREY = 2x it, linear between, read from the step's prey field.
   - "Open" means no other kind of the same sort (dragons for a dragon, giants for a giant) holds the cell.
   - Released land is under scatter's SUITABLE (0.5), so no new pockets are founded in it. The kind can only walk or fly in from land it holds next door.
   - It applies only within RELEASE_KM = 300 km of the kind's own country (its habitat without release reaching the coverage target's "suitable"), which is the "neighbouring" in the ruling. This bound was added after a smoke run without it: there, fire giants spread from the volcanoes over warm grassland at 3x their count.
   - It holds them at about a third of the density.
   - It is not used in the deep epoch (no prey field for those plates).
   - The coverage target is computed without it.
   - Evidence that this form is the lever: where K allows, 80-90% of cells are occupied, so raising K where it is low is what fills land; dispersal does the rest.
   - It is general: any preset with megafauna gets it, with no data in the preset.
2. **Count release.** Leave ranges alone and move part of a neighbouring pocket's expected count onto empty food within the foraging reach (FORAGE_KM). Rejected: it is invisible on the maps, has no interaction with rivals, and is an accounting trick, not a mechanism.
3. **A higher MEGAFAUNA_OFF everywhere** (0.1 to about 0.3). Rejected: it is unconditional (poor land and rival-held land too) and blurs PW-924's "each kind sticks to its country".

### Check (after the coordinator has seen this)

A paired sweep, main (2cdf9641) against lane 50: 6 worlds x rolls 7000-7001, lane 45b's probe (`docs/review/megafauna/probe.py --eras 25,10,0 --save`), at most 6 at a time. Reported:
- rich empty occupancy;
- dragons per run;
- dragons by country;
- giants by kind;
- per-people pass rate (>= 300 cells);
- remnants;
- maps of each dragon kind before and after.

## 4. Results: the paired sweep

Both arms are on the same base, main 29c38f8b (after the speed merge, before the fix lane 45d51c3f): main as is, and lane 50 on top. 6 worlds (2a7385, 1df1c3, e71172, 6909cb, a12762, 067778) x rolls 7000-7001, 12 paired runs, `probe.py --eras 25,10,0 --save`. Full tables: `compare.txt`, `kind_country.txt`. Maps: `kinds-2a7385-7000.png` and `kinds-e71172-7000.png` (main on the left, lane 50 on the right, one row per kind; pale green is rich land).

### In plain words

**Rich land nobody holds now has dragons almost everywhere: 90% of it, up from 52%.** Dragons are up 7% per run and giants 24%. The peoples are untouched: 67.8% of peoples pass, against 67.0%, and there are fewer remnants. Most of the extra dragons are the new gold dragons on open grassland, and white dragons out on cold steppe and hills. Each kind still lives mainly in its own country.

Where each kind lives now (per run, main to lane):
- **Gold dragons** were the missing kind: absent in 4 of 12 runs and ~60 per run before. They are now in every run, ~800 per run, all on open grassland (warm-temperate and cool steppe, the land that was the gap). They reach 70% of their country, against 36%.
- **Blue dragons** still mostly hold the deserts (37,550 per run there, unchanged). About 2,200 more are out on the cold, dry shortgrass steppe (Köppen BSk), with a few on the bluffs and hills by it.
- **Brass dragons** stay on the hot steppe, somewhat fewer (8,700 against 11,500 per run). Gold and blue now share the open grassland round it, and the rivals close released land to each other.
- **Copper dragons** have their new badlands and breaks country (~100 per run) beside their hills; 181 per run against 62.
- **White dragons** grow most: 4,200 against 1,400 per run. They are still mostly in cold mountains and tundra, now also on the cold hills, open country and northern steppe next to them (the "harsh northern steppe").
- **Green dragons** add forest and forest-edge country: 347 per run in forest, against 142.
- **Silver dragons** are a few more in the mountains and onto the hills below them.
- **Red dragons** shift from mountains towards volcano country (486 against 279) and **black dragons** stay in the swamps; both were left as they were (poor fits).
- **Bronze dragons** still keep the coasts (no river or lake tag yet; draft).
- **Giants:**
  - Hill giants go from 1,621 to 1,935 per run, all in hills.
  - Fire giants go from 1,339 to 2,165, mostly more volcano country plus some steppe next to it.
  - Frost giants go from 1,326 to 1,508 (more tundra).
  - Cloud giants go from 158 to 195.
  - Storm giants are unchanged.

### Numbers

| | main | lane 50 |
|---|---|---|
| rich empty land holding any dragon (present) | 0.52 (398 cells per run) | **0.90** (362) |
| the same at 25 kyr | 0.58 | 0.90 |
| all rich land holding any dragon (present) | 0.32 | 0.35 |
| dragons per run | 54,226 | 57,991 (+7%) |
| giants per run | 5,625 | 6,997 (+24%) |
| per-people pass (>= 300 cells) | 185/276 = 67.0% | 187/276 = 67.8% |
| remnants (< 100 cells; absent) | 44 (12) | 40 (12) |

- Rich empty occupancy rises in all 12 paired runs. Examples:
  - e71172: 0.06 to 0.94 and 0.06 to 0.68;
  - 2a7385: 0.27 to 0.79 and 0.28 to 0.80;
  - 067778/7001: 0.24 to 0.99.
- 2a7385 stays the lowest. Its rich empty land is partly the rain mismatch (section 1c), desert to every habitat.
- Dragons per run rise in 11 of 12 paired runs. 1df1c3/7000 halves (120k to 62k). There red, black, bronze, storm giants and fire giants fall too, kinds that A does not touch, at densities 2-14x sparser. That is the peoples' history going another way on that roll (more pressure), not the change itself; its sister roll rises 107k to 151k.
- Per-people pass by people changes by at most one run of 12 for any people except tritons (2 to 4 runs).

The coverage target (share of a kind's country reached) falls for blue (1.00 to 0.86), brass (0.96 to 0.90) and black (0.85 to 0.79). Their country is larger now (blue), or rivals hold more of it. It rises for gold (0.36 to 0.70), copper (0.41 to 0.50), green and white.

### Caveats

- **A and B are not separated in this sweep.** The gold widening alone explains the gold dragons. The released land shows up in the pockets as "country" (no dominant land type: 17 to 1,018 per run) and as hills and steppe next to a kind's own country. A run with `megafauna.RELEASE = False` would split the two. It was not done, to keep the CPU light.
- The dragon count is still dominated by blue dragons in the deserts (65%), as on main (PW-990's food budget).
