# Lane 288 (PW-1683): why an L7 run holds more land above 3 km than L6

Lane 288, 2026-11-10. Base: main 5411930b. Its simulation code is that of 7dae542a (lane 286's base): the only
`planet/` changes since are worlds, zooms and polities (`git diff --stat 7dae542a..5411930b -- planet/`:
export, humanuse, polity_live, zoom/*), none in the run. Scripts: `docs/review/tectonics/mountains/l7_high_ground.py`
(this lane: thermostats, volume and area against target, hypsometry, crust books per checkpoint) and
`andes_late_series.py` (lane 286). Scratch root /data/personal/scratch/lane288 (runs listed in section 2).

## 1. Diagnosis (written before the screen)

### 1.1 What sets how high continents stand

Mean continental thickness is crust volume / continental area. Two thermostats hold both near their targets
(`planet/tectonics/crust.py:54-79`, `thermostats`): arc growth follows volume against
`target_fraction x continental_thickness` (35 km), subduction erosion follows area against `target_fraction`
(40%). Their factors are clipped (arc growth x0.1-5, subduction erosion x0.2-5, `crust.py:76-77`), so either can run
out of lever. With both on target, mean thickness is 35 km at any level. Lane 286's L7 run had 36.9 km late
against L6's 34.9 km (same seed and code, andes-late.md section 1.2 and 3): 5.7% thicker, so at L7 the volume runs
above target, the area below, or both. Land above 3 km is the tail of the hypsometry: ~100-200 m of mean lift
moved L6's tail by about a point (andes-late.md 1.2).

A second, separate way L7 can have more land above 3 km at the same mean thickness: the shape of the tail. L7
resolves belts half as wide, so the same volume in a belt can stand higher in fewer cells.

### 1.2 Is it this week's Andes mechanism or the L7 grid?

What each would leave in the books:

- **The Andean mechanism (PW-1497)**: Andean closing (`crust.py:271-330`, `andean_contraction`) moves a closed
  edge cell's whole column into a belt behind it and turns the cell to ocean: volume kept, area lost. Lane 286
  found it the largest area sink at L6 (book `andean.closed` 59-61 thousand km x L5 cells by 1 Gyr against
  subduction erosion's 15-28 thousand) and seed 1's area thermostat sitting at its floor (x0.20-0.24) from
  400 Myr. If the same sink outruns the area lever at L7, area falls below target and the continents thicken.
  Its signature: on-arm area below target with `shrink` at 0.2, the off arm on target and thinner.
  The mechanism is written per km of trench (pool in km^2, `crust.py:300-310`; belt width `ANDES_BELT x scale`
  cells), so it should be level-neutral per km, with one level-dependent cap: the pool is capped at
  `cell_km2 x (candidates - closed)` (`crust.py:310`), which at L7 is half as many km^2 per km of trench.
- **The L7 grid itself**: area processes that act per cell rather than per km. `coherence`
  (`crust.py:579-651`) welds one-cell inlets into continent and drops one-cell thin shreds into ocean: at L7 a
  cell is a quarter the area and coastlines carry twice the cells per km, so the weld/shred balance is a
  per-level area source or sink the area thermostat must answer. Continental birth (`birth_and_cratons`,
  `crust.py:683-715`) and the 15-km "gone" bound of subduction erosion (`crust.py:247-251`) are per cell too.
  Its signature: both arms thick at L7, area or volume off target the same way in both.
- **The tail's shape**: at matched mean thickness, L7 above 3 km higher than L6. Signature: the off arm thick
  at L7 by the same amount, and >3 km at L7 higher than L6 even where the thickness matches. Crustal flow is
  level-consistent by construction (`crust.py:568-569`: substeps x scale^2; `plate_kernels.py:250-262`), the
  collision stacking spread likewise (`crust.py:197`: 6 x scale^2 passes of the same kernel), and the
  height cap is on the column's height, not per cell (`isostasy.py:244-253`).

### 1.3 The level guard

The PW-1556 guard (`tests/test_nest.py:111-142`, slow) builds seed 21's unrun L7 ground and checks that the
climate computed on L7 and through `nest.climate_coarse` on L6 give the same arid share (within 2.0 points) and
land rain (within 5%). It is a climate guard only: it runs no tectonics and does not compare crust thickness,
area, volume or hypsometry between L6 and L7 runs. Nothing in the suite would catch L6 and L7 continents drifting
apart in thickness.

### 1.4 Candidates (before measuring)

1. **The Andean area sink is beyond the area thermostat's reach at L7** (signature above). Fix candidates: a
   continent that has lost area to shortening gives it back by extension (lane 286's candidate 3, collapse that
   widens at the margin), not `andean_steer` (rejected by lane 286, 2.2).
2. **A per-cell area process at L7** (coherence or birth): measure the books per level. Fix: make the process
   per km (as subduction erosion was made in PW-052).
3. **Within bounds**: if the off arm is as high as the on arm at L7 and the excess is the tail's shape, it is the
   grid resolving narrower belts; Earth on the L7 grid is 2.5% (ETOPO1), and 4.3% would be a 1.7x tail without
   unsoundness. A guard against thickness drift between levels would still be worth a draft.

## 2. Screen

### 2.1 Runs

All `planet simulate --seed S --level L --myr 1000 --checkpoint-every 20 --threads 4`, on main 5411930b (run code
of 7dae542a, section header), `PLANET_DATA=/data/personal/scratch/lane288/data`:

| run | seed | level | arm | final land | reproduces |
|---|---|---|---|---|---|
| 2e1bc2 | 2 | 7 | on (defaults: `andean_shortening` 0.1, `collapse` 30) | 34.0% | lane 286's L7 run (8f0042, deleted): >3 km median 600-1000 4.33%, mean 4.01%, >4 km 1.29%: identical |
| 6286ce | 2 | 7 | off (`andean_shortening=0 collapse=0`) | 34.5% | - |
| dc517e | 2 | 6 | on | 33.4% | lane 286's L6 on arm and scorecard c219720a seed 2 (33.4%); >3 km 3.30% as andes-late.md 2.1 |
| 296220 | 2 | 6 | off | 34.4% | lane 286's L6 off arm and scorecard a626c541 seed 2 (34.4%); >3 km 2.67% |

Measured with `l7_high_ground.py` on every 20-Myr checkpoint; medians (means) over 600-1000 Myr (21 checkpoints).

### 2.2 L7 against L6, mechanism on and off (seed 2)

| level | arm | land > 3 km | > 4 km | Andes share of > 3 km | mean cont. crust (km) | cont. area % (target 40) | volume / target | area thermostat (subduction erosion x) | mean land (m) |
|---|---|---|---|---|---|---|---|---|---|
| 7 | on | **4.33 (4.01)** | 1.29 (1.45) | 19.2 | **36.7 (36.9)** | 39.7 | 1.04 | **0.20 (its floor) the whole window** | 996 (1000) |
| 7 | off | 2.77 (2.81) | 0.82 (0.83) | 12.3 | 35.5 (35.5) | 41.0 | 1.03 | 0.37 (0.39) | 755 (781) |
| 6 | on | 3.30 (3.41) | 1.20 (1.70) | 31.4 | 34.8 (34.9) | 41.1 | 1.01 | 0.68 (0.66) | 813 (825) |
| 6 | off | 2.67 (2.84) | 1.01 (1.12) | 8.8 | 34.3 (34.2) | 41.7 | 1.02 | 0.47 (0.52) | 746 (796) |

Earth on the grid (ETOPO1, andes-late.md section 0): > 3 km 2.4% (L6) / 2.5% (L7), > 4 km 1.5% / 1.6%; mean land
~840 m.

- **The L7 excess is the Andean mechanism's, not the grid's.** Without it, L7 holds 2.77% of its land above
  3 km, as L6 does (2.67%) and as Earth on the L7 grid (2.5%). With it, 4.33%: +1.56 points at L7 against +0.63
  at L6.
- **How: the area thermostat runs out of lever.** At L7 with the mechanism on, subduction erosion (the area
  thermostat's only lever) sits at its floor (x0.20, `crust.py:77`) from ~350 Myr to the end (x0.21 median over
  100-600 Myr too). Area is held just on target (39.7%) with no slack, crust volume runs 4% over target
  (the volume thermostat's integral, wound up in the early deficit, as in every arm), and the continents are
  1.2-1.4 km thicker than the off arm's. That lifts everything ~220-240 m (mean land 996 against 755 m), which
  moves the tail above 3 km most. The Andes are also a larger share of it (19% against 12%).
- **The grid adds ~1 km of mean thickness in both arms** (L7 off 35.5 against L6 off 34.3 km; on 36.7 against
  34.8), but in the off arm that does not show as high ground (2.77% against 2.67%; mean land 755 against 746 m).
  It is not what makes the L7 on arm high.

### 2.3 Area books: where the continents' area goes (`area_books.py`, 600-700 Myr resumed from each run's checkpoint)

Change in continental area by process, % of the surface per 100 Myr:

| process | L7 on | L7 off | L6 on | L6 off |
|---|---|---|---|---|
| stretch (rifted margins, necking) | +3.68 | +2.93 | +3.67 | +2.45 |
| coherence welds | +2.49 | +2.08 | +3.41 | +2.70 |
| birth (arcs, sediment wedges) | +2.48 | +1.88 | +1.78 | +1.54 |
| coherence shreds | -2.60 | -2.70 | -3.46 | -2.36 |
| resolve (plate motion, collision overlap) | -2.30 | -2.19 | -2.48 | -2.63 |
| **Andean closing** | **-1.82** | 0 | **-2.08** | 0 |
| subduction erosion (thermostat x) | -0.49 (x0.20) | -0.59 (x0.34) | -1.10 (x0.62) | -0.38 (x0.34) |
| net | +1.49 | +1.40 | -0.17 | +1.34 |

- Andean closing is the same sink per level (-1.8 to -2.1 points per 100 Myr): the mechanism is level-neutral,
  as written (pool in km^2 per km of trench).
- It is as large as the whole of subduction erosion's lever: subduction erosion at its nominal rate would take
  ~1.7-2.5 points per 100 Myr here (its take over its factor), and the floor leaves at most ~80% of that to give
  back. So with the mechanism on, the area balance has little room on any level; which run hits the floor is
  the run's own history (L7 seed 2 here; L6 seed 1 in lane 286, x0.20-0.24 from 400 Myr, 35.7 km against 34.2).
  At L6 seed 2 the run's area stays above target (41.1%) and the lever never runs out.

### 2.4 Second L7 seed (seed 1)

Runs 213321 (on) and 28d710 (off), same settings. Medians (means) over 600-1000 Myr:

| level | arm | land > 3 km | > 4 km | Andes share | mean cont. crust (km) | cont. area % | volume / target | area thermostat | mean land (m) |
|---|---|---|---|---|---|---|---|---|---|
| 7 | on | **5.62 (5.83)** | **3.42 (3.12)** | 24.7 | **37.7 (37.7)** | **37.6** | 1.02 | **0.20, floor, from ~100 Myr to the end** | 1060 (1090) |
| 7 | off | 3.90 (4.70) | 1.11 (2.09) | 8.9 | 35.2 (35.3) | 40.5 | 1.02 | 0.33 (0.33) | 921 (886) |
| 6 | on (lane 286) | 3.36 (4.22) | 1.55 (1.99) | 25.4 | 35.7 (mean) | 40.1 (mean) | 1.01-1.04 | 0.20-0.24 from 400 Myr | - |
| 6 | off (lane 286) | 3.54 (3.28) | 1.69 (1.46) | 8.9 | 34.2 (mean) | 42.5 (mean) | 1.01-1.04 | - | - |

- **Same cause, stronger.** The area thermostat sits at its floor for nearly the whole run, and here area does
  not even hold its target (37.6% against 40%): the continents are 2.5 km thicker than the off arm's and land
  above 3 km is 5.6% (Earth 2.5%), above 4 km 3.4% (Earth 1.6%), twice Earth's.
- Seed 1 is a high-ground planet in both arms and at both levels (off arm 3.9% at L7, 3.5% at L6), so part of its
  excess is the planet's; the mechanism adds +1.7 points above 3 km and +2.3 above 4 km on top.
- At L7 the floor is hit on both seeds tried (2 of 2); at L6 on one of three (seed 1; lane 286). The L7 off arms
  run with a little less area slack (thermostat x0.33-0.37 late against L6 seed 2's x0.47; continents ~1 km
  thicker, 2.2), which is the grid's share: it makes the floor easier to reach, but it is not what raises the
  high ground (L7 off arms 2.8% and 3.9%, L6 off 2.7% and 3.5%).

## 3. Verdict and candidates

- **Cause: the Andean mechanism (PW-1497), through the area thermostat's floor.** Andean closing removes
  1.8-2.1% of the surface of continental area per 100 Myr, the same at L6 and L7 (2.3); that is about all
  subduction erosion, the area thermostat's only lever, can give back before its x0.2 floor. On runs that are
  short of area anyway, the lever pins, the same volume covers less area, and every continent stands higher.
  Not the L7 grid: with the mechanism off, L7 has the same share of land above 3 km as L6 (seed 2: 2.77% against
  2.67%; seed 1: 3.90% against 3.54%).
- **Unsound?** Partly. Shortening that removes area with nothing that gives it back is a one-way leak in a model
  whose area is otherwise balanced by a clamped thermostat. Seed 2's late excess (4.3% above 3 km, 1.3% above 4)
  is a plausible planet; seed 1's (5.6% / 3.4%, area 2.4 points under target) is not Earth-like and is a
  floor-pinned control, not a physical state.
- **Candidates** (none built in this lane; the hand-off section says why):
  1. Collapse that gives area back (lane 286's candidate 3): a thick dead belt at a continent's edge spreads
     outward into the same plate's ocean cell as well as inward, so lower-crustal flow can widen the continent
     (Basin and Range; Dewey 1988). In `flow_and_orogeny` (`crust.py:547-576`) the flow runs only on
     `inner_edges` (continental cells of one plate, `crust.py:168-189`), so collapse today is area-neutral.
     A feedback on thickness itself; sound in kind. Needs building, a screen on L7 seeds 1 and 2 against the
     on arms here, then the 18-draw paired judge.
  2. `andean_steer = 1`: rejected by lane 286 (2.2 there).
  3. A lower subduction-erosion floor (`crust.py:77`, x0.2 -> x0.05): a clamp move; rejected without running.
- **Level guard**: the PW-1556 guard is climate-only (1.3). The L7 grid's own ~1 km of extra thickness does not
  show as high ground, so no new guard is proposed.

## Hand-off state

Stopped at the diagnosis and screen (tool-call budget). Nothing in `planet/` changed, no default change, no judge
run. Inbox draft `draft-andean-area-sink-exhausts-thermostat.md` carries candidate 1. The L7 runs 2e1bc2,
6286ce (seed 2) and 213321, 28d710 (seed 1) are kept under /data/personal/scratch/lane288/data/runs for the
lane that builds candidate 1 (its baselines); the L6 runs were deleted.

# Lane 292 (PW-1693): collapse that gives area back

Lane 292, 2026-11-10. Base: main bb30e268 (run code as 5411930b: lane 288's merge adds docs and the scorecard's
`late` block only). Baselines: lane 288's L7 runs on 5411930b (section 2.1, 2.4): 2e1bc2 (seed 2 on), 6286ce (seed 2
off), 213321 (seed 1 on), 28d710 (seed 1 off), kept under /data/personal/scratch/lane288/data/runs.

## 4. Design note (written before coding)

### 4.1 What collapse does today

- `flow_and_orogeny` (`planet/tectonics/crust.py:547-576`) runs `plate_kernels.crust_flow` (`plate_kernels.py:250-262`)
  on the edges `inner_edges` gives it (`crust.py:168-189`): continental cells of one plate, plus collision edges
  between two continents. A cell not folded for `collapse_delay` (20 Myr, `record.T_FOLD`) on both ends of an edge
  flows (1 + `collapse`) = 31 times faster (`crust.py:559-564`).
- Flow on those edges only moves crust between continental cells: volume kept, and no cell changes from ocean to
  continent, so collapse is area-neutral. A dead belt at a continent's edge can only spread inward; the crust that
  Andean closing stacked behind the trench (`andean_contraction`, `crust.py:271-330`, whose closed cells became
  ocean) never gets that area back. The area it took is answered only by subduction erosion's thermostat, which
  sits at its x0.2 floor (`crust.py:77`) on L7 seeds 1 and 2 (sections 2.2-2.4).

### 4.2 The change (`collapse_margin`, default 0 first)

In `flow_and_orogeny`, beside the inner edges, the edges from a dead continental cell to a neighbouring ocean cell
of the same plate also flow, at the dead belt's rate times `collapse_margin` (1: as fast as inland). Not at a trench
(either side of a subducting edge: a live Andean margin is held up by the slab, and its forearc notch is
subduction erosion's), not into a hotspot pile. The kernel is unchanged, so flow only runs where the thicker side
is over 40 km (`crust_flow`'s x = (t - 40)/10): only thick dead belts spread out, a normal 35 km coast does not.
An ocean cell filled to `BECOMES_CONT_KM` (20 km) becomes continental crust there and then: thin, extended crust
(the belt's basement rock, its rift time set now, as `rifted_margin` lays one), booked as "collapse.margin". Crust
in a cell not yet filled sits on the ocean floor until it fills (booked out with "flow+cap"). Volume is kept;
area grows by the cells the spreading belt fills, so a run that loses area to shortening gets some back where
the shortened crust collapses.

### 4.3 Why it is physical

Gravitational collapse is the decay of the lateral contrast in gravitational potential energy a thickened belt
holds (Rey, Vanderhaeghe & Teyssier 2001, "Gravitational collapse of the continental crust: definition, regimes
and modes", Tectonophysics 342(3-4):435-449, doi:10.1016/S0040-1951(01)00174-3; abstract read on the
repository.geologyscience.ru record): in fixed-boundary divergent collapse the orogen grows laterally at the
expense of its forelands (brittle gravitational sliding plus horizontal spreading of the lower crust); in
free-boundary collapse the thick crust thins homogeneously. Either way the belt's crust ends up wider: the area
shortening took is given back by extension (Dewey 1988, already the model's collapse source). A thick dead belt
whose foreland is the ocean side of its own plate is the free side; its spreading moves the continent's edge
seaward as thin extended crust, which is what the change lets the flow do. It is a feedback on thickness itself
(only crust over 40 km spreads), not on a global area target, and it does not touch the thermostat's clamp.

### 4.4 Screen bar

L7 seeds 1 and 2 to 1 Gyr, `collapse_margin=1`, against the on arms 2e1bc2 / 213321, medians over 600-1000 Myr
(`l7_high_ground.py`): the area thermostat off its floor; land above 3 and 4 km down toward the off arms (6286ce,
28d710); the Andes share of land above 3 km kept (on arms 19.2% / 24.7%).

## 5. Second arm: PW-1287 option A, water-loaded drowned continent (coordinator's addition)

Coordinator ruling A (correct physics), screened beside collapse_margin, each behind its own parameter
(`water_loaded`, default 0) and in its own commit. Side measures in every arm: shelf share of the ocean (0 to
-200 m) and the median submerged continental cell's depth, late-window medians (PW-950 baseline ~1.4% and
~-1,500 m at L6; Earth on the L6 grid ~5.8% and -184 m).

**What it changes.** `isostasy.elevation` (`_elevation_k` and the numpy path) gives continental crust standing
below the sea `wet` x its air-loaded depth, `wet = K_SEA / K_LAND = rho_m / (rho_m - rho_w) = 1.456` with
`water_loaded = 1` (`Simulation.wet`); the air-loaded height includes `sediment_lift`, so a drowned shelf's
sediment lifts it at the under-water rate (K_SEA), as on the ocean floor, which is PW-1287's bookkeeping gap. The
join at the shore is continuous (0 both sides) with a kink, which is the physics: water loading starts where the
water does. Erosion and deposition's elevation-per-km (`earth.erode`'s `iso`, `iso_dep`) and the reefs' fill take
the same factor on drowned continental cells, so a fill of d metres lays d / (wet x rate) km.

**Expected sign, stated before the screen.** This deepens drowned margins, it does not raise them: under water each
km of thinning sinks the column (rho_m - rho_c) / (rho_m - rho_w) ~ 220 m against 150 m in air (the standard air- to
water-loaded conversion). PW-950's own 2026-10-28 update records lane 23 trying it at L6 (seed 1, branch code):
submerged median -766/-875/-997 m air-loaded against -1105/-1135/-1369 m water-loaded at 200/300/400 Myr, shelf
lower in 6 of 8 samples; and McKenzie 1978's E0 is larger under water (3.2 against 2.2 km, the ticket's 10-29
update). PW-1287's own option text says A "raises the drowned margins"; that holds only for the sediment term
(a km of sediment lifts a drowned shelf 1.46x more), not for the crust's depth. So A is expected to lower the shelf
share and deepen the submerged median, and to lower sea level a little (more water held on drowned continent,
`earth.continent_water`). It is screened as ruled; if it causes trouble it is dropped, not tuned.

## 6. Screens (L7 seeds 1 and 2, 1 Gyr, medians over 600-1000 Myr)

All `planet simulate --seed S --level 7 --myr 1000 --checkpoint-every 20 --threads 4 --set ...` on this branch
(dea5bee9 / 5c55c21a: both parameters default off, so the off settings run main bb30e268's code), scratch
/data/personal/scratch/lane292/data. Measured with `l7_high_ground.py` (lane 292 added `shelf`, the share of the
ocean at 0 to -200 m, and `subm`, the median submerged continental cell, and reads pre-lane-292 runs with both
parameters off). Baselines: lane 288's runs on 5411930b (same run code), re-measured here for the shelf columns.

### 6.1 collapse_margin = 1 alone

| seed | arm (run) | > 3 km | > 4 km | area thermostat | cont. area % | mean cont. crust km | Andes share of > 3 km | shelf % of ocean | submerged median m |
|---|---|---|---|---|---|---|---|---|---|
| 1 | on, main (213321) | 5.62 | 3.42 | 0.20 floor | 37.6 | 37.7 | 24.7 | 1.03 | -1140 |
| 1 | off, main (28d710) | 3.90 | 1.11 | 0.33 | 40.5 | 35.2 | 8.9 | 1.34 | -878 |
| 1 | **collapse_margin (4635ef)** | 4.96 | 1.74 | **0.20 floor** | 38.5 | 37.8 | 23.5 | 1.00 | -982 |
| 2 | on, main (2e1bc2) | 4.33 | 1.29 | 0.20 floor | 39.7 | 36.7 | 19.2 | 1.28 | -1050 |
| 2 | off, main (6286ce) | 2.77 | 0.82 | 0.37 | 41.0 | 35.5 | 12.3 | 1.70 | -1030 |
| 2 | **collapse_margin (d4f6be)** | 3.45 | 1.45 | **0.20 floor** | 38.2 | 37.4 | 20.4 | 0.81 | -1000 |

Books at 1 Gyr (km x L5 cells of crust): `collapse.margin` +9.25e3 (seed 1) / +9.21e3 (seed 2) against
`andean.closed` -5.44e4 / -5.82e4. The margin cells are laid at ~20 km and the closed cells held ~35-40 km, so
collapse gives back roughly a quarter to a third of the area Andean closing takes.

- **Fails the screen's main bar.** The area thermostat stays at its floor (x0.20) through the late window on both
  seeds, as on main; the continents are no thinner (37.8 / 37.4 km against 37.7 / 36.7) and area no closer to
  target on seed 2 (38.2% against 39.7%).
- Land above 3 km falls on both seeds (5.62 -> 4.96, 4.33 -> 3.45), still above the off arms; above 4 km falls on
  seed 1 (3.42 -> 1.74) and rises a little on seed 2 (1.29 -> 1.45). With the thermostat unchanged this is the
  dead coastal belts spreading out, not the area balance being restored; two seeds cannot tell it from chaos.
- The Andes share is kept (23.5 / 20.4 against 24.7 / 19.2).
- Shelf and submerged median: no consistent change (shelf 1.00 / 0.81 against 1.03 / 1.28).
- Why it is weak: the flow kernel (`crust_flow`) moves crust only where the thicker side is over 40 km, so a belt
  spreads seaward only until its edge is down to ~40 km, and a new 20 km margin cell spreads no further unless the
  belt behind it is still over 40 km. Collapse on Earth runs until the potential-energy contrast is gone, nearer
  normal thickness, so the 40 km stop makes the model's seaward collapse end early. A revision that let margin
  spreading run below 40 km would need a new rate or reference thickness without a source, which is tuning; it
  was not attempted (section 7).

### 6.2 water_loaded = 1 alone (PW-1287 A)

| seed | arm (run) | > 3 km | > 4 km | area thermostat | cont. area % | mean cont. crust km | Andes share | land % | shelf % of ocean | submerged median m |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | on, main (213321) | 5.62 | 3.42 | 0.20 | 37.6 | 37.7 | 24.7 | 32.8 | 1.03 | -1140 |
| 1 | **water_loaded (145d7f)** | 3.96 | 1.84 | 0.20 | 38.3 | 37.6 | 20.1 | 33.0 | **0.81** | **-1500** |
| 2 | on, main (2e1bc2) | 4.33 | 1.29 | 0.20 | 39.7 | 36.7 | 19.2 | 34.0 | 1.28 | -1050 |
| 2 | **water_loaded (ea1b47)** | 3.82 | 1.44 | 0.20 | 38.9 | 37.9 | 21.1 | 33.7 | **0.96** | **-1440** |

- **As predicted in section 5, A deepens the drowned margins and shrinks the shelves**: submerged median -1140 ->
  -1500 m and -1050 -> -1440 m, shelf 1.03 -> 0.81% and 1.28 -> 0.96% of the ocean (PW-950's Earth on L6 ~5.8%,
  -184 m). The direction is the opposite of what PW-950 wants. No trouble with sea level or land (land 33.0 / 33.7%
  against 32.8 / 34.0%). It does not touch the area thermostat (floor on both).
- High ground moves (5.62 -> 3.96, 4.33 -> 3.82 above 3 km), but A changes nothing on land above sea level, so this
  is a different run history (erosion and deposition on drowned cells), not a mechanism on high ground; two seeds
  cannot tell it from chaos.
- A is the correct isostasy (it closes PW-1287's bookkeeping gap: sediment off a drowned shelf onto the ocean floor
  is now lifted at the same under-water rate on both), so it may still be wanted, but it makes the shelves worse,
  and PW-950's fix lies elsewhere (lane 23's suggestions: tapered necking, sediment wedges, wave-base planation).

### 6.3 Both (collapse_margin = 1, water_loaded = 1)

| seed | arm (run) | > 3 km | > 4 km | area thermostat | cont. area % | mean cont. crust km | Andes share | land % | shelf % of ocean | submerged median m |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | on, main (213321) | 5.62 | 3.42 | 0.20 | 37.6 | 37.7 | 24.7 | 32.8 | 1.03 | -1140 |
| 1 | **both (eb41d6)** | 3.33 | 1.56 | **0.20** | 38.6 | 36.9 | 23.5 | 33.8 | 0.94 | -1380 |
| 2 | on, main (2e1bc2) | 4.33 | 1.29 | 0.20 | 39.7 | 36.7 | 19.2 | 34.0 | 1.28 | -1050 |
| 2 | **both (a95c21)** | 2.89 | 0.95 | **0.20** | 38.7 | 36.9 | 30.4 | 33.5 | 1.17 | -1480 |

Books at 1 Gyr: `collapse.margin` +9.2e3 / +9.0e3 against `andean.closed` -5.6e4 / -5.8e4.

- The lowest high ground of the three arms on both seeds (seed 2 at the off arm's level), Andes share kept, but the
  thermostat is still at its floor and the continents are no thinner on seed 2 (36.9 against 36.7 km). Each part
  alone moved land above 3 km down by 0.5-1.7 points with the thermostat unchanged, so these are run histories
  diverging, not the area balance restored; two seeds are not enough to call a high-ground gain.
- Shelves: deeper and smaller, as with A alone.

## 7. Verdict (lane 292)

- **No arm passes the screen's main bar** (thermostat off its floor): all three stay at x0.20 on both L7 seeds.
  Seaward collapse gives back only ~1/4-1/3 of the area Andean closing takes (6.1). PW-1287 A deepens the drowned
  margins by ~400 m and shrinks shelves (6.2), as the physics says it must (section 5).
- So no paired judge was run and **nothing is on by default**: both parameters stay 0 (commits dea5bee9
  `collapse_margin`, 5c55c21a `water_loaded`), each in its own commit with tests (`tests/test_crust_belts.py`).
- No revision was attempted: the one that would strengthen collapse_margin (seaward spreading below 40 km) needs an
  unsourced reference thickness; it is option A of the draft below, for a decision.
- Drafts: `draft-area-thermostat-floor-unsolved-after-collapse-margin.md` (needs-decision: A/B/C),
  `draft-water-loaded-isostasy-deepens-shelves.md` (needs-decision: keep A off until PW-950's margin work).
- Scratch runs (lane 288's four baselines and lane 292's six) are still under /data/personal/scratch/lane288 and lane292: deleting them was denied by the permission system, so the coordinator deletes them (no symlinks inside); the per-checkpoint tables
  are in logs/measure_*.txt there.

# Lane 296 (PW-1703): option A, seaward collapse down to 35 km

Lane 296, 2026-11-11. Base: main f692572b. Parameter commit 46a94092. Scratch /data/personal/scratch/lane296.
Attempt 2 on the area-thermostat floor (attempt 1: lane 292's `collapse_margin`, section 7).

## 8. Diagnosis (written before the screen)

### 8.1 Where seaward collapse stops today

- `flow_and_orogeny` (`planet/tectonics/crust.py:547-592`) adds the margin edges from `margin_edges`
  (`crust.py:594-605`) to the inland edges and runs one kernel over both, `plate_kernels.crust_flow`
  (`plate_kernels.py:250-263`). Its rate is `k0 x mult x (x + x^3)` with `x = (max(t_a, t_b) - 40) / 10`
  (`plate_kernels.py:258` before this lane): a margin edge moves crust only while its belt cell is over 40 km.
- A filled ocean cell becomes continent at `BECOMES_CONT_KM` = 20 km (`margin_spread`, `crust.py:608-627`), so the
  new edge cell is itself well under 40 km and spreads no further; the front moves on only when inland flow (40 km
  stop) refills the old edge cell. Every belt edge cell therefore keeps 40 km and the 0-5 km between normal crust
  (`isostasy.CONT_KM` = 35 km, `isostasy.py:37`) and 40 km is never given to the sea.

### 8.2 Why 35 km is defensible

Rey, Vanderhaeghe & Teyssier 2001 (Tectonophysics 342:435-449, doi:10.1016/S0040-1951(01)00174-3; abstract read
this lane on the repository.geologyscience.ru record 123456789/26833): collapse is the relaxation of a lateral
contrast in gravitational potential energy once the forces that held it up weaken; in the divergent regime "an
excess in gravitational potential energy drives crustal material away from the deformed lithosphere", and with a
fixed boundary the orogen "grows laterally at the expense of its surroundings". The excess is measured against the
undeformed lithosphere, so collapse runs until the thickened crust is back to the region's normal thickness, not to
a fixed 40 km. In the model, normal continental crust is `CONT_KM` = 35 km (the thickness the volume thermostat
aims at, `crust.py:54-79`, and that stands at 250 m, `isostasy.py:261`), so 35 km is the model's own
"undeformed" reference, not a new number.

What is not sourced: (a) the rate (the same kernel and `collapse_margin` x (1 + collapse) as lane 292's arm);
(b) that the 40 km inland stop is kept, so inland belts still stand at ~40 km (the inland stop is the kernel's
"thick crust is weak" threshold, PW-1497, and is not this lane's to move); (c) with the margin stop at 35 km, any
dead coast cell of 35-40 km of the same plate (not only an orogen's) creeps seaward. `dead` is true for a cell
never folded (`record.T_FOLD` = NEVER, `record.py:73`), so this widens the mechanism from belts to every thick
passive coast. That is the soft point: a 37 km craton coast is not an orogen with excess potential energy, it is
only 2 km thicker than the model's normal; on Earth such margins are held by lithospheric strength. Its size is
small either way (8.3).

### 8.3 Expected give-back

Measured on lane 292's seed 1 arm (4635ef, `collapse_margin=1`, 600-1000 Myr checkpoints; script
/data/personal/scratch/lane296/estimate.py, not kept): of ~4,600-5,900 coast cells on margin edges (same plate,
no trench), the median is 23 km thick (rifted margins), only 3-6% are over 40 km and 7-11% over 35 km. The crust
standing above the stop in those cells is 1.9-4.3x (median ~2.1x) larger with a 35 km stop than with 40.

So the expected give-back is about twice lane 292's: `collapse.margin` ~1.5-2.0e4 km x L5 cells by 1 Gyr
(lane 292: 9.2e3) against `andean.closed` ~-5.5e4, i.e. from ~1/4-1/3 of the closed area to ~1/2-2/3 (margin cells
are laid at 20 km, closed cells held ~35-40 km). The area books (2.3) need roughly +0.5-0.6 points of area per
100 Myr more for the thermostat to leave its floor on seed 2 (area 38.2% against 40% with lane 292's arm) and more
on seed 1 (38.5%). Expectation: seed 2 may leave the floor for part of the window; seed 1 probably not. Land above
3 km should fall a little (thinner coasts), not to the off-arm level unless the thermostat lifts.

### 8.4 The change

`collapse_margin_km` (params, default 40.0 = today, off): `flow_and_orogeny` passes a per-edge stop to
`crust_flow` (`ref`, new argument), `FLOW_KM` = 40 on inland edges (`crust.py:362`) and `collapse_margin_km` on the
margin edges. Only acts with `collapse_margin` > 0 (also default off). Test:
`tests/test_crust_belts.py::test_seaward_collapse_runs_down_to_collapse_margin_km`.

## 9. Screen (L7 seeds 1 and 2, 1 Gyr, medians over 600-1000 Myr)

All `planet simulate --seed S --level 7 --myr 1000 --checkpoint-every 20 --threads 4 --set collapse_margin=1
collapse_margin_km=K` on commit 46a94092 (this lane's parameter; main f692572b otherwise), both arms on the same
commit, scratch /data/personal/scratch/lane296/data, measured with `l7_high_ground.py`. **Baseline: the off arm is
`collapse_margin=1, collapse_margin_km=40`** (lane 292's arm, rerun here); it reproduces lane 292's 4635ef / d4f6be
to the digit (> 3 km 4.96 / 3.45, books `collapse.margin` 9.25e3 / 9.21e3), so the run code is unchanged since
bb30e268. Main's on arms (no collapse_margin, lane 288's 213321 / 2e1bc2 on 5411930b) and the no-Andes arms
(28d710 / 6286ce) are quoted for scale from section 2, not rerun.

| seed | arm (run) | > 3 km | > 4 km | area thermostat median (mean) | cont. area % | mean cont. crust km | Andes share of > 3 km | shelf % of ocean | submerged median m | land % |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | main on, no collapse_margin (213321, 5411930b) | 5.62 | 3.42 | 0.20 | 37.6 | 37.7 | 24.7 | 1.03 | -1140 | 32.8 |
| 1 | off: margin stop 40 km (783fb3) | 4.96 | 1.74 | 0.20 (0.20) | 38.5 | 37.8 | 23.5 | 1.00 | -982 | 33.8 |
| 1 | **A: margin stop 35 km (ed0b66)** | **3.92** | 1.33 | **0.20 (0.205)** | 39.3 | 37.2 | 18.6 | 1.47 | -937 | 33.9 |
| 1 | no Andes (28d710, 5411930b) | 3.90 | 1.11 | 0.33 | 40.5 | 35.2 | 8.9 | 1.34 | -878 | - |
| 2 | main on, no collapse_margin (2e1bc2, 5411930b) | 4.33 | 1.29 | 0.20 | 39.7 | 36.7 | 19.2 | 1.28 | -1050 | 34.0 |
| 2 | off: margin stop 40 km (5967e0) | 3.45 | 1.45 | 0.20 (0.20) | 38.2 | 37.4 | 20.4 | 0.81 | -1000 | 34.4 |
| 2 | **A: margin stop 35 km (285ffc)** | **3.30** | 1.35 | **0.209 (0.216)** | 40.2 | 36.0 | 27.0 | 1.25 | -978 | 34.3 |
| 2 | no Andes (6286ce, 5411930b) | 2.77 | 0.82 | 0.37 | 41.0 | 35.5 | 12.3 | 1.70 | -1030 | - |

Earth on the L7 grid (ETOPO1): > 3 km 2.5%, > 4 km 1.6%.

Books at 1 Gyr (km x L5 cells): `collapse.margin` +1.37e4 / +1.38e4 with A against +9.25e3 / +9.21e3 off (x1.48 /
x1.50); `andean.closed` -5.86e4 / -5.76e4 (off -5.44e4 / -5.82e4). In area (margin cells laid at 20 km, closed
cells ~37 km): A gives back ~0.43 of the area Andean closing takes, against ~0.30 off.

Thermostat through the window (subduction erosion x, 20-Myr checkpoints): seed 1 at 0.20-0.21 to 900 Myr, then
0.21-0.23; seed 2 0.20-0.21 to 740 Myr, 0.22-0.25 over 760-880 Myr, back to 0.20 from 900 Myr. Off arms: 0.20 at
every checkpoint.

- **Fails the bar.** The area thermostat does not leave its floor on either seed: medians 0.20 and 0.21, brief lifts
  to 0.23-0.25 only. The give-back rose x1.5, below the x2 expected in 8.3 (supply to the edge is still inland flow
  with its 40 km stop).
- What it did do: area closer to target (39.3 / 40.2% against 38.5 / 38.2%) and continents thinner (37.2 / 36.0 km
  against 37.8 / 37.4). On seed 2 the area reaches its target, but the thermostat stays at the floor: the floor is
  its integral term at its clip (`sim.thermo` at -`THERMO_MAX`, exp(4 x -0.4) = 0.20, `crust.py:37-38, 75-79`),
  wound there by the long deficit, and an area 0.2 points over target unwinds it by only ~1e-4 per Myr. So area on
  target with erosion still at x0.2 says the balance needs the floor rate: the slack is not restored.
- Land above 3 km falls on both seeds (4.96 -> 3.92, 3.45 -> 3.30; Earth 2.5%), seed 1 to its no-Andes level. But
  seed 1's fall comes with the Andes share falling (23.5 -> 18.6%) while seed 2's rises (20.4 -> 27.0%), and the
  > 3 km series moves by 3-6 points within 100 Myr in every arm (e.g. 860-1000 Myr); two seeds cannot tell a high-ground gain
  from run history (as in 6.1-6.3).
- Shelves: a little larger on both seeds (1.00 -> 1.47, 0.81 -> 1.25% of the ocean), submerged median a little
  shallower (-982 -> -937, -1000 -> -978 m): A widens margins at 20-35 km, the right direction for PW-950 but small.

## 10. Verdict (lane 296) and option C

- **Option A does not get the thermostat off its floor** (x0.20 / x0.21 medians on L7 seeds 1 and 2). By the
  brief's rule this lane stops: no third mechanism, no judge, no default change. `collapse_margin_km` stays 40
  (off), `collapse_margin` stays 0.
- **Option C, accept the floor, means:** with `andean_shortening` on (default 0.1) the L7 area thermostat runs at
  its x0.2 floor for most of a run on some planets (2 of 2 L7 seeds, 1 of 3 L6), area ends 0-2.5 points under its
  40% target, continents stand ~1.2-2.5 km thicker and ~200-250 m higher than without the Andes, and L7 land above
  3 km sits at about 4-5.6% (main: 4.33 / 5.62% on seeds 2 / 1) against Earth's 2.5% on the same grid; above 4 km
  1.3-3.4% (Earth 1.6%). That is ~1.7-2.2x Earth above 3 km on the worst seeds, a plausible high planet on seed 2
  and a floor-pinned one on seed 1. The thermostat then has no slack for any further area sink, so any new
  mechanism that takes continental area will show as thicker continents straight away.
- Options for the decision (draft `draft-accept-l7-area-thermostat-floor.md`): C1 accept; C2 `andean_shortening`
  off at L7 only; C3 Andean belts wider instead of taller (lane 292's B). Lean C1 (reasons in the draft).
