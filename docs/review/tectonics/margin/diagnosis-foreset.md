# PW-950 round 3 diagnosis: the shelf's sediment front (lane 100)

Written before any run (diagnosis gate). Code at `b52ba525` (v0.1.0 main merged into the lane branch).

## In plain words

The wall comes from one line: the first deep cell beyond the shelf is filled right up to shelf level before anything
moves on, so the shelf grows a whole cell at a time with a vertical front. But at L6 (120 km cells) and L7 (60 km),
a real shelf front at its natural steepness (about 3 degrees, so ~4 km of drop over ~80 km) is itself narrower than a
cell or about one. So the one-cell front is roughly right at those levels. Giving it a slope only changes L8. What keeps
the L6 and L7 middle depths short of Earth's is elsewhere: shelves that are too narrow, and too little sediment piled on
the lower slope and rise. The mechanism to pick is the one the margin literature uses for both: sediment on the sea
floor creeping downslope in proportion to the slope (a diffusion of the sea-floor relief), which turns a stepped front
into a graded one and carries sediment down onto the rise.

## Where the wall comes from

`planet/surface.py: _offshore`, the brink branch (PW-818). Cells are visited shallowest first. A deep cell
(`elev <= SHELF_EDGE`, -400 m) next to land or shelf is a brink, keeps share 1.0 of what reaches it, up to
`(SHELF_TOP - elev) / iso`, i.e. it fills to -60 m. Only the overflow moves to its deepest neighbour. When the brink is
full it becomes shelf and its deepest neighbour becomes the new brink. The result is a flat wedge at -60 m and a front
one cell wide, whatever the crust under it. That is why round 1's necking (thinner edge crust) just moved the step out
to the new edge: the thinned cells were filled with ~8 km of sediment (rifted-margin edge ~21 km of crust and sediment
at about -900 m, then -3500..-3800 m in the first oceanic cell). After `_offshore`, `_spread` diffuses the *deposit*
(not the relief) along the shelf and over the deep floor, but never across the shelf edge (`shelf[ea] & shelf[eb]`,
`deep[ea] & deep[eb]`), so nothing grades the front.

## What the front should look like at each level

Mosher et al. 2017 (Marine Geology 393: 245-259, read in round 2 and again now): upper-slope gradients "exceed 3
degrees, between 200 and 2000 m water depths, for most of the margin length" (p. 248); out-of-grade slopes ~10 degrees
(p. 249). Graded slopes have "a smooth exponential decay shape, where the gradient is steepest near the shelf edge and
gradually diminishes seaward" (p. 247). The rise extends seaward from the foot of the slope where the sediment is more
than 300 m thick (p. 246). A 3 degree foreset (52 m/km) drops 4 km in ~77 km, so the steep part is about one L6 cell
wide (120 km), about one L7 cell (60 km), and 3 L8 cells (28 km). A one-cell front is the right cell-average shape at
L6 and L7, and too sharp only at L8. Earth resampled to L6 has 19.6% of its ocean at 200-3000 m (round 2's
earth_margin.py) because its shelves are wider (6.2% of the ocean against ~3% in the runs) and its rise and lower slope
carry kilometres of sediment, not because a foreset spans several cells.

## Candidate mechanisms

1. **Slope-stability ceiling (angle of repose).** A deposit may not stand more than `S_c * d` above its deepest
   neighbour. The overflow moves on, so the front aggrades from its toe and progrades at slope `S_c` (Mosher p. 248:
   ~3 degrees). Physical (failure beyond a critical slope), one parameter from the source. Expected effect: nil at L6
   (`S_c d` = 6 km is more than the relief) and small at L7 (3 km), so it would not move the paired L6 judge. It helps
   L8 only.
2. **Marine slope diffusion of the sediment relief (picked).** The standard progradation model (Mitchell & Huthnance
   2008, "Oceanographic currents and the convexity of the uppermost continental slope", author's manuscript
   (journal not stated in it), NERC Open Research Archive eprint 2772, read now; manuscript pp. 5-6). Topography H evolves by `dH/dt = K laplacian(H)`
   (eq. 1): flux down the gradient, `Q = -K rho_s dH/dy` (eq. 2), with mass conserved (eq. 3). It is used for basin fill
   and clinoforms (Driscoll & Karner 1999, Flemings & Grotzinger 1997, Granjeon & Joseph 1999 and others, as they cite).
   They show US and Iberian Atlantic slope morphology is compatible with it, with mobility K declining with depth, which
   gives the rounded shelf-edge rollover (abstract). Implement it as a per-step diffusion of the sea-floor relief over
   all sea cells, moving only sediment cover (no cell gives more than its cover), with K falling with depth. It grades a
   stepped front into the cell-average profile, feeds sediment onto the lower slope and rise, and widens the shelf's
   effective edge. It doesn't depend on resolution in km^2/Myr. **Open:** a K value from a source actually read. A web
   summary points to Simon et al. 2022 (Basin Research, clinoform transport coefficients ~0.1 km^2/kyr), but its HAL
   copy is behind a bot wall and I have not read it, so it is not cited. Step 1 of the work is to get a readable source
   for K (and its depth decay), then screen. Expected effect: at K ~100 km^2/Myr the diffusion length per 2 Myr step is
   ~14 km and ~100 km per 50 Myr, so it reaches across one L6 cell over tens of Myr. It should raise the 200-3000 m
   share and cut the next-cell cliff share at every level. The risk is that it also smooths trenches and seamount
   flanks, so mask to cells with sediment cover, and no cell goes below its basement.
3. **Sub-cell front position.** Keep the fill-to-shelf rule but carry the front's position inside the brink cell and
   set the cell-mean depth from a 3 degree foreset at that position. Exact for the geometry, but bookkeeping-heavy and
   it does nothing for the rise. Kept as a fallback.

Pick: 2, because it is the physical progradation mechanism (not a clamp), works at L6 where the judge runs, and covers
the rise too. Add 1 later only if L8 fronts stay too steep.

## Screen plan

Worst draws first. Round 2's cliff share is highest on L6 seeds 1 and 3 (23% next-cell; 15% with necking). Run 2-3
targeted L6 runs with `margindiag.py`: main, necking + rise (round 2), and necking + rise + diffusion as the kitchen
sink. Then the full 18x2 paired judge once, at the end. Report the shelf, 200-3000 m and next-cell cliff shares against
round 2 and main.

## Addendum (round 3, lane 100c): K and its depth law, before any screen

Sources read this session (PDFs kept in the lane scratch, not committed):

- **Mitchell & Huthnance 2008** (NERC eprint 2772, author's manuscript). The depth law: in their 2-D run "the mobility
  was decreased inversely with depth d: K = K0(d/d0)^-1" (manuscript p. 24, lines 5-6), "nearly equivalent" to their
  measured current-speed trend (Fig. 5A, beta = 0.36) with K ~ u^3 (p. 24, line 7); K scales as roughly u^2 to u^3
  (p. 10, lines 6-7). They give **no absolute K** (the depth changes are "omitted ... to highlight the pattern",
  p. 24) and censor results below 400 m, where "the model is not relevant to the muddy slope sediments" (p. 24).
- **Strata tutorial** (Flemings group, UT Austin, `jsg.utexas.edu/flemings/files/Strata_tutorial.pdf`, PDF p. 4),
  for the Jordan & Flemings (1991) clinoform model: "Jordan and Flemings (1991) found reasonable values for Kmarine to
  be on the order of 100-1000 m2/yr", non-marine 1e4-1e5 m2/yr; lowering Kmarine steepens the clinoforms. I read the
  tutorial, not Jordan & Flemings 1991 itself.
- **Simon, Robin, Rouby, Guillocheau, Yuan & Braun, EGU2018-6425** and **Simon et al., EGU2019-7016** (abstracts of the
  Simon et al. 2022 Basin Research study, whose full text I still could not reach): diffusion coefficients measured
  from seismic stratigraphy and wells in the Ogooue and Zambezi deltas "range over two orders of magnitude (x0,01 to 10
  km2/ka)" (2019; 0.01-1 km2/ka in 2018), "strongly depend on the slopes along the depositional profiles", and the
  diffusion approach is "optimal at a scale of several kilometers and million years" (2019).
- **Kaufman, Grotzinger & McCormick 1991** (Kansas Geol. Survey Bull. 233, pp. 489-508, eq. 3, p. 491):
  `D = C0 exp(-C1 W)` with C1 = 0.05 /m (Table 1, p. 492). That decay (e-folding 20 m) is for wave-swept shelves 0-150 m
  deep, not a slope; noted, not used.

**K.** 100-1000 m2/yr is 100-1000 km2/Myr; the Ogooue/Zambezi measurements, 10-10^4 km2/Myr, bracket it. The default is
**K0 = 300 km2/Myr** (the log-middle of Jordan & Flemings' range) at the reference depth, screened within 100-1000.
That is a sourced order of magnitude, with the value inside it a judgement (needs-decision draft
`draft-marine-diffusivity-k-and-depth-law`).

**Depth law.** `K(d) = K0 d_ref / (d + d_ref)`, d the water depth, d_ref = 200 m: Mitchell & Huthnance's K ~ 1/d at
depth, finite at the shore, K0/2 at the shelf edge (200 m) and K0/16 at 3000 m. Using 1/d below 400 m extrapolates past
the range they fit. This is a judgement, kept because the slope must stay less mobile than the shelf, or the
rollover inverts (Kaufman p. 491, the same logic). K is taken at the upslope (donor) cell's depth, where the moving
sediment lies.

**Why it should help, in numbers.** At L6 (cell ~120 km), the timescale to grade one cell is d^2/K ~ 50 Myr at K0, and
~10x longer at slope depths. So over 1 Gyr it reaches the lower slope and rise many times. Expected effect: the front
cell keeps its fill-to-shelf rule, but the cell beyond it gains sediment fed down the gradient, so 3000-4000 m cells
next to the shelf aggrade into the 200-3000 m band.

**Conservation.** Equal-area cells (`geo.cell_area_km2`), so the km of cover that leave one cell are the km that
arrive in the other. Only sea-to-sea edges carry flux. A donor gives at most its light sediment cover (cover minus
lava flows), its carbonate, sand, salt, coal and tuff pro rata. It arrives as mud (shale), and `sediments()` gives
it its sand share by depth, as for any sea deposit. Bare rock gives nothing.
