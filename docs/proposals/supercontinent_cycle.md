# Supercontinent cycle: three proposals

*Status: C's breakup fix + B′ implemented 2026-10-14 (branch `mantle`); see "Implemented" at the end. Written 2026-10-13.*

## The problem

On Earth, continents have gathered into a single supercontinent roughly every 400–600 Myr:
- Columbia, ~1.8 Ga;
- Rodinia, ~1.0 Ga;
- Pangaea, ~0.3 Ga.

Each one lasts 100–200 Myr and then breaks up.

In our runs, the starting supercontinent breaks into 30–60 pieces. Over 1.5–2 Gyr, the largest landmass stays at 3–14% of the surface (Pangaea was ~25–30%). It never reassembles, across 12 survey seeds.

### What the model has today (`planet/tectonics.py`)

**Plate motion** (`_forces`): each step, every plate's velocity is solved from four forces:
- *slab pull*: a sinking slab drags its plate toward the trench;
- *ridge push*: plates are pushed away from spreading ridges;
- *collision drag*: colliding continents resist further closing;
- *mantle drag*: a random, slowly wandering push per plate (an Ornstein–Uhlenbeck process, ~60 Myr memory).

None of these knows where other continents are or where the mantle is sinking. So continents random-walk, and collisions happen only by chance.

**Merging** (`_sutures`) works as intended: two colliding plates weld into one once the collision stalls. This is the "merger feature". It merges plates that happen to meet; it doesn't *bring* them together. Today that's ~5 long collisions per 500 Myr.

**Breaking** (`_maybe_rift`) has three triggers:
- *heat*: any plate carrying more than 7% of the surface as continent rifts at a rate of ~1/130 Myr, scaled up for bigger continents;
- *stress*: big plates whose halves are pulled apart break;
- *margin*: old passive margins start subducting.

Together these break up anything large quickly, and rifts can cut anywhere, so fragments get small.

To get cycles, we need **(a) something that draws continents together** and probably **(b) breakup that produces a few large pieces, not dozens of small ones**. The three proposals mainly differ on (a); each includes a fix for (b).

### What "working" would look like (proposed acceptance criteria)

Measured over a 2 Gyr run at level 6, across ~4 seeds:
- The largest landmass exceeds ~25% of the surface (≈60% of all continental crust) at least twice per 2 Gyr.
- Assemblies come ~300–700 Myr apart.
- Between assemblies there are ~5–15 landmasses bigger than 0.5% of the surface. Today there are 30–60, mostly slivers.
- No harm to what we've just fixed: land 25–35%, crust budget, ocean age ~50–90 Myr, plate speeds 2–8 cm/yr.
- Runtime stays within ~10% of today's.

---

## Proposal A: a slowly evolving large-scale mantle flow (imposed)

**Idea.** Below the plates, the mantle convects in a few huge cells. Supercontinents gather over the big *downwellings*, where cold slabs sink and drag the surface inward. Breakup follows when the mantle under the assembled continent heats up and turns into an *upwelling*. Africa and the Pacific today sit over two giant warm upwelling regions, and the "ring of fire" between them is a downwelling girdle.

**Mechanism.**
- Define a smooth world-frame **mantle flow field** on the sphere: a few low-order spherical-harmonic patterns (degrees 1–2, i.e. one or two big up/down regions).
- Its pattern rotates and morphs slowly, over ~300–500 Myr.
- Add a basal-drag term to `_forces`: each cell feels the mantle's surface velocity, weighted by how deep its plate's root goes.
  - Continents (deep keels) feel it ~2–3× more than ocean.
  - The existing `continental_keel` parameter already weights continental cells in the drag matrix.
- The random OU drag stays, but becomes smaller.

**Breakup fix.** Continental heat rifting becomes much less likely unless the continent has sat still for ≥100 Myr. Rift cuts prefer old sutures (weak zones, which is where Pangaea actually split), so the pieces are the large blocks that went in.

**Parameters:**
- `mantle_flow` (strength);
- `mantle_flow_period` (Myr per cycle);
- `mantle_degree` (1 = one supercontinent pole, 2 = Pangaea/Pacific-like).

**Pros:**
- Simple, cheap (one vector field per step) and very controllable.
- Cycles are almost guaranteed, and the period is a dial you can set.

**Cons:**
- It's imposed: the mantle doesn't react to the plates.
- Cycles can look metronomic.
- Continents are told where to go rather than finding their way.

**Effort:** small, ~1 session including tuning.

## Proposal B: a mantle that remembers where slabs sank (emergent)

**Idea.** The same physics as A, but the mantle flow is built from the simulation's own history instead of imposed:
- **Cold slab graveyards.** Wherever plates subduct, cold dense rock piles up in the mantle and pulls the surface toward it. Continents converge on long-lived subduction zones (the "introversion/extroversion" picture of supercontinent assembly).
- **Thermal insulation.** A big continent that sits still traps heat beneath it. After ~100–200 Myr that hot patch pushes the surface outward, and the continent breaks apart, as Pangaea did over the hot mantle under Africa.

**Mechanism.** Keep a world-frame scalar field `mantle_T`, a temperature anomaly per cell, on the existing grid:
- **Source:** every step, subduction deposits cold (−) at the trench, proportional to convergence × slab age.
- **Source:** continental cells add warmth (+) slowly, faster the longer the continent has sat over the same mantle.
- **Relaxation:** the field diffuses a lot (smoothing ~2000–4000 km) and decays over ~300 Myr, so it represents the big-scale mantle, not the local slab.

**Forces.**
- Basal drag pushes plates *down* the gradient toward cold, i.e. down `∇mantle_T`; continents feel it more (keel).
- Heat rifting's hazard is driven by the warmth under the continent, instead of today's fixed "continent > 7%" rule.

**Hotspots, bonus.** New plumes become likelier where `mantle_T` is warm. That's realistic: plumes rise from the edges of the big warm regions.

**Parameters:**
- `slab_memory` (strength, decay Myr);
- `insulation` (rate);
- `mantle_scale_km` (smoothing);
- `basal_drag` (strength).

**Pros:**
- Physical and emergent: assembly sites and timing come from each world's own history, so different seeds have different stories.
- Plays nicely with the existing slab pull, hotspots and heat rifting.
- Hotspots get a natural home.

**Cons:**
- More parameters.
- Feedbacks can overshoot: everything piles together, or nothing ever converges. It needs careful, envelope-tested tuning.
- Cycles aren't guaranteed for every seed; some worlds might never complete one. You might also count that as a pro.

**Effort:** medium, ~1–2 sessions. It needs a diagnostic for the largest landmass over time, which the survey scripts already compute.

## Proposal C: fix breakup and closure rules only (lightest touch)

**Idea.** Leave plate forces alone and change the event rules so the Wilson cycle (ocean opens, ages, then closes) does more of the work.
- **Breakup.** Big continents rift less often (fixing the "30–60 slivers"):
  - only along old sutures or the thinnest crust;
  - never cutting off a piece smaller than ~3% of the surface.
- **Closure.** Interior oceans, those opened by a recent rift between continents, close preferentially:
  - their old margins start subducting sooner than an outer ocean's;
  - a weak pull draws together continents that were once joined. That's the "introversion" story: the Atlantic-type ocean closes and the same continents re-collide.

**Mechanism:**
- Changes inside `_maybe_rift` (where cuts go, minimum piece size, a lower heat hazard).
- A record of each ocean basin's "parents" (which rift created it), so its margins get a higher `margin` subduction hazard as they age.
- Optionally a small attraction term between plates that share a recent suture.

**Pros:**
- Smallest change.
- Directly targets the fragmentation, which is the most visible defect.
- Easy to reason about.

**Cons:**
- It's bookkeeping more than physics.
- It may produce repeated open-and-close of the same ocean, the accordion pattern, without true whole-planet assembly.
- Probably won't reach the 25% landmass criterion on its own.

**Effort:** small–medium, ~1 session.

---

## B′: B plus rifting from mantle drag under the plates (your suggestion, 2026-10-13)

**Idea.** The mantle drags on the plates' undersides (basal traction). If the flow beneath one plate diverges, pulling its two halves different ways, the plate is stretched and can split. This is the "active rifting" picture of continental breakup:
- East Africa/Afar is rifting over a mantle upwelling today.
- Giant lava outpourings came just before the Atlantic opened and before India left Madagascar.

The other picture, "passive rifting", has a plate pulled apart from its edges; the existing slab-pull forces already cover it.

On most oceanic plates the mantle acts more as a brake than an engine, since slab pull drives them faster than the mantle under them. Basal drag matters most under thick continental keels, which are exactly the plates whose breakup we care about.

**Mechanism.** On top of B:
- B's mantle field supplies a **traction vector under every cell**, flowing from warm regions toward cold ones and weighted by keel depth.
- That traction goes into the force balance in `_forces`, as B already plans.
- The existing **stress trigger** in `_maybe_rift` then decides breakup: it finds the line along which a plate's halves would separate fastest, compares that opening rate with a strength threshold, and today counts only boundary forces plus random drag. With traction in it, a continent over a warming, diverging mantle splits along the divergence.

**What this replaces:**
- the fixed "continent > 7% rifts at a rate of ~1/130 Myr" heat rule;
- the "plates > 20% of the surface break up readily" rule.

Breakup becomes emergent: assemblies sitting over cold downwellings hold together until insulation warms the mantle beneath them, then come apart along the warm axis. Plumes, also tied to warm mantle in B, would tend to appear along that axis just before the split, as in the Earth cases above.

**Cost:** about the same as B. The traction comes from the same field, and the stress-cut machinery already exists.

**Risk:** if traction is too strong, every big plate is permanently under tension; if too weak, nothing rifts at all. Envelope tests on the landmass count and the largest landmass, plus a seed sweep, would guard that.

## Recommendation

Do **C's breakup fix first** (minimum piece size, cuts along old sutures), whichever option you pick. It's cheap, it's needed in every scenario, and it alone should cut the landmass count a lot.

Then **B′** (B plus traction-driven rifting, replacing the fixed rifting rules), with A as a fallback:
- B fits the project's direction: physics depth, controls that influence rather than force, and each world telling its own story.
- If B's feedbacks prove too fiddly, A's imposed field is a quick and dependable substitute. Both use the same new basal-drag term in `_forces`, so the work isn't wasted.

## Questions for you

1. Should every world be *guaranteed* a cycle (favouring A), or is it fine that some seeds never reassemble (B)?
2. Is a tunable cycle period worth exposing as a knob (A gives it directly; B only indirectly)?
3. Do you want plume/hotspot placement tied to the mantle field (B's bonus), or kept separate for now?

---

## Implemented (2026-10-14): C's breakup fix + B′, and lighter sediment

The user chose the breakup fix + B′, with hotspots tied to the warm mantle and no guarantee of cycles.

### Breakup fix (`events.py`)
- `strength()` gives the lithosphere's strength per cell (1 = ordinary crust):
  - cratons 1.6;
  - collision belts 0.35–0.85, weakest when young (sutures);
  - thinned crust down to ×0.7;
  - plume swells ×0.7–1 (rifts follow plumes, like Afar).
- `stress_cut` tries 12 straight cuts with offsets.
  - It ranks them by opening speed ÷ the mean strength along the cut, × (plate area / 5%)^¼. A bigger plate pulls harder per length of cut.
  - `rift_side` tries 4 wandering (noisy) cuts and keeps the one through the weakest rock.
- `rift_min_piece` = 0.03: no rift leaves a piece with 0.3–3% of the surface as continent. Oceanic pieces are fine.

### B′ (`mantle.py`)
`sim.mantle` is a world-frame temperature anomaly (relative units, about ±1–2).
- **Smoothing:** low-passed in real spherical harmonics, degrees 1–8 (built once per grid by orthonormalising monomials), with a heat kernel over `mantle_scale_km` = 2500. The global mean is dropped.
- **Memory:** it relaxes over `mantle_memory` = 200 Myr.
- **Sources:**
  - *Cold slabs:* each trench adds cold ∝ convergence × slab age (`slab_cold` = 0.002).
  - *Insulation:* warmth under continents ∝ `mantle_lid` (`insulation` = 0.04). `mantle_lid` is a ~100 Myr running average of continental cover over that patch of mantle. So the longer a continent stays put, the faster the mantle under it warms.
  - *Starting state:* warm under the starting continents.
- **Traction:** −`mantle_drag` (0.6) × ∇(mantle + eddies) × the drag weights (continental keels 2.5×). It goes into `motion.forces` before the torques, so `stress_cut` sees it.
- **Eddies:** `mantle_eddies` (rms 0.3) is a random OU field over degrees 3–8 with a 60 Myr memory. It stands in for convection the model doesn't resolve, so different parts of a big plate get dragged different ways.
- **Plumes:** `plume_odds` ∝ exp(1.5·T) × (1 + T⁺ × |∇T| / mean). New plumes favour warm mantle, and the edges of warm regions most.
- **Rules removed:** the fixed heat rule (continent > 7%) and the big-plate rule (> 20%), along with the params `rift_min_continent` and `big_plate`. Other changes:
  - `rift_stress` 3 → 2 cm/yr;
  - per-plate wander `mantle_noise` 0.35 → 0.2;
  - rift events say whether they opened over warm or cold mantle.
- **Cost:** ~11 ms per step at level 6 (~2%). The basis is built once per grid (0.4 s). Level-6 runtime per 500 Myr was 86 s against 93 s before (B′ has fewer, cheaper rifts).
- **State:** `mantle`, `mantle_lid` and `mantle_eddies` are in `Simulation.STATE`.

### Lighter sediment (`isostasy.py`, user decision)
- **Density:** sediment is 2.1 g/cm³ at the surface and compacts to 2.6 at depth (2 km e-folding). Crust is 2.80 (continental) and 2.85 (oceanic).
- **Elevation:** `elevation()` adds `sediment_lift` for the light cover (cover minus lava flows). Erosion of cover and all deposition use the marginal `sediment_iso`.
- **Basin fill:** filling 5 km of deep water now takes ~15 km of sediment (3×, as on Earth) instead of ~25 km.
- **Effect at level 6, seed 1, 1 Gyr** (light vs crust-density sediment, same mantle):
  - cells at the 18 km metamorphic cap: 0–103 instead of 76–664;
  - land: about +1.5 points;
  - median land elevation: +100–200 m;
  - 99th percentile and maximum elevation: unchanged.
  - The maximum cover still reaches the cap in a few cells.

### Results: level 6, 2 Gyr, seeds 1–4 (final code, merged with main)
Command: `tools/supercontinent.py --level 6 --seed 1 2 3 4`. "Largest" is the largest landmass above sea level, as a % of the surface.

| seed | spells > 25% (Myr, peak %) | landmasses > 0.5% while dispersed | plates (median, min) | land % (median, range) | volume | ocean age | speed |
|---|---|---|---|---|---|---|---|
| 1 | 0–280 (start), 400–590 (29), 1930 (29) | 6 | 6, 3 | 34.4, 21.9–38.7 | 1.00 | 80 | 4.0 |
| 2 | 0–510 (start), 870–970 (32), 1740–1770 (27), 1950–1980 (30) | 6 | 6, 2 | 34.8, 26.4–38.1 | 1.01 | 78 | 4.0 |
| 3 | 0–240 (start), 450–720 (37), 1110–1200 (28) | 5 | 7, 2 | 35.8, 25.8–39.1 | 1.02 | 77 | 4.2 |
| 4 | 0–300 (start), 430–550 (34), 1220–1400 (38) | 7 | 7, 2 | 34.3, 26.8–40.5 | 1.00 | 77 | 3.9 |

Before (main before this work, same metric): after the starting supercontinent broke up, nothing above 25% in 3 of 4 seeds. Seed 4 had one brief spell (470–570, 31%). The largest landmass's median was 8–10%.

**Against the acceptance criteria:**
- **Reassembly > 25% at least twice per 2 Gyr:** yes, counting the starting supercontinent, in every seed.
  - Counting only reassemblies, seed 2 has 3 and seeds 3 and 4 have 2. Seed 1 has 1, plus a single 10-Myr sample at 1930.
  - Peaks are 27–38%.
  - Assemblies form over cold mantle (anomaly about −0.4 to −0.5 under the largest continent). The mantle warms under them, and they rift (most continental rifts are tagged "over warm mantle").
- **Spacing ~300–700 Myr:** mostly 400–870 Myr between assembly starts, so somewhat long. There are some longer quiet stretches (seed 1: 590–1930).
- **5–15 landmasses > 0.5% between assemblies:** median 5–7 while dispersed (largest < 20%), range up to 11. Before, the median was 8–10 at all times (7–9 with the breakup fix alone).
- **Land 25–35%:** median 34–36%, on the upper edge, and up to ~40% when assembled. About +1.5 points come from the lighter sediment and the rest from assembled continents flooding less. Excursions below 25% are brief (sea-level swings when the plate count dips).
- **Crust volume, ocean age, speeds:**
  - volume ratio 1.00–1.02 at 2 Gyr, but the scorecard at 1 Gyr showed 1.04;
  - ocean age 77–80 Myr ✓;
  - speeds 3.9–4.2 cm/yr ✓.
- **Runtime:** the same as before or slightly faster.

**Showcase:** run `6d9dcf`, "B′ supercontinent cycle seed 2" (level 6, 2 Gyr, with checkpoints). Spells above 25% of the surface:
- 0–508 Myr: the start, which breaks up by ~100 and regathers by ~200;
- 892–976 (32%);
- 1736–1772 (27%);
- 1948–1988 (30%).

Plots: `seed<N>.png` in the job's tmp dir (largest landmass, count, events, mantle under the largest continent).

### Remaining issues
- **Low plate count:** the median is 6–7 (it was 8–10), with dips to 2–3 about 10–20% of the time. Plates are now born less often, because the fixed heat rule made ~65 splits per 2 Gyr. Traction-driven welding isn't the cause: sutures fell from ~90 to ~50.
- **Land on the high side** (median ~34–35%), and the crust volume drifts up to +2–5% mid-run. While continents are assembled, fewer continental margins subduct, so subduction erosion removes less crust, and the volume thermostat (power 4) only partly compensates.
- **Quiet stretches:** some seeds go quiet for ~1 Gyr between assemblies (seed 1). Cycles aren't metronomic, as the user accepted.
- **Elevation spikes:** a one-sample ~12–13 km spike in the maximum elevation appeared once each in two runs (B′ seed 1 at 1260 Myr; breakup-fix-only seed 2 at 1200 Myr). It's probably a transient right after a split. Not investigated.
- **Compaction isn't remembered:** an uplifted, eroded sediment pile becomes porous again.
