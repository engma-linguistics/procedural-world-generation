# PW-950 diagnosis: why the continental margin is a one-cell cliff (lane 100)

Written before any sweep (diagnosis gate). Code read at `cb366840` (main merged into the lane branch).

## In plain words

When a continent splits in the model, the two halves move apart as rigid plates straight away, and the gap between
them fills with ordinary ocean floor within a step or two. The crust at the edge only gets stretched while the split
line itself still runs through continental crust, which is a few Myr. So the edge is hardly thinned (beta about 1.04),
and the crust jumps from ~26-33 km of continent to 7-9 km of ocean floor in one cell. Isostasy then turns that jump
into a ~4 km drop in one cell. On Earth, rifting stretches the edge for 20-40 Myr before the ocean opens, and the crust
thins from ~30 km to under 10 km across a 50-60 km necking zone, plus a hyper-extended strip beyond it. That thinned
strip is the continental slope. The fix to try first: when a rift opens next to continent, fill the new gap with
continental crust thinned out of the edge (crust is conserved), until the edge is thin enough to break up.

## Where the margin's crust and depth are set

1. **Rift stretching** (`planet/tectonics/crust.py: rift_stretching`). The thinning rate is `stretching x opening rate`
   (0.01 /Myr per cm/yr) at the two cells of each *opening* plate-boundary edge, spread over a Gaussian belt one
   level-5 cell wide (`spread(..., 1.0)`, ~240 km), but only while the boundary cell is continental and thicker than
   23 km (`fresh = w_cont & w_thick > 23`).
2. **The stretch floor** (`crust.stretch`): stretched crust thins `t * exp(-rate dt)`, never below 22 km. The lost
   crust goes into the plate's `rift_pool`, and strain is logged in the record (`record.rift`, `RIFT_STRAIN`).
3. **Margin rings** (`crust.rifted_margin`): new ocean floor of this step (`newc`) next to the plate's own
   continental crust is turned into continental crust, one ring at a time, at `rift_margin_km` (18 km), or thinner
   down to `MARGIN_MIN_KM` (12 km) when the pool runs short. Below 12 km, nothing is laid and the cell stays ocean floor.
   Pool that no ring takes decays back into the plate's rifted cells over 100 Myr (`flanks`).
4. **Isostasy** (`isostasy.elevation`): continental crust stands at `250 + 150 (t - 35)` m (air-loaded Airy;
   22 km -> -1700 m, 12 km -> -3200 m), ocean crust at `ocean_depth(age) + 200 (t - 7)` (-2600 m at age 0, -4200 m at
   ~21 Myr). Plus light-sediment lift and `isostasy.subsidence` (thermal sag from `RIFT_STRAIN`: McKenzie 1978, and
   flexural moats). Lane 23 showed water-loading deepens a drowned margin rather than lifting it (McKenzie 1978 agrees:
   E0 water-loaded 3.2 km vs 2.2 km air-loaded, Table 1 p. 27); not retried.
5. **Offshore sediment** (`surface._offshore`): shelf cells fill to `SHELF_TOP`, the brink cell fills toward shelf
   level (clinoform, PW-818), and the rest passes downslope, a share `1 - exp(-d/fan_km)` (fan_km 1000 km) settling per
   deep cell passed, so overflow is spread thinly over ~1000 km of abyssal floor. Nothing piles at the slope foot.

## Why the transition is one cell

- **Breakup is instant.** The rift is drawn as a plate boundary and the two halves move apart rigidly from the first
  step (`events.py` rifting, plate kinematics). At 3-5 cm/yr the gap is 60-100 km per 2 Myr step: one L6 cell every
  ~2 steps, one L8 cell every step. From then on the *opening* boundary runs between the two plates' new floor cells,
  which are oceanic, so `fresh` is false and stretching stops. The edge was stretched for only the step or two before
  the gap appeared: strain ~ 0.03 /Myr x 2-4 Myr ~ 0.06-0.12, i.e. beta ~ 1.04-1.1 (lane 96 measured a median edge
  strain of 0.04 at L8; the lane's 150 Myr L6 seed-1 check: 0.07).
- **The pool is too small to lay a ring.** Crust lost by that brief stretching (~0.06 x 35 km x a belt a few cells
  wide) is a fraction of one 18 km ring per cell of margin, so most new-floor cells next to the continent get nothing
  (ring thinner than 12 km is skipped) and become ocean floor, and the continent never touches new floor again.
- **Result:** the last continental cell keeps 24-26 km (beta ~1.1-1.3 from the stretch belt and the 22 km floor) and
  the next one is 7-9 km of young ocean floor: a 15-18 km crust step, which isostasy turns into a 3.5-4 km drop in one
  cell (lane 96, L8: 25.9 km / -441 m -> 9.0 km / -4199 m; L6 seed 1 at 100 Myr in this lane: 23.9 km / -695 m ->
  8.5 km / -4628 m).
- Nothing downstream can fix it. Thermal sag acts on the stretched crust, and there is barely any; sediment that passes
  the brink is spread over ~1000 km of abyss.

The isostasy itself is sound: on Earth too, a ~10 km crust at the foot of a margin sits 3-4 km down. What is missing is
the *thinned crust*, i.e. the kinematics of the rift phase.

## Candidate mechanisms

### C1. Necking: pay for the gap with thinned continental crust (main candidate)

**Source.** Mohn, Manatschal, Beltrando, Masini & Kusznir 2012, "Necking of continental crust in magma-poor rifted
margins: Evidence from the fossil Alpine Tethys margins", Tectonics 31, TC1012 (read this session; PDF from the
University of Turin repository, kept in the lane scratch, not committed). Abstract (p. 1): "the transition from weakly
thinned continental crust (30 km) in proximal margins to hyper-extended crust (<=10 km) in distal margins occurs within
a narrow zone, referred to as the necking zone". Section 2.1 [5] (p. 2): "This thinning occurs over a relatively narrow
area, which may be 50-60 km wide"; proximal margins have beta "typically less than 2" ([4]), "within the necking zone,
beta-factors are typically >2" ([5], p. 3). Distal margins are hyper-extended crust, then an ocean-continent transition,
then ocean crust ([3]-[4], Fig. 1). Rifting there ran from ~205-180 Ma (Eita shear zone, abstract) to mid-ocean-ridge
magmatism "during the Bathonian to Oxfordian" ([6], p. 3): tens of Myr of stretching before ocean floor. Mohn et al.
also note "the mass of the crust needs to be conserved during rifting" ([54], p. 23). McKenzie 1978
(on file; p. 27) also assumes "continental crust is assumed to be conserved" in his stretching model.

**Mechanism.** When a rift's new floor appears next to a plate's own continental crust (`rifted_margin`'s ring step),
lay it as continental crust whose thickness continues the edge's, and take that crust out of the plate's continental
cells within a necking zone `L` km of the edge, thinning each by `exp(-eps * w)`, `w = 1 - d/L` (the edge most, nothing
beyond `L`). `eps` is solved so the crust removed (plus any rift pool) equals the crust laid: volume is conserved.
The ring's thickness is the edge's after thinning. Each new ring becomes the next edge, so the profile thins seaward
ring by ring; when the next ring would be thinner than `MARGIN_MIN_KM` (hyper-extended crust, <= ~10-12 km), the rift
breaks up and further floor is ocean. The strain is logged in the record so the McKenzie sag acts on it.
For small steps the thinning per km of new margin is ~2/L, independent of the grid (continuum limit), so the margin's
width in km is roughly level-independent; L6's 110 km cells will resolve it coarsely.
**Expected effect.** Edge crust 35 -> ~12 km over ~100-200 km in total (inner zone + new rings) instead of one cell.
At 150 m/km that is a slope from ~0 to ~-3200 m spread over 2-4 L7 cells and 4-8 L8 cells; the 200-3000 m band should
grow, coast-to-3000 m distance lengthen, `near1`/`near2` drop. Risk: more continental area (thermostats answer it:
subduction erosion steers area), thinner mean continental crust, lower land; watch land %, sea level and the hard bars.

### C2. A continental rise: sediment that passes the brink settles at the slope foot

**Source.** Mosher, Campbell, Gardner, Piper, Chaytor & Rebesco 2017, "The role of deep-water sedimentary processes in
shaping a continental margin: The Northwest Atlantic", Marine Geology 393: 245-259 (read this session; Zenodo record
1247930). p. 245-246: margin morphology is "the result of isostatic elevation differences between oceanic crust and
adjacent continental crust", but "further modified and even transformed by sedimentary processes"; the rise is "low
gradient, evenly-spaced, slope-parallel contours extending seawards from the foot of the continental slope generally
confined to areas of sediment thickness > 300 m" (quoting Harris et al. 2014 / IHO 2008); graded slopes "have a smooth
exponential decay shape, where the gradient is steepest near the shelf edge and gradually diminishes seaward" (p. 247);
upper-slope gradients exceed 3 degrees between 200 and 2000 m (p. 248).
**Mechanism.** In `_offshore`, deposit the brink overflow where the sea floor flattens (the slope foot) before
spreading the rest as fans: e.g. a deep cell whose own downhill drop is smaller than the drop into it keeps a share
`1 - drop_out/drop_in` of what arrives. **Expected effect:** a sediment apron at the slope foot, smoothing the profile
and raising the 3000-4000 m band toward 200-3000 m. Smaller than C1, and only useful once a slope exists. Second.

### C3. (Considered, not first) wave-base planation at lowstands

A shelf is cut to wave base (~-50..-120 m) at sea-level lowstands, which would flatten the inner margin. No paper on
file or read this session, and it cannot make a 200-3000 m slope (it planes the top only), so it is not tried here.

## Screen plan

L6, seeds 1-3, 1 Gyr, in memory through `docs/review/tectonics/margin/margindiag.py` (tools/ice_diag.py plus margin
numbers every 50 Myr): shelf %, 200-3000 m %, 4000-5000 m %, submerged-continent median, coast-to-3000 m (km), coast
cells with >3000 m within 1 / 2 hops, the signed profile across the continent-ocean crust boundary, edge rift strain,
continental and land %, mean crust; plus the hard bars from the run's own series (docs/review/v1-cut/tally.py). Arms:
baseline, C1 (L = 200 km, MARGIN_MIN_KM unchanged), C1 + C2. One L7 seed if C1 helps at L6, since L6 cells are about
the width of the whole necking zone.
