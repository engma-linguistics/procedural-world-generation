# Lane 275 (PW-1497 pass 4, owner's go-ahead): do dead belts come down? Diagnosis, then post-orogenic collapse

Lane 275, 2026-11-10. Base: main a784b8ea. Follows `scout6.md` (pass 1), `scout7.md` (pass 2: overriding-plate
contraction, `scout7_andean.patch`) and `scout8.md` (pass 3: the long-term rate). Daniel asked for PW-1497 to be
prioritised again; this is one diagnosis-led attempt, not a loop.

## In plain words

- **Why the last three tries failed:** in the model a mountain belt never comes down once it stops being squeezed.
  Its extra-thick crust lasts ~260-390 Myr (e-folding), on main as with the Andes patch. On Earth a thick plateau
  whose squeezing has stopped spreads and thins by extension within about 10-50 Myr (the old Variscan plateau of
  Europe, the plateau where Nevada's Basin and Range is now). About 60% of main's land above 3 km was last squeezed
  more than 10 Myr ago, and 13-23% more than 100 Myr ago.
- **The fix (built, off by default):** post-orogenic collapse. Crust that has not been squeezed for 20 Myr spreads 31x
  faster (the model's existing lower-crustal flow, so no crust is created or destroyed). It acts on collision plateaus
  and Andean belts alike. With it, dead high ground is gone 30-60 Myr after its last squeeze.
- **Screen** (3 test planets, L6, 600 Myr, against today's main on the same planets): the Andes patch at a share of
  0.1 with collapse puts **21.5%** of high ground on ocean-continent coasts (main 10.2%, Earth ~25%) and land above
  3 km is **2.26%** (main 2.76%, Earth 2.6%). It passes three of the four bars outright; continental crust is 37.9%
  on one planet against a 38% line (main is 37.8% on that planet). Share 0.2 with collapse makes too much high ground.
- **Not yet done** (hand-off): the forked screen (running), the scorecard and the hard-failure judge. Merge-ready only
  if those hold and the coordinator reads the continental line over the three seeds.

## 1. Diagnosis (written before any screen)

### 1.1 How the model takes thickened crust down once shortening stops

Thickness sets height: Airy isostasy, 150 m of elevation per km of continental crust over 35 km (`isostasy.py`),
so land above 3 km is crust thicker than about 53 km. Three things remove that excess; nothing else does.

- **Erosion with rebound** (`surface.erode`, called from `earth.erode`). Each step lowers the *surface*: hillslope
  creep, river incision (stream power), and a weathering term that takes the height above a 200 m base level
  down with an e-folding time `erosion_timescale` / (1 + (h / `erosion_height`)^2) = 400 Myr / (1 + (h/2 km)^2),
  times a rain and plant factor. The rock removed is that surface drop divided by 150 m/km, so the isostatic
  rebound is built in (a km of surface lowering costs ~6.7 km of crust). At 3 km the weathering term alone is an
  e-folding of ~130 Myr, at 5 km ~60 Myr (before the rain factor and the river and slope terms).
- **Lower-crustal flow** (`crust.flow_and_orogeny`, kernel `plate_kernels.crust_flow`): crust thicker than 40 km
  spreads to its neighbours on the same continent, at a rate `crust_flow` x (x + x^3), x = (thickness - 40 km)/10 km.
  It is a diffusion that keeps volume, so a wide belt spreads slowly (time ~ width^2). It acts the same whether
  the belt is still being squeezed or not.
- **The height cap** (PW-1446, `max_km`): clips columns above ~6.6 km. Only the top few cells.

There is no collapse: nothing in the model knows whether a belt is still being squeezed, so a dead belt is held up
exactly as long as a live one. Nothing removes a root either (there is no lithospheric mantle in the model; the
crust's thickness is the whole root).

### 1.2 Measured: how long belts last once squeezing stops

`scout9_decay.py` reads every checkpoint (every 20 Myr, t >= 100 Myr) of L6 runs of seeds 1, 2, 6001 x 600 Myr.
"Last squeezed" is the strata record's fold date (`record.T_FOLD`), which `flow_and_orogeny` sets wherever crust is
stacked at > 0.05 km/Myr (collisions, and with the patch Andean contraction); it rides with the plate. Two measures:
- the land above 3 km split by the time since it was last squeezed, and the share of each part within 2 L6 cells of a
  live ocean-continent margin (`scout6_measure`'s zone);
- the decay of a dead belt's excess crust: plate-frame cells (they move with their plate) that are continental, have
  crust > 45 km, were last squeezed >= 20 Myr ago and are not squeezed in the next 20 Myr; the e-folding time of
  their pooled excess over 35 km between the two checkpoints.

**Baseline: main a784b8ea, re-run here** (planet/tectonics changed since scout 240: PW-1628, PW-1637, lanes 263,
273). Share 0.4: `scout7_andean.patch` (applies cleanly to a784b8ea), same seeds.

| run | seed | land >3 km (% land, all ckpts) | of it, by Myr since last squeezed: 0-10 / 10-30 / 30-60 / 60-100 / >100 / never | near a live margin, of each (%) | dead-belt cells | excess km at t, t+20 | e-folding of the excess |
|---|---|---|---|---|---|---|---|
| main | 1 | 5.48 | 37.9 / 14.9 / 18.3 / 15.0 / 12.9 / 0.9 | 19.6 / 0.1 / 1.0 / 0.2 / 0.0 / 0.6 | 18885 | 17.0, 15.8 | **261 Myr** |
| main | 2 | 4.04 | 38.5 / 12.5 / 12.8 / 12.7 / 22.6 / 1.0 | 24.1 / 3.3 / 1.8 / 0.5 / 0.3 / 1.5 | 15567 | 17.5, 16.5 | **337 Myr** |
| main | 6001 | 2.00 | 39.6 / 15.8 / 16.0 / 14.2 / 13.9 / 0.5 | 23.6 / 5.0 / 2.6 / 1.3 / 0.6 / 0.0 | 16958 | 15.7, 14.7 | **305 Myr** |
| share 0.4 | 1 | 12.14 | 47.1 / 12.4 / 12.8 / 11.0 / 16.2 / 0.5 | 38.7 / 4.9 / 0.5 / 0.1 / 0.0 / 10.6 | 32620 | 18.1, 16.8 | **282 Myr** |
| share 0.4 | 2 | 10.60 | 49.0 / 14.3 / 12.2 / 9.5 / 14.5 / 0.5 | 41.3 / 6.6 / 1.1 / 0.4 / 0.1 / 7.9 | 25193 | 17.6, 16.7 | **394 Myr** |
| share 0.4 | 6001 | 10.98 | 49.9 / 13.5 / 12.5 / 9.8 / 13.6 / 0.6 | 36.4 / 6.1 / 1.0 / 1.5 / 0.0 / 6.7 | 29247 | 17.4, 16.4 | **329 Myr** |

(The "land >3 km" column pools the checkpoints; `scout7_measure`'s median over keyframes is in the screen table.)

What this says:
1. **A dead belt's excess crust lasts ~260-390 Myr (e-folding) in the model, on main as with the patch.** About
   60% of main's land above 3 km, and ~50% of share 0.4's, was last squeezed more than 10 Myr ago; 13-23% more than
   100 Myr ago. Almost none of that old high ground is near a live margin.
2. **Main's high ground has the same problem.** It is not an artefact of the Andean belts: collision plateaus
   outlive their collision by hundreds of Myr too. Any decay has to apply to both (as scout8.md section 4 said).
3. **But half the high ground is being squeezed now**, and at share 0.4 only ~40% of that active part lies near a
   live margin (the Andean belt is ~290 km e-folding wide, wider than the 2-cell zone, and collisions squeeze the
   rest). So even a perfect decay of dead belts would leave share 0.4 with ~5-6% of land above 3 km: it cannot
   rescue share 0.4. It can only help at the lower shares (0.1-0.2), where scout 240 found the excess was inland.

### 1.3 Earth's decay times (sources)

- **Erosion alone is slow.** Baldwin, Whipple & Tucker 2003 (JGR 108(B3), doi:10.1029/2001JB000550; abstract,
  umimpact.umt.edu, read in scout8.md and re-read in this pass's search): stream-power erosion takes a dead orogen's relief
  down in 1-10 Myr; Airy rebound makes this up to ~6x longer, transport-limited channels 2-3x, an erosion threshold
  ~20x, so erosion and isostasy alone can keep residual relief for hundreds of Myr. Braun & Robert 2005 (Earth Surf.
  Process. Landforms 30, 1203-1225, doi:10.1002/esp.1271; PDF read): in the Dabie Shan, relief fell by a factor of
  ~2.5 over 60-70 Myr after orogeny ended, the erosional response time "likely to be relatively large, i.e. τ > 100 Ma"
  (p. 1223); they define τ as the e-folding time of relief (eq. 23, p. 1214).
  So the model's erosion (~60-130 Myr e-folding at 3-5 km) is within Earth's range for erosion alone.
- **Thick plateaus come down by collapse, not erosion.** Dewey 1988 (Tectonics 7(6), "Extensional collapse of
  orogens"; via the EGU Tectonics division summary, read in scout8.md): collapse is the orogen's last stage, driven
  by its excess gravitational potential once it is no longer held up; erosion alone is too slow to remove the
  excess crust. Ménard & Molnar 1988 (Nature 334, 235-237, abstract on nature.com): the Variscan (Hercynian) belt of
  southern Europe was a Tibet- or Andes-like plateau of thick crust that collapsed into a "Basin and Range"
  province of normal faults and rifts in the late Palaeozoic. Today its Moho is flat at ~30 km (not sourced here).
  Wikipedia "Orogenic collapse" (fetched; secondary, cites Vanderhaeghe et al. 2020, Cassel et al. 2014): Variscan
  thinning c. 345-310 Ma, after the plateau formed; collapse "can begin either once the orogeny ends ... or during
  the orogeny"; the Nevadaplano (the Basin and Range's plateau) stood high from 40 to 23 Ma (Cassel et al. 2014)
  before it extended. The Aegean's thickened crust (orogeny c. 70-14 Ma) extended as its slab rolled back.
- So on Earth a thick plateau whose squeezing has stopped keeps its height for of order 10-50 Myr and then
  spreads and thins by extension; it does not stay 3+ km high for 100-400 Myr. Apart from ice caps,
  volcanic highlands and dynamic uplift, Earth's land above 3 km is in belts being shortened now (Tibet, Andes,
  Pamir-Tian Shan, Zagros, Alps, Caucasus). That last sentence is my observation, not sourced.

### 1.4 What to change, and what it can do

The diagnosis supports one mechanism: **post-orogenic collapse.** A belt that is no longer squeezed loses the
convergence that held its thick crust up and spreads. The model already has the spreading (lower-crustal flow,
volume kept); what it lacks is the switch. Smallest form: crust not squeezed for `collapse_delay` Myr flows
`1 + collapse` times faster (`crust.flow_and_orogeny`, a per-edge factor in `plate_kernels.crust_flow`; both ends of
the edge must be past the delay, so a live belt's edge is not drained by its dead neighbour). Volume is kept
(no new booking, the thermostats see nothing). It acts on collision plateaus and Andean belts alike. Off by
default (`collapse = 0`), so main is unchanged.

- `collapse_delay` = 20 Myr: on Earth collapse comes at the end of, or within tens of Myr after, the end of
  shortening (above); 20 Myr also outlasts the gaps between a slow Andean belt's closing events.
- `collapse`: set so that a dead belt's excess e-folds in tens of Myr (Earth: 10-50 Myr to collapse), measured
  with `scout9_decay.py`, not tuned on the pass-bar metrics.
- Not chosen: removing the root (delamination). On Earth, dropping a dense root *raises* the surface (the Puna);
  in the model removing crust lowers it, so it would be mislabelled physics, and it would destroy volume.

What it can and cannot do (from 1.2): it can lower the inland, dead high ground on main and at shares 0.1-0.2, which
raises the Andes share by removing the denominator. It cannot touch the actively squeezed half. Prediction: share 0.4
still fails the >3 km bar; shares 0.1-0.2 are the candidates.

## 2. Calibration (seed 1, L6, 300 Myr, share 0.4)

Set on how long dead high ground lasts (`scout9_decay.py`), not on the pass bar. Same run without collapse: the share
0.4 row of 1.2 (its first 300 Myr are not separately measured; the 600 Myr pooled numbers are the reference).

| collapse | land >3 km (% land, ckpts) | of it, by Myr since squeezed: 0-10 / 10-30 / 30-60 / 60-100 / >100 | excess-over-35 e-folding | Andes share (keyframes) | >3 km (keyframes) |
|---|---|---|---|---|---|
| 0 (600 Myr) | 12.14 | 47.1 / 12.4 / 12.8 / 11.0 / 16.2 | 282 Myr | 20.3 | 11.57 |
| 10 | 11.42 | 61.7 / 14.6 / 14.5 / 7.7 / 0.4 | 166 Myr | 21.5 | 10.02 |
| 30 | 7.85 | 69.4 / 16.8 / 12.4 / 0.8 / 0.0 | 136 Myr | 31.7 | 6.42 |
| 100 | 6.96 | 77.1 / 18.4 / 3.4 / 0.6 / 0.1 | 131 Myr | 30.7 | 5.90 |

- At `collapse = 30` dead high ground is gone 30-60 Myr after its last squeeze (0.8% of it older than 60 Myr,
  against 27% without): Earth's 10-50 Myr (section 1.3). 100 adds little. **Chosen: 30, delay 20 Myr.**
- The excess-over-35 e-folding only falls to ~130 Myr because flow stops at 40 km (`crust_flow`'s threshold): the
  last 5 km of excess is erosion's. That band is below 1.0 km of height, so it does not matter for land above 3 km.
- As predicted in 1.4: at share 0.4 the actively squeezed half stays, and land above 3 km is still 6-7%.

## 3. Screens (L6, seeds 1, 2, 6001, 600 Myr; `scout7_measure.py`, median of ~29 keyframes with t >= 100 Myr)

Pass bar, as written in scout8.md section 1 before any run, unchanged: Andes share mean >= 20%; land above 3 km no
seed above 3.5% and mean <= 3.0%; land % within 2 points of main on each seed; continental crust median >= 38%.
**Baseline: main a784b8ea re-run here** (planet/tectonics changed since scout 240, so scout7.md's main row is stale).
Collapse arms: `collapse = 30`, `collapse_delay = 20` (section 2). Runs in the scratchpad, deleted after measuring.

| arm | Andes share of >3 km land (mean) | land >2 km | >3 km (mean) | >4 km | land % (vs main) | continental % median / end | top m |
|---|---|---|---|---|---|---|---|
| main | 7.4, 10.6, 12.6 (**10.2**) | 9.53, 8.51, 6.39 | 4.00, 2.76, 1.51 (**2.76**) | 1.22, 1.02, 0.47 | 32.2, 33.0, 33.8 | 37.8 / 41.1, 39.0 / 40.4, 39.1 / 40.3 | 5865, 6468, 5495 |
| share 0.4, no collapse | 20.3, 21.0, 19.8 (20.4) | 22.6, 20.1, 21.0 | 11.57, 10.48, 10.53 (10.86) | 5.18, 4.70, 4.72 | 30.3, 30.7, 31.4 | 34.6 / 36.2, 35.2 / 34.8, 35.2 / 34.6 | 6744, 6684, 6690 |
| **share 0.1 + collapse** | 16.9, 24.4, 23.3 (**21.5**) | 8.96, 6.51, 6.42 | 3.29, 1.85, 1.65 (**2.26**) | 1.06, 0.66, 0.32 | 32.8, 33.4, 32.4 (+0.6, +0.4, -1.4) | **37.9** / 38.2, 38.5 / 40.7, 38.9 / 40.8 | 6320, 5930, 5399 |
| share 0.2 + collapse | 36.3, 24.5, 27.3 (29.4) | 8.82, 12.81, 10.38 | 2.81, **4.51**, 3.46 (**3.59**) | 1.02, 2.02, 1.27 | 32.4, 32.1, 32.0 (+0.2, -0.9, -1.8) | 37.7 / 38.4, 36.6 / 39.1, 37.1 / 39.0 | 6515, 6690, 6404 |

Main on this base is not scout 240's main: its Andes share is 10.2% (was 16.0%) and its land above 3 km 2.76%
(was 2.27%), and seed 1 alone is above the 3.5% line (4.00%) and below the 38% continental line (37.8%).

- **Share 0.2 + collapse fails** the high-ground bar (seed 2 4.51%, mean 3.59%) and continental crust (36.6-37.7%).
- **Share 0.1 + collapse passes the first three bars** (Andes share 21.5% mean against main's 10.2%; land above 3 km
  2.26% mean, max 3.29%, against main's 2.76% and 4.00%; land within 1.4 points of main). On continental crust it
  is 37.9% on seed 1 (main 37.8% on that seed), 38.5% and 38.9% on the others: it fails a per-seed reading of the
  line by 0.1 point, on the seed where main fails it too, and passes a reading over the three seeds (median 38.5%).
  I do not loosen the line; the coordinator decides which reading scout8.md meant.
- Dead high ground at share 0.1 + collapse (`scout9_decay.py`, checkpoints): 0.2-0.6% of land above 3 km was last
  squeezed more than 100 Myr ago (main 12.9-22.6%), 2-7% more than 60 Myr (main 27-37%).

| run | seed | land >3 km (ckpts) | by Myr since squeezed: 0-10 / 10-30 / 30-60 / 60-100 / >100 / never | dead-belt excess e-folding |
|---|---|---|---|---|
| share 0.1 + collapse | 1 | 3.27 | 57.6 / 20.7 / 16.4 / 4.5 / 0.2 / 0.6 | 157 Myr |
| share 0.1 + collapse | 2 | 2.24 | 62.3 / 23.3 / 12.0 / 1.5 / 0.2 / 0.8 | 161 Myr |
| share 0.1 + collapse | 6001 | 3.15 | 59.0 / 20.8 / 12.5 / 6.4 / 0.6 / 0.7 | 158 Myr |
