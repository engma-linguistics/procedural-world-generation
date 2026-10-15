# Physics audit: tectonics (PW-245)

Scope: `planet/tectonics/*` (simulation, crust, isostasy, mantle, motion,
events, volcanism, plate_kernels, record, setup, earth's sea level),
`planet/landform.py`, and the geometry kernels in `planet/kernels.py`.
Branch `worktree-agent-a530cba53893c9bf6`, code at 10b89eb.

Grading follows the owner's calibration. A **sound approximation** is a
recognised simplification with a physical basis, however crude. A
**bandaid** forces an answer, hides a process error, or exists to push a
metric. Simplification alone is not a finding.

## Method and measurements

I read the code against overview §2.2-2.4 and §2.8, and against the
processes it names. I ran an instrumented probe
(`scratchpad/tect/probe.py`: the thermostats, the rift pool, the speed cap,
the crust budget, ocean depth against GDH1, the moat and sag split, hotspot
sediment lift) on:
- L5 seed 1, 0-400 Myr, default params (`l5_base`);
- the same with `max_speed=1000` (`l5_nocap`);
- L6 seed 21, 0-1000 Myr (`l6s21`);

plus a per-plate speed probe (`speed.py`, L5 seed 1, 300 Myr, cap on and
off). All with NUMBA_NUM_THREADS ≤ 4. No runs were stored.

**Crust budget closes exactly.** In every run, the sum of the booked
processes equals the change in continental volume (closure error 0).
Every change is booked, including `resolve` and `events` measured
before and after.

## Findings, ranked

### 1. Sea level hides a persistently young ocean behind a learning baseline (high, bandaid)
`earth.py:100-106`. The basin term is measured against a baseline that
learns the smoothed floor depth over ≤ 300 Myr. Whatever the floor does
for long, sea level is pulled back to 0. In both probe runs the model's
ocean stays much younger than the steady-state ocean it starts from (and
than Earth's): L6 seed 21 mean ocean age 40.6 Myr over 1 Gyr (start 55,
Earth ~64), L5 seed 1 40 Myr. Against the fixed starting floor, with the
physical water-loading factor (ρm − ρw)/ρm = 0.69 instead of the code's
0.5, the basin term would be **+200 to +370 m for almost the whole Gyr at
L6** (up to +557 m after the first breakup; sd 104 m). The model instead
gives −99 to +184 m (mean +13 m). The baseline also makes spurious
lowstands: at L5 t = 204 Myr the floor's mean age (61 Myr) equals the
start's, yet sea_tect is −116 m. So the land share and the stable sea
level are met partly because the term that should report the young ocean
cancels it. The likely process cause is fast spreading: mean cell speed is
6.0-6.6 cm/yr, against Earth's ~4-5. (Seeds differ: the scorecard's L6
seeds 1/2 end at 95/63 Myr. On an old-ocean seed the same baseline
hides a lowstand instead. Either way the term is cancelled, not
measured.)

The tanh ±250 m is a soft limiter, acceptable as such. The depth law
(half-space cooling to 6400 m at 119 Myr) is a sound approximation of
plate-model flattening. It is isostatically consistent with the
continental datum: a 35 km continent at +250 m balances 6.4 km-deep old
ocean within 1% of column mass. It is 0.5-0.8 km deeper than GDH1 at
100-150 Myr, so sea level is ~25-30% more sensitive to ocean age
(mean-depth range 978 m vs 785 m with GDH1 at L6).

Fix (simplest sound version): a fixed reference (the starting floor),
0.69, the limiter kept but wider. Expect much higher sea and less land
(several points) until the ocean-age/plate-speed cause is fixed. So this
needs a decision and probably goes together with plate speeds and ocean age
(PW-051, PW-024). On PW-051: its clip hits in stagnant phases are the same
term seen from the old side, and the baseline is also what later makes them
fade. Draft: `draft-audit-tectonics-sea-level-baseline.md`
(needs-decision).

### 2. Flexural moat: share tuned to a closed-basin KPI, and only half of flexure applied (med, bandaid)
`isostasy.py:96-108`, `params.py:56`. The Airy root of thick continent is
blurred over 150 km, and continent sinks by `flexure` (0.15) × (blurred −
own root), with a tanh cap at 2.5 km. Read as flexure, the share should be
~1. 0.15 was picked by commit 1571042 to hit an inland-drainage share on one
L7 seed (35% → 46%; 0.3 gave 65%). Only the moat half is applied: the
belt keeps its full Airy height, so the moat is an uncompensated depression.
Globally it is small (L6 seed 21: mean −33 m over continental crust, up to
−44; about 0.2-0.4 points of land), but it is the mechanism behind PW-054's closed
basins, so that KPI is met by a tuned knob. The L6/L7 gap in closed basins
(9% vs 20% before the moat) points to a level-dependent cause elsewhere,
which the share now hides.
Fix (sound): share 1, blur width from a realistic elastic thickness, both
halves applied (net zero), then look for the level dependence in
drainage/sediment. Draft: `draft-audit-tectonics-flexure-share.md`
(needs-decision).

### 3. Rifted-margin thickness steered by the global area error (low-med, bandaid)
`crust.py:307`. A margin's minimum thickness is raised from 12 to 18 km in
proportion to (shrink − 1), the area thermostat's excess. This is a local
physical property set by a global KPI error, a second lever on PW-046 next
to subduction erosion. It is active only while area is above target: at L5
seed 1 on every step (shrink 1.0-1.8, mean 1.27), at L6 seed 21 on 30% of
steps (shrink 0.66-1.56). Fix: one
fixed margin thickness; leave area to the subduction-erosion thermostat.
Draft: `draft-audit-tectonics-margin-steering.md`.

### 4. Hotspot sediment floats at the volcano rate beyond the pile cap (low-med, inconsistency left by PW-172)
`isostasy.py:156-157, 151-153`. `_k` gives every HOTSPOT cell 1.75 × K_SEA,
so `sediment_lift`/`sediment_iso` keep the flexural support PW-172 capped
in `elevation`. `iso_rate` also keeps ISO_VOLCANO beyond the pile cap, where
`elevation` moves at ISO_SEA. Extra lift measured up to 410 m at L5 and
**1.07 km at L6** (mean of the per-frame maximum 620 m). Draft:
`draft-audit-tectonics-hotspot-sediment-iso.md` (xs).

### 5. Rift pool decay deletes crust (low, conservation)
`crust.py:304`. Pooled stretched crust decays by e^(−dt/100) and is deleted,
though the comment says it stays in the flanks. It is booked under
"stretch", so the budget hides it. L6 seed 21, 1 Gyr: 3228 km×L5-cells
decayed vs 58 847 laid as margin (~5% of stretched crust; L5 the same). It is a small contributor to PW-046's thinning.
Draft: `draft-audit-tectonics-rift-pool-decay.md` (xs).

### 6. Hotspot piles: ISO_VOLCANO at cell scale (low, sound approximation; noted)
`isostasy.py:41-42, 193-196`. A narrow pile held up by the plate (350 m/km
vs Airy's 200) is real for loads narrower than the flexural wavelength. At
L6/L7 cell size it adds buoyancy without the surrounding moat (the Hawaiian
Deep). Since PW-172 it is capped at 20 km of pile, so it is bounded. I judge
it a sound approximation that helps sub-cell islands show (PW-117). No draft.

### Checked and found sound (no action)
- **Orogen heights / MAX_KM = 80 km.** The cap rarely binds: over 1 Gyr at
  L6 it removed 2 500 km×cells against 116 542 stacked by collisions (2%;
  L5 0.8%), and 0.8% of sampled frames had a single cell at 80 km. Heights are
  set by crust flow, a diffusion ∝ x + x³ above 40 km: lower-crustal flow
  and gravitational collapse, a sound stand-in. Max elevation reached
  8.7 km (L6) from crust physics, not a clip. The flow's flux limiter (0.15)
  is a numerical stability limit and is not reached at default `crust_flow`
  (k0 × 68 ≈ 0.03 at 80 km).
- **Speed cap 18 cm/yr.** It binds on 20% of plate-steps, but those are
  mostly small plates (5% area-weighted). With the cap off, the median
  plate's fastest point is unchanged (11.9 → 12.2 cm/yr), p90 goes 18 → 23,
  mean cell speed 6.65 → 6.31, land, thickness and ocean age are unchanged,
  and plate count is 12.8 → 10.9. A sound limiter on small plates (drag ∝
  area, boundary forces ∝ perimeter). Mean speed 6.2-6.6 cm/yr is above
  Earth's ~4-5 but inside the envelope.
- **Thermostats** (`crust.py:54-78`). Explicit controllers toward
  parameter targets (area 40%, mean 35 km), not Earth-keyed, documented,
  never at their clips in my runs (the volume thermostat climbs to 2.4×
  nominal continental arc growth by 1 Gyr at L6 as continents thin to
  31.8 km: PW-046, already known). A design choice that makes land share
  mostly a parameter; the owner already decided to steer it this way
  (PW-238).
- **Airy constants.** 150 m/km on land and 200 m/km under water match ρc
  2.80 and ρo 2.85. Sediment density and compaction are consistent:
  `sediment_iso` is exactly ∂elevation/∂sediment off hotspots.
- **Thermal sag** (`isostasy.py:111-118`). McKenzie's f(β) = (β/π)sin(π/β),
  E0 = 3.2 km water-loaded → 2.2 air-loaded, τ = 62.8 Myr: correct.
- **Rates against Earth fluxes.** Arc growth ~35-50 km³/km/Myr after the
  thermostat, and subduction erosion ~30 km³/km/Myr at 5 cm/yr. Both are
  inside Earth's published ranges, and both are per km of trench at every
  grid level.
- **Level scaling.** Arcs, erosion, accretion, stretching, stacking and
  crust flow are all per km or per km², with substeps ∝ scale².
- **Slab pull** ∝ clip(age/80, 0.3, 1.5): a crude but sound stand-in for
  slab buoyancy (∝ √age). The mantle field, plume odds and traction are
  sound and smooth.
- **Collision stacking** conserves crust (the loser's thickness is stacked
  in full). Subduction is the deletion of ocean crust.
- **Volcano limits** (TOP_MAX 4.2/3.5 km, LAVA_MAX_KM 3 km, hmax ∝ √age,
  vent gaps from Te = 2.7√age). These are eruptive-height and flexure
  laws with citations, not KPI fits.
- **Ice and sea level** (×0.9 of ice volume over ocean area) is consistent
  by construction.
- **No latitude-, region- or Earth-keyed branches** anywhere in the
  tectonics or landforms. The only `lat` uses are passed to climate and
  ice.

### Tests and history
- `test_envelopes.py`: the continental-thickness floor went 30 → 28 km
  (0fd35e5), back to 30 (37ed15f), then 28 (1ad9059, "seed 1 varies
  29.5-34.8 km run to run, PW-215"). It is loosened, with a stated reason;
  it allows the L5 thinning I measured (37 → 31 km over 400 Myr, PW-046).
  Weak but honest. Other envelopes (ocean age ≤ 120 Myr, max elevation
  ≤ 9.5 km) are wide but have not been widened.
- The only metric-driven tectonics commit is 1571042 (flexure 0.3 → 0.15
  for inland drainage); see finding 1. PW-238's 37 → 35 km nudge is an
  owner decision on land share (a parameter, not hidden).
- No skipped or xfail tests in the area.

## Appendix: inventory

| file:line | what | justification found | verdict |
|---|---|---|---|
| isostasy.py:96-108 | flexure share 0.15, moat only, MOAT_MAX tanh 2.5 km | commit 1571042 (closed-basin KPI, one L7 seed) | suspicious (bandaid) |
| earth.py:105 | sea-level baseline learning over ≤ 300 Myr | "only real changes move the sea"; hides a young ocean | suspicious (bandaid) |
| earth.py:106 | ×0.5 water loading | "halved because the water pushes the floor down" | weak (0.69 physical) |
| earth.py:23,106 | SEA_TECT_MAX ±250 m tanh | Phanerozoic range | fine (limiter) |
| crust.py:307 | margin min km steered by area error | PW-046 | suspicious (bandaid) |
| crust.py:304 | rift pool decays 100 Myr, deleted | comment (inaccurate) | weak |
| isostasy.py:157 | 1.75× K for all hotspot sediment | none since PW-172 | weak |
| isostasy.py:41-42, 193-196 | ISO_VOLCANO 350 m/km, pile cap 20 km | flexure of narrow loads, PW-172 | fine |
| isostasy.py:201 | ocean depth HSC capped at 6400 m | half-space fit; plate-model flattening | fine |
| isostasy.py:36-50 | 250 m at 35 km; 150/200 m per km; densities | Airy; consistent with old ocean | fine |
| isostasy.py:71-72 | SAG 2.2 km, 63 Myr | McKenzie 1978 | fine |
| isostasy.py:148 | LAVA_MAX_KM 3 km | Deccan/Siberian Traps, PW-133 | fine |
| crust.py:37-38, 75-77 | thermostats e^(4 err), clips 0.1-5, 0.2-5, ±0.4 | documented; never at clip | fine |
| crust.py:34 | RIFT_THINNING 0.015/Myr | record threshold | fine |
| crust.py:35 | FOREARC_KM 120 | arc-trench gap | fine |
| crust.py:130 | stretching only on crust > 23 km | stretching moves to the ridge | fine |
| crust.py:222 | edge worn below 15 km becomes ocean | definition | fine |
| crust.py:268-270 | thinning floor 22 km | margin thickness range | fine |
| crust.py:277 | MARGIN_MIN_KM 12 | rifted margins 10-25 km | fine |
| crust.py:366 / simulation.py:328 | MAX_KM 80 cap; clip 1-80 | flow is the process; cap < 1% | fine |
| crust.py:371 | > 50 km becomes OROGEN | metamorphism | fine |
| crust.py:443-444 | born at 20 km; "sedimented" tests | PW-172 | fine |
| crust.py:453 | craton at 1500 Myr, < 45 km | definition | fine |
| crust.py:32-33 | TUFF_SHARE 0.1, GRANITE_KM 4 | geological rules of thumb | fine |
| plate_kernels.py:221-222 | crust flow above 40 km, x + x³, flux ≤ 0.15 | lower-crustal flow; stability | fine |
| plate_kernels.py:100,149,166 | hole-fill thresholds (deg−2, 4, deg−1) | sampling artefacts | fine |
| motion.py:113-114 | slab pull clip(age/80, 0.3, 1.5) | old slabs denser | fine |
| motion.py:123 | collision drag clip(conv, 0, 15) | viscous resistance | fine |
| motion.py:132 / mantle.py traction | keel 1.5 (2.5× drag) | continental keels | fine |
| motion.py:146 | 0.1×area spin regulariser | numerical | fine |
| motion.py:148-151 / params.py:42 | max speed 18 cm/yr | binds on small plates; no KPI effect | fine (limiter) |
| params.py:39 | velocity relax 15 Myr | stand-in for inertia | fine |
| mantle.py:132 | slab age clip 0.3-1.5 | as slab pull | fine |
| mantle.py:44-45 | LMAX 8, eddies degrees 3-8 | resolution of the field | fine |
| mantle.py:178 | plume odds exp(1.5 clip(m)) × edge | plume generation zones | fine |
| events.py:25 | TRENCH_KM 6000 | arc lengths | fine |
| events.py:103 | suture contact threshold max(3, 4·scale) edges | level-consistent | fine |
| events.py:125 | no weld within 80 Myr of rifting | anti-flicker | fine |
| events.py:141 | sliver < 0.15% of cells | numerical | fine |
| events.py:178-183 | strengths: craton 1.6, belt 0.35-0.85, thin 0.7, swell −30% | weak zones | fine |
| events.py:242 | size^(1/4) | "gently" (heuristic) | weak but harmless |
| events.py:308 | margin hazard ×3 | none | weak but harmless |
| events.py:465-470 | split kick 2.5 cm/yr, wander ±4 | none (seeds the rift) | weak but harmless |
| events.py:190 | rift_min_piece 0.03 / 0.1× | few big blocks | fine (design) |
| volcanism.py:55-68 | PLUME_KM 150, HEAD 6 Myr, GAP 60-150 km, TOP_MAX, APRON_TOP, AWASH etc. | cited analogues | fine |
| volcanism.py:122 | swell 1000 m × strength | Hawaii swell ~1 km | fine |
| volcanism.py:127 | ×0.25 plume under continents | melt stalls | fine |
| volcanism.py:194-196 | Te 2.7√age or 40 km; alpha ∝ Te^0.75 | Watts; flexure | fine |
| volcanism.py:264-265 | hmax 2500 + 800√age ≤ 10.5 km | Vogt 1974 | fine |
| volcanism.py:366 | erosion τ ∝ √(1500/rain), rain clip 150-6000 | heuristic | fine |
| setup.py:70-90 | starting relief, cover, ages (mean 60 Myr) | PW-052/053 | fine |
| simulation.py:355 | trench depth −350 m per cm/yr, ≥ −4000 | snapshot only | fine |
| landform.py:113-130, 150 | class thresholds, fold wavelength clip 3-30 km | classification rules | fine |
| record.py:62-66 | MIN_KM, HIATUS, burial and quartzite thresholds | bookkeeping | fine |

Counts: 54 items; 45 fine (incl. 2 limiters and 1 design choice), 6 weak
(3 of them harmless), 3 suspicious (bandaids).
