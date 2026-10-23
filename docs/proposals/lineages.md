# Lineages: peoples evolving and spreading across the three time scales (PW-103, phase 3)

*Proposal and build notes, v2 "cool new stuff" lane, 2026-10-23. Status: stage 1 built on the agent's leans (below); the decisions are filed as needs-decision drafts and each is a small swap.*

## The ask

The owner (2026-10-23): give a phylogenetic tree of fantasy peoples with rough split times and habitat preferences; find plausible places where each line arose and how ranges moved, through the tectonic run (Myr), the glacial time zoom (kyr) and a new **finest pass** over the last ~20–50 kyr (centuries); and a "present day", especially the last ~3000–1000 years, with mixing in connected lowlands and isolation behind seas, mountains and deserts. Optionally soft wishes such as "goblinoids next to orcs", "aarakocra and tortles on the island chains", "lizardfolk far from them".

Principles: game-useful and plausible, not a biology research project; nudge, never force; cheap enough to rerun with a different seed in seconds to a minute at L6.

## The chain

```
tectonic run (keyframes every 4 Myr)          deep epochs: the root lines appear, early splits
   -> glacial time zoom (frames every 2 kyr)   glacial epochs: ice comes and goes, land bridges open and close
      -> recent pass (frames every 0.5 kyr,     the last ~30 kyr at 100-year steps: deglaciation,
         steps 0.1 kyr; NEW)                    short cold spells and droughts, late mixing
         -> present day                         ranges, mixing zones, isolates, wish report
```

Time everywhere in this module is **years before present** ("ago"), present = the chosen moment of the time zoom (a finished world's `timezoom_kyr`, or `--now`). A split at "6 Myr" falls in the run; "150 kyr" in the time zoom; "12 kyr" in the recent pass. Splits older than the available history are clamped to its start (reported).

## 1. The recent pass (`planet recent`, `planet/lineages/recent.py`)

What it is: the last `--kyr` (default 30) kyr before the present of a time zoom, at `--step` (default 0.1 kyr) steps, one stored frame per `--every` (default 0.5 kyr). It is **not** a new physics simulation:

- **Base state:** the time zoom's own frames (every 2 kyr) of surface elevation (ice included, above that frame's sea level), ice, temperature, Köppen climate and tree cover, interpolated linearly in time (the categorical climate takes the nearer frame). Sea level and the coastline therefore move as the time zoom's do; a land bridge that opens at a glacial maximum opens here, at the century the interpolated surface crosses sea level.
- **Rain:** the time zoom stores none, so the source keyframe's annual rain is scaled by exp(0.07 ΔT) with the local temperature change since the time zoom's start (Clausius–Clapeyron, the time zoom's own rule; clipped to 0.5–1.5×), then by the variability below.
- **Short-period variability** (seeded, deterministic): a red-noise global anomaly (AR(1), τ = 300 yr, σ = 0.35 °C, the late-Holocene centennial scale), and a few regional **episodes** (default 1 per 6 kyr): a cold spell ("little ice age": −1 to −2.5 °C over a cap of 1500–3000 km radius for 200–800 years) or a drought (rain × 0.5–0.75 over a similar cap). Each is listed as an event (`kind`, time, place, size), so the viewer's event list shows "a 500-year cold spell over 45°N 20°E". If the window contains a deglaciation (the time zoom's glacial index falls by ≥ 0.4), one cold reversal (Younger Dryas-like, −2 °C poleward of 40° in the glaciated hemisphere for 1.2 kyr, in the first half of the warming) is added. The ice and coastline are not changed by the variability (it acts on habitat only: centuries are too short for the ice sheets to answer much, and the ice lane owns the ice).
- **Stored** as a run of `kind: timezoom` with `meta.phase = "recent"` and frame times in **kyr relative to the present** (−30.0 … 0.0), with the time zoom's frame stats interpolated (sea level, ice volume, orbit), so the viewer's time-zoom UI plays it with no new code: elevation, ice thickness, bed under ice, temperature, climate, tree cover, the sea-level chart. Layers: the time zoom's `elevation`, `ice`, `temperature`, `climate`, `tree_cover`, plus `precipitation`. "Finish world here" is hidden for it (finish from the parent time zoom).
- **Cost:** reading and interpolating; 30 kyr at L6 is a few seconds, ~25 MB.

What it deliberately does not do (yet): re-run the ice at century steps (the ice lane's), day-scale weather (PW-156), volcanic forcing (cheap to add as more episodes), salinity-driven abrupt events (PW-018).

## 2. The lineage model (`planet lineages`, `planet/lineages/`)

### Input (TOML; JSON accepted with the same shape)

A flat list of lines, each naming its parent (a tree without nesting, easy to edit), plus optional wishes. Sample: `planet/lineages/samples/dnd.toml` (the owner's reptilian, mammalian and avian lines).

```toml
[meta]
name = "D&D-ish peoples"
seed = 7

[[lineage]]
id = "reptilian"            # unique id
name = "reptilian stem"     # optional display name
appears = "8 Myr"           # roots only: when the line is first placed
temp_c = [18, 30]           # comfort range of the annual mean, soft edges (+-6 C to zero)
rain_mm = [800, 3500]       # comfort range of the annual rain, soft edges (x0.5 / x2 to zero)
elev_m = [-50, 1500]        # optional comfort range of the ground's height
prefers = ["Af", "Am", "Aw"]   # optional Köppen codes or groups (tropical, arid, temperate,
avoids = ["EF", "ET"]          #  continental, polar, steppe, desert, forest, coast, island, mountain)
traits = ["swims"]          # movement and behaviour, below

[[lineage]]
id = "tortle"
parent = "reptilian"
split = "1.2 Myr"           # when it split from its parent
traits = ["swims", "coastal"]
prefers = ["coast", "island", "tropical"]
# anything not given is inherited from the parent

[[wish]]                     # soft; nudges, never forces
a = "goblin"
b = "orc"
want = "near"                # near | apart
weight = 1.0
[[wish]]
a = "aarakocra"
want = "island"              # also: coast, mountain, inland
```

**Traits** (each a small multiplier, documented in `spec.TRAITS`): `flies` (crosses up to ~4 cells of sea, mountains no barrier), `swims` (crosses ~2–3 cells of sea, coastal cells favoured), `coastal` (habitat bonus within one cell of the sea), `seafaring` (from 3 kyr ago crosses ~5 cells of sea: boats), `agricultural` (late expansion: in the last 6 kyr spreads 2× faster into fertile lowland, pushes into others' ranges), `nomadic` (2× faster on steppe and grassland), `mountain` (no barrier penalty in high ground, habitat bonus there), `hardy` (comfort ranges widened by 50%), `insular` (mixes little: keeps its range late), `cosmopolitan` (mixes freely late).

### Habitat (`habitat.py`)

Per line and epoch, a carrying capacity K ∈ [0, 1] per cell: land and ice-free (fliers and swimmers too: they live on land), times soft trapezoids on annual temperature and rain (and elevation if given), times the Köppen / place preferences (prefers ×1.5 capped at 1 after normalising, avoids ×0.25), coast and island bonuses (island = a landmass under 1% of the land, from `grid.components` of that epoch's land). The same inputs exist on all three scales (run keyframes: temperature, rain, climate; time zoom: temperature, climate and rain scaled as in §1; recent pass: all stored).

### Spread (`spread.py`, numba)

The state is a presence p[line, cell] ∈ [0, 1] (share of the habitat held). Per step:

1. **Loss:** p ← min(p, K) (habitat gone, the line is gone there: the ice pushes lines into refugia).
2. **Spread:** "widest-path" passes over the cell graph: a cell can be reached from a neighbour with the neighbour's presence × the cost of entering it (1 for good habitat; ×0.6 for poor land; sea only for swimmers/fliers/seafarers, ×0.55 a cell with a per-line maximum; high relief ×0.7 per 1000 m of rise for walkers). The number of passes per step is the line's speed × step / cell size (default 0.5 km/yr: ~4 cells per 1 kyr at L6), so **at Myr and kyr steps ranges fill whatever is connected** (connectivity-limited, the honest answer at those scales) **and at century steps fronts move** (speed-limited: the recolonisation after an ice age takes centuries to millennia).
3. **Competition:** a line can take only the room the others leave: room = K − Σ α·p_other, α = niche overlap (shared comfort range and Köppen preferences) × 0.9, minus a relatedness discount so sisters compete harder than strangers. Incumbents keep their ground, so ranges meet at fronts (parapatric) instead of everyone being everywhere.
4. **Wishes** (soft): K of a gets ×(1 + 0.3·w·p_b) where a wants to be near b, ×(1 − 0.3·w·p_b) where apart; place wishes (island, coast, mountain, inland) multiply K by 1.3·w on those cells.

### Origins and splits

A **root** is placed at its `appears` time at the cell maximising K × (wish nudge) × seeded Gumbel noise among the top 2% of the planet's land; it starts as the connected suitable patch around that cell, a radius of 3 cells.

A **split** at time T: the child's origin is sought inside the parent's range at T, scored by
- the child's own K there (it arose where its niche was good),
- **isolation** (vicariance): cells in a part of the parent's range cut off from its largest part (an island, a basin behind a sea that rose, a refuge left by the ice) score ×3; else the parent's range edge (low parent presence) ×1.5 (peripatric),
- the wishes (an "island" wish prefers island origins; a "near b" wish prefers origins near b's range),
- seeded noise.

The child starts as a blob of 2–4 cells there and takes the parent's presence in it. The **parent continues** until its last child splits; at that moment its remaining range is shared out among its children by graph-nearest child range (the last split is a vicariance of what is left), so the leaves are what exists at the present. A line with `persists = true` keeps living (an extant stem, e.g. if "humans" were the stem of the mammals).

### Late mixing (the last ~3–1 kyr)

From `mixing_start` (default 3 kyr ago) competition relaxes where people can reach each other: α falls linearly to α × (1 − 0.6) by the present for every pair, except for lines marked `insular`; `seafaring` lines cross straits; `agricultural` lines spread faster in fertile lowland (temperate and subtropical Köppen, rain over 500 mm, ground under 1000 m). Mixing is therefore wherever the graph lets peoples meet — connected lowlands, coasts, straits — and isolation is wherever it doesn't: islands beyond reach, high mountains, deserts.

### Best of N

The whole history is cheap, so `--tries N` (default 4) runs it with N noise seeds and keeps the one that best satisfies the wishes (score in the report). This is the main nudge: the history is never edited after the fact.

## 3. Outputs

- A run of `kind: timezoom`, `meta.phase = "lineages"`, frames at the deep, glacial and recent epochs (time in kyr before present: −8000 … −300 … −30 … 0; the slider is by frame, so the uneven spacing is fine) with the terrain layers of each epoch plus:
  - `peoples`: the dominant line per cell (uint8 index into `meta.lineages`, 255 none),
  - `peoples_mix`: how many lines hold ≥ 25% there (0–n),
  - `peoples_p<k>`: per line presence (0–100%) only at the present frame? No: stored for every frame for the leaves only when cells × frames × leaves stays under 64 MB, else at the present only.
- `meta.lineages`: the tree (ids, names, parents, split times, colours), each origin (cell, lat/lon, epoch, why: isolated / edge / habitat), each line's range by epoch (area in Mkm², centroid), migration paths (centroid track over time), extinctions and refugia.
- `meta.present`: per line area, centroid, main landmasses, neighbours (the lines whose ranges touch it, with border length), mixing zones (connected regions where ≥ 2 lines hold ≥ 25%, with their lines), isolates (a line's separate patches), wish scores.
- `run.txt`: the readable report, with ASCII maps of the present (letters per line).
- **Viewer:** the run opens in the time-zoom UI. New: the **peoples** layer (each line's colour; mixed cells hatched lighter, by `peoples_mix`), **peoples mix**, the hover card's peoples row, the tree panel (lines, splits, origins; click a line to highlight its range; origin marks on the globe).

## 4. Costs (L6, 40,962 cells)

Recent pass: seconds. Lineages: ~15 lines × (~5 deep + ~75 glacial + ~300 recent steps) × a few passes; with numba, seconds per try. Storage ~30–60 MB at L6 (terrain layers dominate).

## 5. Decisions (filed as needs-decision drafts; stage 1 is built on the lean)

1. **Finest pass physics** (`draft-lineages-recent-physics`): A interpolate the time zoom + seeded variability (lean: cheap, consistent with the ice it came from, no physics-lane changes); B re-run the time zoom's ice and climate at 100-yr steps over the window (true century ice, ~10× the cost, owned by the ice lane); C A plus a full climate recompute every 2 kyr on the interpolated surface (better rain, ~1 min at L6).
2. **Parent at a split** (`draft-lineages-parent-split`): A the parent continues until its last child splits, then its range is shared among the children (lean); B the parent always continues (more peoples at the present, more overlap); C every split ends the parent (strict bifurcation, needs binary trees).
3. **How strongly wishes act** (`draft-lineages-wish-strength`): A best of N tries + mild habitat and origin nudges (lean; a wish can fail and says so); B stronger: origins placed to satisfy the wish first, then simulated; C post-hoc range editing (rejected: forcing).
4. **Where results live and how they show** (`draft-lineages-store-kind`): A as time-zoom-kind runs with `meta.phase` (lean: the viewer's time-zoom UI plays them for free; the family tree lists them as time zooms of the planet); B a new store kind `lineages/` with its own viewer tab and family node.
5. Smaller, decided on the lean without drafts: TOML input (stdlib `tomllib`, comments allowed; YAML would add a dependency); no invented lines (vicariance only places the given splits; isolates are reported as candidate sub-peoples); speeds default 0.5 km/yr (Neolithic expansion ~1 km/yr, Ammerman & Cavalli-Sforza 1971; foragers slower).
