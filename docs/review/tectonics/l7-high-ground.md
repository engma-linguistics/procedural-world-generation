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
