# Scout 237 (PW-1497 pass 2 of 3, PW-1509 option A): the overriding plate contracts

Scout 237, 2026-11-08/09. Base: main a1db4525. Follows scout 209 (`scout6.md`), which holds the sources and the
first five screens.

## In plain words

- **Option A is built and it fixes what broke last time, but at the rate tried it makes far too much high ground.**
  The overriding continent now really shrinks: near an ocean-continent trench its edge closes up a whole cell at a
  time, the cell's crust is piled into a narrow belt behind the arc, and the cell becomes sea floor. Volume is kept
  exactly; the plate loses area the way Earth's does. It is off by default (`andean_shortening = 0`), so main is
  unchanged (golden tests pass).
- **What worked** (baseline: main on the same 3 L6 seeds x 600 Myr, scout 209's numbers on identical physics): the
  share of high ground near ocean-continent margins rose from 11-18% to 22-25% (Earth 25%), and continental area
  held far better than scout 209's edge arm (35-36% of the surface against main's ~40%; the edge arm fell to 27-31%).
- **What failed:** at a share of 0.4 of the plate's advance (the central Andes' present rate), land above 3 km is
  10.6-12.3% of land against main's 1.4-2.7% (Earth 2.6%). Three quarters of that high ground sits more than ~240 km
  from a live margin: belts outlive their trench.
- **Promising lead, not judged:** a cheap L5 rate sweep (one seed, 600 Myr) at share 0.1 (about the Andes' long-term
  mean, since they shorten in bursts) gave land above 3 km 1.7% (main 2.9% on the same L5 seed) with 29% of it at
  margins; 0.2 and 0.4 gave 4.2% and 6.9%. One seed and L5 only, so this is a lead for the third pass, not a result.
  The L6 screen of share 0.1 was not run: the machine's load stayed at 30-250 all night (rule: no new batch over 30).
- **Verdict: needs another pass** (strike 3 of 3): L6 screens at share 0.1 (and 0.05) on the same seeds, then the
  judge if it holds. If 0.1 also blows up high ground at L6, park PW-1497 for good as a known Earth difference.

## 1. Diagnosis (written before any L6 run)

### How a collision's overlap works today

- Every plate keeps its crust on its own copy of the grid and moves rigidly (`plates.Plates`, a rotation `Q`).
  `plate_kernels.resolve` decides, for each world cell, which plate's crust shows there. Where two continents
  overlap, the winner keeps the cell and the loser's cell is **un-owned on the loser's grid** (`owned[k, r] =
  False`): the loser's plate loses that area for good. Its thickness is added to `stacked` at that world cell,
  and `crust.stack_collisions` spreads `stacked` over a belt a few hundred km wide (Himalaya plus Tibet).
- So a collision already does what Earth does: **volume is kept, area is lost** by the plate that is shortened.
  Nothing else in the model refills that area directly; the area thermostat (`crust.thermostats`, the factor
  `shrink` on subduction erosion, 0.2-5x) is the only lever, and the sources of new area (island arcs born
  continental, rifted margins, welds) do the rest.

### What contraction would reuse

- An overriding continent at an ocean-continent trench is not overlapped by anything, so resolve never pulls
  its cells. Contraction has to be its own step, but it can work the same way: area is taken from the
  overriding plate a whole cell at a time, and the cell's crust is stacked behind it on the same plate.
- Implementation (`crust.andean_contraction`, after subduction erosion in `Simulation._physics`):
  - rate per trench-edge cell = `andean_shortening` x the overriding continent's own speed toward the trench
    (cm/yr, clipped to 0..convergence). Scout 209's control: the trench is pinned by the slab (Schellart 2008:
    stable or advancing trench goes with shortening), and the central Andes take up 1-1.75 cm/yr of the
    foreland's ~3 cm/yr (Medvedev et al. 2006), a share of 0.33-0.58.
  - Each plate pools the area its edge has shortened (`plates.short_pool`, km^2: rate x step x trench length),
    like `rift_pool` pools stretched crust. While the pool holds a cell's area, the edge cell shortening
    fastest closes up: its **whole column** goes into a narrow belt behind it and the cell becomes ocean floor
    at the trench, by the same path as a subduction-eroded edge (`crust.to_ocean`, now shared). The plate's
    coastline steps back one cell, as the Andean coast does when the forearc shortens or is eroded.
  - The belt: a Gaussian `ANDES_BELT` = 1.2 level-5 cells (~290 km e-folding) on the plate's own continent,
    with the arc's forearc gap (FOREARC_KM, little lands within ~120 km of the trench), **normalised so the
    belt receives exactly the closed cell's crust**. Width check: Gotberg et al. 2010 say 240-300 km of
    shortening of a 35-40 km crust builds a 60-70 km crust "under the whole plateau"; 270 x 37.5 / (65 - 37.5)
    = ~370 km, the width that budget implies. The collision spread (`surface._spread` 6 x scale^2 diffusion
    passes) is not used: scout 209 found it carried the belt ~300 km inland where it outlived its trench.
  - The belt counts as squeezed crust (added to `stack_add`): folded, orogen rock, not thinned by stretching.
  - Option `andean_steer`: the area thermostat's `shrink` factor scales the rate too, since contraction and
    subduction erosion are both the trench's sinks of continental area.
- Done as a world-frame step on the Column, not inside the numba `resolve`: the cell that closes is a world
  cell owned by the overriding plate, and `_write_back` writes it to the plate's grid as ocean floor, which is
  the same as un-owning it on the continent and letting ocean in. No change to resolve's ownership rules.

### What could break

- **Area bookkeeping.** This is the risk. Shortening moves ~7x more crust per km of trench than the arcs
  (scout6.md), and each km of it costs a km of the plate's width. At 1 cm/yr along a trench, the coast steps
  back 10 km/Myr; subduction erosion's nominal 0.05 km/Myr per cm/yr over a 120 km forearc retreats it
  ~1.5 km/Myr at 5 cm/yr. So unless the advance is small, contraction is the bigger area sink, and the area
  thermostat can only turn subduction erosion down to 0.2x. Expect continental area to fall until the area
  sources (arcs born continental, margins) catch up, as scout 209's edge arm did (40% -> 27-31%).
  Difference from that arm: the edge was drained to 10 km first (a trough at every margin) and paid as
  thickness; here the column moves whole and the coast stays high to the end.
- **Volume** is kept exactly (booked: `andean.closed` out, `andean` in), so the volume thermostat sees
  nothing directly; it sees the area change through mean thickness.
- **Plate identity.** A plate can lose many edge cells; `events` splits and dies are untouched. The pool is a
  new per-plate field, reset in `new_slot`.
- **Grid remapping.** The closed cell is written back as the overriding plate's ocean floor at the trench (its
  age from the neighbouring floor, `floor_age`), exactly as subduction erosion leaves it; the next steps'
  resolve and boundaries treat it like that. No holes are left (coherence does not weld at trenches).
- **Total high ground** may rise: the crust is concentrated even though it is not new.
- **Climate**: more high ground, more weathering, cooler (scout 209's thermostat arms ran 1-4 C cooler).

### Sourced numbers (fetched; see scout6.md for the full list)

- Medvedev, Podladchikov, Handy & Scheuber 2006 (ch. 23, *The Andes*): central Andes shorten 1-1.75 cm/yr of
  a ~3 cm/yr westward foreland; southern Andes 0-0.5 cm/yr.
- Gotberg, McQuarrie & Carlotto 2010 (GSA Bull. 122): 240-300 km of shortening to build the plateau's 60-70 km
  crust from 35-40 km; shortening began ~45-35 Ma (long-term ~0.6-0.8 cm/yr).
- Schellart 2008 (GSA Bull. 120, abstract re-read this pass): "trench retreat generally corresponds to
  extension while an approximately stable trench or trench advance generally corresponds to shortening";
  orogenesis "when the overriding plate is moving trenchward at 0-2 cm/yr (e.g., Andes, Japan)", in "central
  regions of wide subduction zones (>= ~4000 km)"; extension "only found close to lateral slab edges or during
  overriding plate motion away from the center of a wide subduction zone".
- Not obtained this pass (pages refused): plateau and orogen widths from Allmendinger et al. 1997, and the
  global share of shortening margins (Lallemand et al. 2005). The belt width is the one implied by Gotberg's
  budget above.

### Candidates

| arm | share | steer | expectation | risk |
|---|---|---|---|---|
| main | 0 | - | Andes share 11-18%, >3 km 1.4-2.7% | - |
| a40 | 0.4 | no | margin belts; area down | area loss past the thermostat |
| s40 | 0.4 | yes | margin belts, area held by the thermostat | thermostat turns contraction off where area is short |

L5 smoke (seed 1, against main L5 seed 1 at the same times; continental area as a share of the surface):
a40 0.358 at 200 Myr (main 0.361); s40 0.340 at 200 and 0.378 at 300 Myr (main 0.397); share 0.15 0.413 at 300.
Volume per cell 13.3-13.7 against main's 13.2-13.3. Contraction moved ~10x the crust subduction erosion removed and
about as much as collisions stacked, yet area fell only 0-2 points: much less than scout 209's edge arm.

## 2. Screens

Setup: L6, seeds 1, 2, 6001, 600 Myr, `--set andean_shortening=SHARE` (scratch runs, gone with the scratchpad),
measured with `scout7_measure.py` (scout6_measure's Andes share and hypsometry plus land and continental-crust
share of the surface, median of ~29 frames with t >= 100 Myr). **Baseline: main on the same seeds and window.**
Main's numbers are scout 209's (main e6cb463c): no commit touches `planet/tectonics`, `climate.py`, `surface.py`,
`kernels.py` or `grid.py` between e6cb463c and this base (a1db4525), so a run of main here is the same run. (A fresh
baseline was started and stopped at 100 Myr to free its cores for the arm under the night's load.)

| arm (seeds 1, 2, 6001) | Andes share of >3 km land | land >2 km | >3 km | >4 km | land % | continental crust % (median, end) |
|---|---|---|---|---|---|---|
| main | 11.4, 18.4, 18.2 | 6.9, 7.9, 5.7 | 2.7, 2.7, 1.4 | 0.75, 0.88, 0.27 | 34.0, 33.3, 34.0 | ~40 (scout6: 40% throughout, seed 1) |
| a40 (share 0.4) | 24.9, 21.7, 23.4 | 22.1, 23.5, 20.3 | 12.3, 11.4, 10.6 | 5.2, 5.5, 4.7 | 30.5, 30.7, 31.3 | 35.7 / 37.9, 35.3 / 37.2, 36.1 / 38.1 |
| scout 209 e05 (edge drain, seed 1) | 20.2 | 38.1 | 25.0 | 14.4 | 27.7 | 27-31 |

Top cell 6.6-6.7 km in every a40 run (the PW-1446 cap, as in main and scout 209's arms).

L5 rate sweep (seed 1, 600 Myr, the same measure done in-process with a 1-cell L5 margin zone, so its margin share
is not comparable with the L6 column above; main against arms only):

| share | >3 km (% land) | of it near a margin | land % | continental % |
|---|---|---|---|---|
| 0 (main) | 2.92 | 0.9 | 31.5 | 41.1 |
| 0.1 | 1.68 | 28.6 | 30.9 | 40.0 |
| 0.2 | 4.17 | 21.8 | 29.4 | 39.1 |
| 0.4 | 6.89 | 23.5 | 30.2 | 39.5 |

Not judged: hard failures (no 1 Gyr draws: nothing reached the bar for the judge), scorecard (no candidate).

## 3. What the screens say

1. **Real contraction solves the area problem that killed scout 209's edge arm.** Moving the whole column and
   letting the coast step back cost 4-5 points of continental area at share 0.4 (40 -> 35-36%, recovering to 37-38%
   by 600 Myr as the area thermostat answers), not 9-13. The volume budget is exact by construction.
2. **The margin share responds the right way** (11-18% -> 22-25%, Earth 25%), so the mechanism makes Andes where
   Andes should be.
3. **The total is the problem, and it is set by the rate.** At share 0.4 the contraction moves about as much crust as
   all collisions and ~10x what subduction erosion removes (L5 budget, `andean.closed` against `subd.erosion`).
   That is the present central-Andean rate applied at every advancing ocean-continent margin all the time. Earth's
   Andes did most of their shortening in the last ~40 Myr of ~200 Myr of subduction (Gotberg et al. 2010), and the
   southern Andes barely shorten (Medvedev et al. 2006): the long-term mean per km of margin is several times lower.
   A share of ~0.1 is that long-term mean with a model advance of ~2-3 cm/yr. The L5 sweep is consistent with this
   (0.1 lowered total high ground on that seed; 0.2 and up raised it), but one L5 seed is noise-level evidence.
4. Belts outlive their trench: even with the narrow belt, ~75% of a40's high ground lies more than 2 L6 cells from a
   live margin. A lower rate lowers this too; a belt that decays faster is not proposed (it would be a fudge on
   erosion, which already wears high ground faster the higher it is).

## 4. Next (pass 3 of 3)

- L6 screens of share 0.1 and 0.05 on seeds 1, 2, 6001 x 600 Myr (`scout7_measure.py`), against main's row above.
  Pass if: Andes share >= ~20%, land above 3 km within or near main's 1.4-2.7% (well under ~4%), continental area
  within ~2 points of main. Then the full judge (36 draws, two-tier bar) and `tools/scorecard.py`.
- If share 0.1 still blows up total high ground at L6, park PW-1497 (option B: high ground mostly collisional).
- Not tried: `andean_steer` (the area thermostat also steering contraction) at L6; on L5 it changed little.

Draft: `issue-tracking/inbox/draft-andean-contraction-pass3-low-rate.md`.
