# Supercontinent cycle: three proposals

*Status: proposal, nothing implemented yet. Written 2026-10-13.*

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

## Recommendation

Do **C's breakup fix first** (minimum piece size, cuts along old sutures), whichever option you pick. It's cheap, it's needed in every scenario, and it alone should cut the landmass count a lot.

Then **B**, with A as a fallback:
- B fits the project's direction: physics depth, controls that influence rather than force, and each world telling its own story.
- If B's feedbacks prove too fiddly, A's imposed field is a quick and dependable substitute. Both use the same new basal-drag term in `_forces`, so the work isn't wasted.

## Questions for you

1. Should every world be *guaranteed* a cycle (favouring A), or is it fine that some seeds never reassemble (B)?
2. Is a tunable cycle period worth exposing as a knob (A gives it directly; B only indirectly)?
3. Do you want plume/hotspot placement tied to the mantle field (B's bonus), or kept separate for now?
