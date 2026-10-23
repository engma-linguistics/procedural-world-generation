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

### Owner additions (2026-10-23): origins beyond splits, the editor, switching off, extinctions

Built as follows (the input is a DAG; `planet/lineages/spec.py` has the exact rules):
- `origin`: **root**, **split** (`parents = [p]`), **arrival** from outside the world (elves, gnomes from the feywild; optional `place = [lat, lon]`, else the best habitat, near the other parent of any hybrid it has), **hybrid** of two parents (half-elves, half-orcs; `contact = true`: exists only where both meet, as an overlay; false: founds a people of its own where they meet; waits until they do), **template** (tieflings, aasimar, genasi: an overlay on its hosts from `at`, seeded at `sites` places in their range, spreading only through it, `share` of the hosts' people).
- `enabled = false`: its split children re-parent to its nearest enabled ancestor (or become roots / arrivals), keeping their inherited niche; its hybrids and templates go too. `custom = true` marks user-added lines.
- `extinct = "T"`: the line's habitat dwindles to nothing by T; it shows in the past epochs and its descendants and hybrids live on; a dying side branch doesn't end its parent.
- Preset: `planet/lineages/samples/dnd.toml` (46 lines since the preset lane, editable defaults, one extinct extra: troglodytes).
- Editor: `viewer/lineages.html` (a log time axis over the three scales; drag times; edit, add, switch off, delete; wishes; save / load / download; run on a world and see origins and areas back).

## 3. Outputs

- A run of `kind: timezoom`, `meta.phase = "lineages"`, frames at the deep, glacial and recent epochs (time in kyr before present: −8000 … −300 … −30 … 0; the slider is by frame, so the uneven spacing is fine) with the terrain layers of each epoch plus:
  - `peoples`: the dominant line per cell (uint8 index into `meta.lineages`, 255 none),
  - `peoples_mix`: how many lines hold ≥ 25% there (0–n),
  - `peoples_share` (the leading people's share, %) and `peoples_overlay` (the strongest template or contact hybrid); every line's presence (%) at the present in `layers/presence_present.bin` (lines × cells).
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

## Lane 2 additions (2026-10-23)

### Sea crossings (`planet/lineages/crossing.py`)
Three ways across the sea, all mechanism, none forced:
- **Land bridges**: every epoch's land is that epoch's (the time zoom's surface above its own sea level), so a strait that falls dry at a glacial low stand is walked over by the ordinary spread. The history only names it: the first time a line reaches a present-day landmass it gets an event ("walks over a land bridge to the continent at 12°N 21°W"), or "spreads overland (the land was joined then)" in deep time (the plates moved).
- **Short hops**: unchanged, the spread's per-trait sea factor (swimmers ~3 cells, fliers ~6, seafarers late).
- **Long crossings**: per step and per landmass a line doesn't hold yet, a Poisson chance `1 - exp(-dt x Σ_ways rate x exp(-gap / L) x K_landing)`, the gap being the sea distance from the line's own coast (a sea-only BFS, so island chains are stepping stones). `spec.HOPS`: rafting on drift for everyone (3e-4 /kyr, L 150 km: a few hundred km once in a few Myr, the monkeys across the young Atlantic), coastal canoes (0.01 /kyr, 250 km), swimmers (0.05, 400 km), fliers (0.05, 700 km), seafarers (1 /kyr, 1500 km, the last 6 kyr: Lapita/Polynesian voyages). A landing needs habitat and room.

An empty continent is now a geographic outcome, not a bug: on 119973 the 18 Mkm² continent is ~4300 km of open ocean from everything (36 cells), so walkers and swimmers never get there and seafarers only sometimes do in the last 6 kyr (it was held 0.79 in one try, 0 in others). The summary lists `empty_continents`; an arrival with a `place` puts a people there if wanted.

### Contact corridors and territorial competition
A **contact value** c ∈ [0, 1] per cell and epoch (`crossing.corridor`): river valleys (top 8% of land by the world's flow, glacial and recent epochs) 0.9, coasts 0.8, open lowland 0.5 (upland 0.4), elsewhere 0.3; capped in deep forest (≥ 60% trees, 0.25 off rivers/coasts), deserts away from rivers (0.2), mountains (0.15, 0.4 along rivers), islands (0.3), ice (0.1).
Competition: `alpha_eff = alpha + (1 - c) x (ALPHA_CLOSED - alpha) x same_way`, ALPHA_CLOSED = 1.4, same_way = 0.5 per difference in flies / swims / mountain / coastal / subterranean. Lotka–Volterra-like: under 1 peoples settle side by side, over 1 the larger excludes (closed country keeps one people; peoples with different ways of life share it). A people held above its room declines toward it (e-folding 1 kyr: **displacement**, which lane 1 lacked: there, once shared a cell stayed shared forever). Late mixing relaxes competition in proportion to c (`1 - 0.6 x ramp x mix x c`), so it concentrates in corridors; farmers' push (agricultural, last 6 kyr) acts only on farmland (temperate/subtropical, savanna and warm continental, rain > 500 mm, under 1000 m).
Safeguards, both from the spec rather than metric-chasing: a split's founders hold the suitable country within 400 km of the origin (or the whole cut-off part they arose in), not 2–4 cells; and a line the tree says lives at the present doesn't die out: below 0.5 Mkm² displacement stops, and at < 3 cells it holds a refuge at its best habitat near where it was (an event).

### Wishes
Place wishes score half "how much of that kind of place the line holds" (half of it is full marks) and half "how much of its range is there against how common the place is". New place kinds: `jungle`, `steppe`, `desert`, `tundra`, `island_chain` (islands with another landmass within 4 cells), plus `farmland` as a tag.

### Output additions
`meta.lineages[].reached` (present-day landmass → first arrival: when, how, gap), `crossings`, `story` (game-ready sentences); `meta.present.mixing` (area, land share, corridor/closed shares), `landmasses` (held share), `empty_continents`, `lost`, `stories`. Viewer: origins and centroid tracks on the globe (overlay "Peoples' origins and tracks"), a `peoples overlay` layer (templates, contact hybrids), the hover card's peoples rows (this frame; every people's share at the present), the story of a picked people in the panel. Server: `POST /api/lineages` is a job (`api.lineages_job`), polled at `/api/jobs/<id>`; peoples and recent runs nest under their time zoom in the family tree.

## Lane 3 additions (2026-10-23)

- **Speed.** L7 is ~4x faster with the same outputs: 265 s → 63 s a try on 1144ce, side by side. How:
  - The spread visits only the front: the neighbours of the cells that changed in the pass before.
  - Competition is summed in numba over a line's rivals, on the cells where it can hold ground (K ≥ EST).
  - The habitat is worked out on land cells only.
  - Neighbour reductions use `reduceat`.
  - Island chains are tagged only when named.
- **Near wishes** (`History._wish_near`). A near wish:
  - pulls the habitat toward the other people's border, ×(1 + 0.5 w) just outside its range, e-folding over 300 km (`NEAR_KM`), not into it;
  - pulls whichever origin comes second toward the other people, ×(1 + 2 w), e-folding over 1000 km;
  - halves the competition between the two (`NEAR_TOLERANCE`).

  The near score counts a's range within 330 km of b's (`NEAR_SCORE_KM`) at any grid level.
- **Shelf corridors.** Land of a glacial or recent epoch that is sea at the present has a contact value of at least 0.7 (`crossing.SHELF_CONTACT`).
- **Best of N** takes 0.05 off a try's score for each living line it lost (`LOST_PENALTY`).
- Showcase: `docs/review/lineages/showcase-3.md`.

## Lane 4 additions (2026-10-23)

- **Contact hybrids linger (PW-613, lean B).** `History._hybrid`. Where its parents meet, a contact hybrid is a share of their people, as before, and it can keep growing there. Once it has appeared:
  - where its parents no longer meet, it fades within its own habitat (e-folding `LINGER_KYR` = 10 kyr);
  - where they last met, it lives on as a small people of its own, at least `LINGER_MIN` (0.3) of its habitat;
  - cells it holds on its own count on the `peoples` layer as its own people, not as an overlay. `meta.present.lines[id].own_mkm2` gives their area;
  - the first parting is an event ("half-elves live on as a people of their own where humans and elves last met"), and the story tells it if the parents are still apart at the present.
- **Preset (PW-614, lean B).** The wish "goblin near orc" is now "hobgoblin near orc", the usual pairing of hobgoblin and orc warbands: savanna borders steppe. Goblins keep the jungle wish.
- **Land use: the world's game layers in the habitat** (`planet/lineages/land.py`, spec `[[use]]`, meta `land_pull`).
  - **Goods.** `land.goods(world)` makes 0..1 goods per cell from the world's layers:
    - living goods: `fertile` (humanuse), `grazing`, `foraging`, `timber`, `fuel`, `building` (gameattrs). Each is scaled to this world's own best (the 95th percentile of the land that has any). A living good on under 2% of the land is left out as missing, e.g. pasture on worlds whose plants have no grasses;
    - geology: `stone` (resources.stone: granite and marble best), `metal`, `gold`, `iron`, `copper`, `tin`, `gems`, `mithril` (the fantasy ores), `coal` (res_* likelihoods);
    - coasts: `harbour` and `nav_hazard` (from the sea cells, carried to the coast), `coral`, `lagoon` (barrier islands), `mangrove`, `cliff`, `seabirds`, `seals` (coastform).

    Point-like goods (ores, coasts) reach one cell ring inland at 0.7 of their value. A world without the resource or coast layers (they are add-on commands) gets them worked out in memory, never written to the world. That is ~10 s at L7 with the run's history, once per run.
  - **Uses.** `[[use]] by = <trait or place/climate tag in prefers>, good = <good>, weight = w` (w < 0 avoids). The editor has a "Land use" table and a "land pull" field. The preset:

    | way of life | goods |
    |---|---|
    | agricultural | fertile |
    | nomadic | grazing |
    | forest | timber, foraging |
    | rainforest | foraging |
    | miner (new trait: dwarves, gnomes) | gold, iron, gems, mithril |
    | subterranean | stone, metal |
    | seafaring | harbour (+), nav_hazard (−0.7) |
    | coastal (tortles, sea elves, tritons) | coral, lagoon |
    | wetland | mangrove |
    | flies (aarakocra, the avian stem) | cliff, seabirds |
  - **Habitat.** `History._land_mult` multiplies K by (1 − pull + pull G):
    - G is the best of the line's favoured goods in the cell, each by weight ÷ the largest weight. A people favours any of its goods, so farmland or a harbour, not both;
    - the multiplier is normalised to a mean of 1 over the line's own country (today's habitat). The goods move a people within its niche without making it a weaker people overall: a rare good like a coral coast lifts its few places instead of cutting everywhere else;
    - each avoided good multiplies K by (1 − pull |w| g);
    - pull is 0.5 by default (`meta.land_pull`).

    Timing: the land use is off in the deep epochs (the plates have moved since). Before `HOLOCENE_KYR` (10 kyr ago) only the geology counts, because the farmland, pasture, forests and coasts are today's. The dwarves' origin (500 kyr) is therefore already drawn toward the ores.
  - **Homeland notes.** `land.homeland_notes` adds one or two sentences per people to its story: what its land (presence ≥ 25%) gives it, for the goods its way of life looks for. Ores, harbours, coral and seabird coasts are counted as districts (connected cells ≥ 0.5): "the dwarves hold two of the world's five richest gold districts (the best in the 2,000 km mountain range at 9°N 39°W)". Area goods are a share of the world's best: "the humans hold 31% of the world's best farmland (…)". The world has no place names, so the notes name the nearest highlight feature that covers the place (`highlights.find`: mountain ranges, plateaus, great forests, deserts and so on), or else give directions. Stored in `meta.present.homeland`.
- Showcase: `docs/review/lineages/showcase-4.md`.

## Preset lane (2026-10-24): the owner's D&D tree

- **Intermediate stems**, as with real hominids:
  - draconic stem (3 Myr) → kobolds, dragonborn;
  - feline stem (4 Myr) → tabaxi (1.2 Myr), leonin (900 kyr);
  - goblinoid stem → goblins, and the greater goblinoid stem (600 kyr) → hobgoblins, bugbears;
  - archaic humans stem (400 kyr) → humans (200 kyr), halflings (100 kyr).
- **Giants.** The elder giants are gone. The giant-kin stem (1.5 Myr) → goliaths, firbolgs and the true giants stem (1.2 Myr), which splits into:
  - hill giants (900 kyr);
  - sky giants stem (800 kyr) → cloud giants (400 kyr), storm giants (300 kyr);
  - elemental giants stem (700 kyr) → frost giants (350 kyr), fire giants (250 kyr).

  All five live today, as rare insular peoples with narrow niches.
- **New goods** (`land.goods`):
  - `volcanic`: the world's volcano table, active 1, extinct exp(−age / 3 Myr), young arc and hotspot ground ≥ 0.5;
  - `hills`: moderate relief under the mountains, the steepest rise to a neighbour 1.5–14 m/km on ground 100–1900 m;
  - `peaks`: ground 2000→3500 m;
  - `frost`: permafrost and the ice's edge, today's only;
  - `storm_coast`: wave power offshore, today's only.
- **New place tags:** `volcanic` (glacial and recent epochs only) and `hills`.
- **`[[use]]` changes.** `by` may name one line's id, and an optional `pull` (0..1) overrides `meta.land_pull`; a line takes the strongest pull of its favoured goods. `strict = true` cuts the habitat off the goods to 1 − pull instead of renormalising it to a mean of 1. The preset gives each true giant its own good at pull 0.85, strict. On run e8cc18 (1df1c3) the giants hold 0.01–3.7 Mkm² each (frost giants the most); humans hold ~20.
- **New wishes:** leonin on open country; frost giants apart from fire giants.


## Workbench lane (2026-10-24): demography, explorers and seafarers, the multi-tab workbench (PW-650)

The owner: giants far fewer, with larger roaming areas; some peoples insular, some exploratory; landmasses with
few or no peoples found by the explorers and seafarers ("not 'no dwarves sail the seas', but a smaller
proportion"); peoples as a multi-tab thing of their own.

### Four knobs per people (`spec.DEMOGRAPHY`, `Lineage.demo`)
Each can be given on a `[[lineage]]`; left out, a split inherits its parent's given value, else the value comes
from the traits (the strongest among them; `insular` sets exploration and insularity whatever else).

| knob | meaning | default (no traits) | from traits |
|---|---|---|---|
| `density` (or `band_km2`) | people per km² of full habitat; a band of 25 roams 25 / density km² | 2 | agricultural 10, coastal / miner / subterranean 3, nomadic / flies 0.6 |
| `explore` 0..1 | how readily the frontier pushes into marginal land and over the sea | 0.5 | seafaring / nomadic / cosmopolitan 0.7, flies 0.65, subterranean 0.35, insular 0.25 |
| `sea_share` 0..1 | the share of the frontier that tries water crossings | 0.03 | seafaring 0.6, swims 0.4, coastal 0.3 |
| `insularity` 0..1 | resistance to mixing and to leaving home | 0.5 | insular 0.85, cosmopolitan 0.2 |

`speed_kmyr` stays the expansion rate (km/yr of frontier; `expansion_kmyr` is accepted as a synonym).

What they do (all cheap, on the existing frontier model):
- **density**:
  - **numbers**: a people's population is Σ presence × density × cell area (`History.population`). An overlay is its share of its hosts' people. Per people and per present-day landmass, in `meta.present.lines[id].population` and `by_landmass`, and per stored frame in `stats.population`.
  - **viable population**: a separate patch of a people's land with fewer than `meta.viable_pop` (500) people fades, e-folding 2 kyr (`History._viable`, looked at about once a kyr). The largest patch is exempt: a people's last land is the refuge logic's. So a sparse people needs a big piece of good country to hold a land at all. Giants at 0.005–0.01 /km² need ~0.1–0.2 Mkm² of full habitat; humans need a few cells.
  - **competition**: the competition a line feels from a rival is × (the rival's density / its own)^0.1, within 0.7..1.4 (`DENSITY_PUSH`). Mild on purpose: at ^0.25, within 0.5..2, the elves and orcs lost most of their land to the humans in single tries on 1df1c3.
- **explore**:
  - into marginal land (K < 0.3) the spread's pressure keeps a + (1 − a) K / 0.3, with a = 0.25 + 0.5 explore. It was 0.5 for everyone, which is the default explore of 0.5;
  - every long-crossing way but the drift raft is × 2 explore × (1.25 − 0.5 insularity) (`crossing.hop_mult`).
- **sea_share**:
  - boats (the crossing way `seafaring`, `spec.BOATS`): rate 1 /kyr × share / 0.6, reach from 300 km (share 0) to 1500 km (0.6 or more), from 6 kyr ago. Humans at 0.6 sail as the old `seafaring` trait did. Dwarves at 0.05 put to sea ~12× less often and less far, but not never;
  - short hops over straits from 3 kyr ago, for a share ≥ 0.2: sea factor 0.75 × (share / 0.6)^0.5.
  - The `seafaring` trait's movement knob (`late_sea`) is gone: the trait now sets the share (0.6) and still names the harbour use.
- **insularity**:
  - the late relaxing of competition is × 2 (1 − insularity). This replaces the `insular` and `cosmopolitan` traits' `mix` knob: 0.85 → 0.3 (was 0.2), 0.2 → 1.6, 0.5 → 1;
  - the long crossings, as above.

### Landmasses: discovery and numbers
Per present-day landmass, `meta.present.landmasses[]`:
- `discovered`: the first native people there, its origin included (`by`, `ago_kyr`, `how`, `gap_km`);
- `settled_by`: the first of today's peoples, since the stems found most land in deep time;
- `arrivals`: the first 12 arrivals;
- `population`: per people.

`run.txt` gains "Numbers at the present" and "Landmasses: who found them first". `meta.present.ascii` holds the present-day map (letters per people) for the workbench.

### The preset
| people | density /km² | explore | sea share | insularity |
|---|---|---|---|---|
| true giants (stem, hill, cloud, storm, frost, fire) | 0.005–0.01 | 0.3 (storm 0.45) | 0.02 (storm 0.5) | 0.85 |
| goliaths, firbolgs | 0.15, 0.3 | 0.4, 0.3 | – | 0.7, 0.8 |
| humans, halflings | 10, 12 | 0.55, 0.35 | 0.6, 0.1 | 0.3, 0.4 |
| elves, sea elves, drow | 1, 1.5, 2 | 0.8, 0.8, 0.4 | 0.3, 0.85, 0.02 | 0.7, 0.7, 0.9 |
| dwarves, gnomes | 4, 3 | 0.35, 0.5 | 0.05, 0.1 | 0.75, – |
| tortles, tritons | 1, 1 | 0.7, 0.6 | 0.8, 0.9 | –, 0.8 |
| goblins, hobgoblins, bugbears, kobolds | 5, 4, 0.8, 4 | –, 0.6, 0.4, – | – | – |

PW-655: the giants' uses are now pull 0.7, not strict. The giants are rare through density (numbers in the hundreds to thousands) and the viable population (one land each), not a cut habitat.

### The workbench (`viewer/lineages.html`, same URL; tabs keep `#tree`, `#peoples`, `#places`, `#wishes`, `#results`)
- **Tree & timeline**: the editor as before, with a Demography block in the side panel.
- **Peoples**: a table of every line: on/off, origin, time, habitat, prefers, traits, density / band km², expansion, explore, sea share, insularity, and the last run's population, area and patches. Empty fields show the value used (from the traits or the parent) in grey; headings sort.
- **Places & land use**: the `[[use]]` table (by, good, weight, pull, strict, which peoples it applies to), the land pull, the goods and place tags, and the last run's homeland notes.
- **Wishes**: the wishes with the last run's score per wish.
- **Results**: pick any peoples run. It shows:
  - totals;
  - peoples today (population, density, area, patches, main lands);
  - a discovery timeline (log time, a dot per arrival) and table per landmass;
  - the present-day map (coloured letters);
  - mixing zones, wish scores, stories (with numbers);
  - links to the globe and to `run.txt`.

No server change: the page uses the existing `/api/lineage-tree(s)`, `/api/lineages` and the store's `runs/index.json`.

### Groups within a people (PW-665; built by the groups lane, 2026-10-24)
As built (the design follows below; where they differ, this wins):
- **Spec.** `origin = "group"`, `group_of = <people>` (`at` defaults to `spec.GROUP_KYR` = 6 kyr). It inherits what it leaves out, demography too, as a split does. It is never a split child, so it never ends its people. A group of a group, template or contact hybrid is refused. Switching a people off switches its groups off. `Tree.groups_of`, `Tree.people_of`.
- **Appearance** (`History._group_origin`). At `at`, a group takes up every cell of its people's range where its own habitat beats its people's by `GROUP_MARGIN` (0.15). The comparison is unclipped, so prime land for both still tells them apart. It takes half the people's presence there. Its origin (the event and story) is the cell of the largest advantage, with founders within `FOUNDER_KM` around it. Without such land, it starts at its people's range edge.
  - Taking every such cell is divergence in place. At first only the founders' blob was seeded, and the groups stayed speed-limited: seafarers held 58–193 cells after 6 kyr.
- **Mixing.** A group, its people and its sister groups compete at `GROUP_KIN` (0.5) × their niche overlap, with no closed-country term.
  - A near wish naming a people tolerates its groups too.
  - Hybrids, templates' hosts and near / apart wishes see a people as a whole (`History.whole`: its presence plus its groups', at most 1). So half-orcs appear where steppe orcs meet human herders.
- **Outputs.**
  - A group is a line of its own: row, story, population, homeland notes.
  - `meta.present.peoples[<people>]`: the people as a whole (joint area and patches, population, by landmass, each part's share). `meta.present.lines[g].group_of`; `meta.lineages[].group_of` and `groups`.
  - Mixing (zones, `peoples_mix`) counts peoples as wholes, so a people mixing with its own groups is not a mix.
  - New layer `peoples_whole`: the leading people as a whole.
  - A group's colour is a tint of its people's (`output.tint`).
  - Stories: "Steppe orcs became a way of life among the orcs ~9 kyr ago…", and the people's story ends with the whole: "…the humans are 200 million in 31 Mkm²; 72% keep the old ways".
  - `run.txt` gets "Peoples with their groups".
- **Workbench.**
  - Peoples tab: ▸ opens a people's groups (indented); "+ group" adds one; population and area also show "all".
  - Side panel: a group's own knobs, "Its land use" (the `[[use]]` rows that apply to it) and its wishes; a people lists its groups.
  - Results: a people's "all" row with its groups beneath, each with its share.
- **Globe.** The peoples panel lists groups under their people, with a checkbox "peoples as wholes (not by group)" (`&peopleswhole=1`), which draws the `peoples_whole` layer.
- **Preset.**
  - orcs → steppe orcs (steppe, grazing pull 0.75), forest orcs (forest, cold, density 2, insular-ish);
  - humans → farmers (fertile pull 0.75, density 12), herders (open / hills / steppe, grazing), nomads (nomadic, steppe / desert, density 0.8), seafarers (coast / island, sea share 0.85, harbour pull 0.75);
  - dwarves → hill dwarves (hills, density 6).
- **Runs** (L7, 2 tries; ~123 s a try, about as before). Shares are of each group's land at ≥25% presence; the world's land in brackets.

  | | 1df1c3: 8bac4d (was 37e9da) | 3e9e7d: c646ea (was 33b1c3) |
  |---|---|---|
  | wish score | 0.715 (0.72) | 0.687 (0.687) |
  | orc steppe wish | 0.587 (0.602) | 0.251 (0.152) |
  | steppe orcs | 1.1 Mkm² thin (no land ≥25%: the orcs already hold the steppe there, 88%) | 0.56 Mkm², 97% steppe (8%) |
  | forest orcs | 0.52 Mkm², 88% forest | 0.06 Mkm², 100% forest |
  | human seafarers | 1.06 Mkm², 100% coast (7%), 9% island (1%), 2–7 kyr crossings up to 2,500 km | 1.56 Mkm², 100% coast (10%), 15% island |
  | human farmers | 11.9 Mkm², 91% farmland (39%) | 18.6 Mkm² |
  | human herders | 5.4 Mkm², 96% open (33%) | 13.0 Mkm², 91% open, 45% steppe |
  | human nomads | 5.3 Mkm², 65% desert (14%) | 12.6 Mkm², 29% steppe, 33% desert |
  | hill dwarves | 0.67 Mkm², 99% hills (18%) | 0.36 Mkm², 84% hills |
  | humans, all | 198 M; old ways 72%, farmers 24%, herders 2.5%, seafarers 0.8%, nomads 0.9% | 273 M; 67 / 27 / 3.8 / 0.7 / 1.4% |

  Screenshots: `docs/review/lineages/groups-*.png`. How large a share takes up a way of life is a judgement call (inbox draft-peoples-group-shares).

### The groups design (owner, 2026-10-24)
The owner's idea: groups within a people are cultures, not subspecies. Examples: steppe orcs and forest orcs;
human seafarers, farmers and nomads. Each group shares its people's ancestry and identity, but has its own way
of life: habitat niche, traits, demography (sea share, density…), land use and wishes. So it settles and
spreads as a range of its own.

Proposed model:
- **Spec.** A new origin kind, `origin = "group"`, `group_of = "<people>"`, `at` (default `mixing_start` or 6 kyr), plus any niche, trait, demography, use or wish fields.
  - What a group leaves out comes from its people, as for a split.
  - It is a row of its own, so the Tree and Peoples tabs, wishes and `[[use]] by = <id>` work unchanged.
  - Alternative input: a `groups = [{…}]` list under the people, flattened by `spec.parse`.
- **Appearance.** By divergence, not a split. At `at`, the group takes the cells of its people's range where the group's own capacity K beats the people's by a margin (its niche exists there), seeded as a split's founders. Without such cells, it is placed at the people's range edge with the best K_group.
  - The people does not end: groups never end their parent, like `persists`.
- **Mixing.** A group and its people, and sister groups, compete as kin with no closed-country exclusion: `terr = 0`, α × 0.5. So they mix freely where their niches overlap, and no hybrid is needed.
  - Against other peoples, each group competes with its own niche and density.
- **Outputs.**
  - Each group keeps its own presence row, layer index, story and population.
  - Summaries add a `people` roll-up: the people's own row plus its groups' rows, for area, population, landmasses and wish scores naming the people.
  - The `peoples` map layer shows the group's colour, a tint of its people's colour.
- **Workbench.** Peoples tab: a people's row expands to its groups (indented, "+ group" button). Results: a people row with its groups beneath. Stories: "the steppe orcs, a way of life among the orcs since ~4 kyr ago, …".
- **Preset examples.**
  - orcs → `steppe_orc` (nomadic, steppe, grazing) and `forest_orc` (forest, timber, density 2, insular);
  - humans → `human_seafarer` (coastal, sea share 0.8, harbour), `human_farmer` (agricultural, fertile, density 12), `human_nomad` (nomadic, steppe, density 0.8, explore 0.7).
- **Cost.** A group is a line in the loop. Six groups add ~15% runtime at L7.
- **Scope: shallow on purpose** (owner, 2026-10-24). A group is "culture instead of genetics" only as far
  as a way of life goes: habitat niche, traits, land use and wishes within a people. No languages,
  religions, customs, cultural spread or assimilation, or effects of culture on peoples: those belong to the
  civilization-simulation epic PW-661. Model and UI stay minimal: a row per group, an expandable row in the
  Peoples tab, roll-ups in the results.

## Peoples change the land (PW-662, built 2026-10-24)
As built (`planet/lineages/landuse.py`, `planet landuse RUN`; `planet lineages` runs it on every run with a world):
- **No names.** A line's way of life is the weights its `[[use]]` rows (traits, preferred places, own id) put on the goods that feed a people: `fertile` is farming, `grazing` herding, `timber` (and 0.3 x `foraging`) woodland; the shares are of those weights. Miners, flyers, seafarers' harbours and the like add nothing. Numbers are presence at the present x the line's density x cell area (overlays are shares of their hosts and are skipped; the total is ~5% under `meta.present` because lingering hybrids are left out).
- **Per cell** (people per km² by way of life, the world's own farmland class 0..4 and grazing good, the present's tree cover):
  - cropland: farming people x 0.007 km² / yield of the class (0.55 marginal, 0.8 fair, 1 good, 1.15 prime), capped by class (35 / 60 / 85 / 95% of the cell);
  - pasture: herding people x 0.15 km² plus 0.01 km² of meadow per farming person, on grazing land outside the fields;
  - burned grassland: herding people x 0.10 km² of woodland margin on grazing land;
  - managed woods: every person 0.003 km² for fuel, timber users 0.03 km² more x their share, out of the trees left (canopy thinned by 30%);
  - settlement density: all people per km²; tree cover left after all of it.
- **Stored** as static files on the run, not per frame: `layers/anthro_{crop,pasture,burned,managed,people,tree_after}.bin` (uint8, one value per cell, `people` log2p1), described in `meta.anthro` with the summary. `run.txt` ends with "Peoples change the land". `planet landuse RUN` redoes it in place.
- **Viewer** (peoples runs): a "land use" colour layer (wild tree cover with cropland, pasture, burned grass, managed woods and dense settlement over it), a "show cleared land (present)" checkbox in the Peoples panel that tints the tree-cover (and vegetation / satellite, where a run has them) colours, a hover line, `&anthro=0`. Only the last frame, the present, shows it. Screenshots: `docs/review/lineages/anthro-*.png`.
- **Numbers** (L7, runs d489d0 on 1df1c3 and 7709bf on 3e9e7d; the same draws as 8bac4d and c646ea, so the peoples are unchanged):

  | | 1df1c3 (d489d0) | 3e9e7d (7709bf) |
  |---|---|---|
  | people (farming / herding) | 329 M (246 M / 8 M) | 358 M (262 M / 15 M) |
  | land; fair-to-prime farmland | 188; 48 Mkm² | 169; 43 Mkm² |
  | cropland | 1.37 Mkm² = 0.7% of the land, 1.1% of the farmland (0.51 Mkm² of it on it) | 2.21 Mkm² = 1.3%, 2.2% (0.94) |
  | pasture / burned grass / managed woods | 2.34 / 0.02 / 0.68 Mkm² | 3.93 / 0.10 / 0.89 Mkm² |
  | tree cover | 57.2 -> 56.4 Mkm² (-1.5%) | 60.1 -> 58.6 Mkm² (-2.5%) |
  | densest cell | 22 people/km², 24% cropland | 22 people/km², 23% cropland |

  Against Earth's pre-industrial range (plausibility, not a target): ~300 M people c. 1000 AD farmed ~2-3 Mkm² (~1.5-2% of the land), ~1700 AD ~4 Mkm² (~3%); pasture and range ~8-15 Mkm²; ~3-5% of the forest was gone by 1000 AD. So cropland is in range for the population, pasture and forest loss are at or under its low end (few herders: 8-15 M, and the peoples' densities top out near 20 /km² where Earth's farmed plains reached 30-100). Clearing here is population-limited, which is the `density` knobs' call (draft-anthro-land-per-person).
- **Not built:** history (soil exhaustion, collapse, war) is PW-661's.

### The cleared land on a finished world and on a regional zoom (PW-669, PW-667)
As built:
- **A finished world's satellite (PW-669, `viewer/index.html`):** opening a world looks in `runs/index.json` for its newest peoples run (`phase: lineages`, `world` = the world id; `&peoples=RUN` picks one, `&peoples=0` turns it off), reads that run's `anthro_*.bin` on the fly (same cells; nothing is written into the world) and tints the world's `satellite`, `vegetation` and `biome` colours with the run view's `anthroTint`. The world summary has a "show cleared land" checkbox and the run's numbers, the legend names the run, hover adds the cell's land use. A world without a peoples run shows neither. Screenshots: `docs/review/lineages/anthro-world-1df1c3-satellite-tinted.png` against `...-wild.png` (run d489d0 on 1df1c3: the farming peoples' country in orange and pasture green across the southern continent).
- **A zoom with the peoples' land (PW-667, `planet/zoom_peoples.py`):** `planet zoom WORLD --lat L --lon L [--size-km --res-km] --peoples RUN` (RUN: a peoples run of that world with `meta.anthro`). It is a zoom of its own (its id carries the run; the same arguments without `--peoples` give the old zoom, byte for byte: layers and PNGs checked against the code before this change), with a `land_use` layer (0 wild, 1 cropland, 2 pasture, 3 burned grass, 4 managed woods, 5 settlement), `meta.peoples` (run, km² of each use, tree cover before and after) and the viewer layer "Peoples' land". The run's cell fractions (and people per km²) are Gaussian-interpolated to the pixels (land cells only), then in each coarse cell the best ground takes the cell's share, so each cell keeps the run's cropland, pasture, burned and managed share of its land (capped by what the ground allows):
  - **cropland** the best arable pixels first: the zoom's `fertile_score` (>= 0.12), flat ground (none above tan 0.18, ~10 degrees), nearness to a river (a floodplain: exp(-km/6)), and a 12 km noise, so fields lie in veins along the rivers and valley floors, not as speckle;
  - **settlements** a village to every 1,000 people (one pixel; at most 3% of a cell's land, only where people >= 0.3/km²), drawn at random with odds by site: rivers, harbours near the coast, passes, flat fertile ground; villages are dots, not a ribbon along each river;
  - **pasture** gentle, open ground round the fields and villages (8 km) and what the fire noise opens; **burned grass** fire patches (18 km noise) in woods still standing (tree cover >= 20%); **managed woods** woods near the farmed and settled country and rivers, canopy thinned by `landuse.THIN` (30%), stand height x 0.55 (age reset).
  - **The plants follow:** the plant-type fractions lose trees (cropland 97%, pasture 80%, burned 90%, a village 95%) and shrubs (90 / 40 / 70 / 95%) into the herbs (crop grass where the pixel had none), a village keeps a quarter of its plants, a managed wood 70% of its trees; tree cover, plant cover (a field 80%, a village 25%), leaf area, npp, canopy height (a cleared pixel 0.5 m, a field 1 m), fire return (burned 3 yr, fields and villages none), the named type (cleared woods become that climate's open type: tropical grassland, steppe or prairie, parkland, maquis; a thinned wood stays) and the biome change with them, and the game layers and the satellite are made from the new plants. The satellite (`satellite._landuse`) paints a field per 3 km parcel (ploughed earth, green crop, ripe gold; stubble and bare earth out of season), pasture, burned ground and village ground over the plants. `planet satellite` / `add_game` redo a peoples zoom with the overlay (`zoom_vegetation.fractions` applies it again).
  - **Demo:** zoom 859e74 (world 1df1c3, run d489d0, -36, 104, 1000 km @ 2 km): cropland 112,500 km² (11% of the land), pasture 143,600, managed woods 22,100, burned grass 600, villages 7,600 px; screenshots `docs/review/lineages/anthro-zoom-859e74-satellite.png` (against `anthro-zoom-wild-satellite.png`, the same place without peoples) and `anthro-zoom-859e74-landuse.png`.
  - **Not built** (drafts): fine zooms of a peoples zoom (they start from the wild plants), making one from the viewer or the API, soils and the game layers' reading of land use, named 'cropland' / 'pasture' vegetation types, more world views and a run picker (PW-669).

### Empty land at the present, and the D&D enmities (PW-677, PW-678; built 2026-10-24)
As built:
- **Measure.** Habitable land = ice-free present land where some living people's own habitat K >= 0.25 (before competition); unpeopled = no native people at presence >= 0.12. Runs d489d0 (world 1df1c3) and 7709bf (3e9e7d), the same draws re-run with tries 2: 35.7% and 30.4% of the habitable land empty (31.9% / 21.0% of the land warmer than 0 C; the rest is polar and frost-giant-only country). 42.5 N -113.3 (437 m, a good cell for eight peoples) was empty on d489d0 because its landmass held only kobolds.
- **Cause 1: a stem's cut-off stock vanished at its end (`History._end_parent`).** A stem (mammalian, hominid, archaic humans...) spreads over several landmasses in deep time; its children arise on one of them. At the stem's end its range was shared among the children only through land joined to a child's range (a BFS through the stem's own cells), so every other landmass the stem held lost its people with it, and the children had to cross the sea again. Now a part cut off from every child goes whole to the child whose habitat suits it best (mean K over the part), where that child can live at all. No cell is painted: it is the stem's own population, relabelled as its descendant.
- **Cause 2: no canoes before the voyages.** A people without a swimming or flying trait reached another landmass only by the raft (3e-4 per kyr, 150 km) until the boats at 6 kyr ago, so modern peoples that had existed for 100-200 kyr sat on one continent and filled the others in the last 6 kyr. Now from `spec.CANOES_KYR` = 60 kyr ago (Sahul) a people with a sea share crosses the way boats do but with the short reach only (`BOATS[1]` = 300 km) until the voyages open the long reach; rates and the sea-share scaling are unchanged (so 600-1300 km gaps still wait for boats, and low-explore, insular or landlocked-minded peoples cross rarely).
- **Rejected:** a canoe/paddle way for every people (`HOPS['paddle']`, L 250 km): it got the stems across in deep time but not the modern peoples, and raised the empty share.
- **Numbers (L7, two tries each, same seeds; habitable land empty / of it warmer than 0 C):** 1df1c3 35.7% / 31.9% -> 19.9% / 11.8% (run 7bc9ed); 3e9e7d 30.4% / 21.0% -> 19.7% / 4.7% (run 53b9c1). What is still empty is mostly cold (T < 5 C, 18 of the 26 Mkm2 on 1df1c3): frost giants, goliaths and dwarves are the only peoples with a niche there and they are sparse and insular; the Greenland-like and the south-polar lands. 3e9e7d keeps 68% of its 7 Mkm2 north-Atlantic continent empty (no crossing reached it).
- **Wishes (PW-678).** `dnd.toml` goes from 11 to 38 wishes: 20 'apart' pairs (humans from goblins, lizardfolk, bugbears, kobolds, drow, hill giants; elves from orcs, goblins, hobgoblins and drow; dwarves from orcs, drow, goblins and hill giants; halflings from bugbears, goblins and orcs; gnomes from kobolds and goblins; firbolgs from orcs; aarakocra from kenku; tabaxi from orcs; lizardfolk from sea elves), one 'near' (kobolds by dragonborn) and three fire-giant 'near' wishes (hobgoblins, dwarves, humans: warlords by the peoples they rule, weight 1; at 0.5 their habitat of the fire mountains outweighed the nudge and all scored 0). 'apart' is one-directional (a's habitat is cut where b lives), so a is the people with more to lose; human-elf and human-orc stay unwished because the half-elves and half-orcs need them to meet. Most apart pairs are met by default (niches rarely overlap), so the average rises when they are added: the old 11 alone score 0.827 / 0.694 in the new runs (0.715 / 0.687 before; 0.82 / 0.691 with the model fixes and the old wishes), all 38 score 0.782 / 0.799, the 27 new ones 0.755 / 0.861. The fire-giant wishes are met in 1 of 3 (1df1c3) and 2 of 3 (3e9e7d).

### Filling the land: pioneers, arctic hunters, mutual 'apart' (PW-684, PW-683, PW-682; built 2026-10-24)
As built (measured on 1df1c3 and 3e9e7d, tries 0-3 as single tries, "empty" = PW-677's definition, ice excluded):
- **Cause (PW-683/684): a crowded people could not push into empty country.** The spread carried a people's own presence p as pressure, and p at its border is the competition-thinned room, so a people squeezed at home lost the pressure in 1-3 cells of any hostile ground and never reached empty good land that other peoples' country (or a range, or the old ice) separated it from. Now `History.run` runs a second spread (`PIONEER_P` = 1.0) for every non-overlay people outside the deep epochs, from pressure max(p, min(K, 1)) on its held cells, and takes up only cells nobody holds (`taken`), so the new ground is settled at the habitat's own pressure. Settled peoples and their ranges are not touched.
- **Cold land (PW-684).** Only sparse, insular peoples had a niche below 5 C. New group `human_arctic` of the humans (30 kyr ago, -14..8 C, 0.3 /km², sea share 0.5: kayaks and skin boats, the Thule and Inuit). Groups now go on arising after their origin (`History._diverge`, about each kyr): wherever the people is and the group's habitat beats its people's by GROUP_MARGIN, half the people go over to it. Without this a people that crossed to a cold coast after the group's time lived there as plain humans with K near zero and the landing died.
- **Far landmasses (PW-683): the rates are plausible, no change.** A people with sea share s crosses a gap g at rate 1.0 x s/0.6 x m x exp(-g / L) per kyr (L 300 km until the voyages 6 kyr ago). Humans (s 0.6): 0.16 /kyr at 600 km, 0.04 at 1,000 km over the 54 kyr of canoes, then 0.5 /kyr at 1,300 km in the last 6 kyr; dwarves and orcs (s 0.03-0.05): 0.007 /kyr at 600 km, nothing beyond. That is Earth's pattern (Sahul over ~100 km gaps ~50-65 kyr ago, Remote Oceania ~3 kyr ago); land-bound peoples staying put is the design. What had left far land empty was the pioneer pressure above and, on the 7 Mkm2 north-Atlantic continent of 3e9e7d (1,564 km from the nearest home), landings by peoples with no niche in the cold.
- **'apart' (PW-682).** It now cuts both peoples (b where a lives too). Its score is against the niches: the share of a's habitat (K >= 0.25, its groups' too) within 330 km of b's habitat is the baseline, the score is 1 - closeness / baseline (0..1), and a pair whose baseline is under `APART_CONTESTED` (0.1) isn't counted (36 of 37 pairs are contested in the D&D preset: the habitats overlap widely, so the old 1 - closeness was high only because the ranges were small). `wish_score_raw` keeps the old average; the run page lists the baseline per wish.
- **Numbers (single tries, seeds 0-3; empty share of habitable land / of it warmer than 0 C / of land below 5 C), before = the new code with `PIONEER_P` = 0 and no arctic group:** 1df1c3 25.4% / 16.6% / 72% -> 15.2% / 11.8% / 36%; 3e9e7d 22.4% / 10.1% / 62% -> 5.3% / 2.6% / 14%. The best-of-2 runs kept: 1df1c3 run 9819bb 14.5% / 11.4% / 33% (was 7bc9ed 19.9% / 11.8% / 56%); 3e9e7d run 9ecac6 1.7% / 0.2% / 5.6% (was 53b9c1 19.7% / 4.7% / 42%). Seed to seed the spread is large (1df1c3 4.5-25%). Wish score (counted): 0.803 and 0.775 (was 0.782 and 0.799); with the old 1 - closeness for 'apart' the same runs score within 0.03 of it.
- **What is left (1df1c3):** 5-8 Mkm2 blocks of good country behind ground that was ice until 2-10 kyr ago or behind hostile ranges, where even the pioneer pressure dies in 2-3 cells (draft draft-empty-enclaves-behind-ice-and-ranges); frost giants (sparse, insular, patches under the viable population fade) fill little of the polar land.

## Domestication lane (PW-691; senses PW-694, horses PW-688 part 1; built 2026-10-24)

### Senses and bodies (PW-694)
As built: every people has a `body` (`spec.BODY_DEFAULT`, resolved on `Lineage.body`, only what the spec gave on `Lineage.body_given`; a `body = {...}` table in the TOML/JSON). Keys: `sweet` (tastes sweet), `milk` (digests milk as an adult), `capsaicin` (feels chili heat), `bitter` and `smell` (low | normal | high or keen), `diet` (herbivore | omnivore | carnivore | obligate_carnivore), `raw_meat`, `cellulose`, `toxic` (a list of `alliums`: onion and garlic, `theobromine`: chocolate). Inherited key by key from the first parent (hybrids and templates too), so a stem's body reaches its children; validated in `spec.parse_body`. Nothing in the simulation reads it; it is for the cuisine pass (PW-692).
- **Editor** (`viewer/lineages.html`, People tab, "Senses and body"): a dropdown per field whose first entry is the inherited value in brackets, plus checkboxes for the toxicities.
- **Preset** (real-world analogues): feline stem (so tabaxi, leonin): no sweet, obligate carnivores, raw meat, keen smell, alliums and theobromine toxic; avian stem (aarakocra, kenku): no sweet, no capsaicin, poor smell, faint bitter, raw meat, alliums and theobromine toxic; reptilian stem: keen smell, raw meat; lizardfolk carnivores; tortles herbivores that digest cellulose; goblinoids raw meat and low bitter; bugbears keen-nosed carnivores; orcs raw meat and keen smell; dwarves low bitter; elves high bitter and keen smell; tritons no capsaicin, raw fish. Lactase persistence (`milk`) on the herder groups: human herders, human nomads, steppe orcs (draft draft-lactase-body-trait-on-groups-or-peoples).
- **Output:** `meta.lineages[].body`, and each living people's story ends with a sentence ("The tabaxi cannot taste sweet, have a keen sense of smell, ... and are poisoned by alliums (onion, garlic) and theobromine (chocolate).") in the stories and `run.txt`.

### Horses (PW-688 part 1; `planet/lineages/horses.py`)
The first domesticated animal. No fauna is simulated, so everything comes from the land and the peoples; nothing names Earth or a species, so it is the same in the real-world and the fantasy mode (PW-695). `meta.horses` (default true) and `meta.horses_at` (the date anchor, default 5.5 kyr) in the tree; a checkbox in the Tree box of the workbench.
- **Wild range:** `wild_range(env, land)`, 0..1 per cell from the epoch's climate and cover: mean annual temperature (-4, 4, 20, 27 C: rising, full, full, falling), rain (120, 300, 1000, 1700 mm), tree cover (full open below 8%, none from 35%) and ground (thinning from 2800 m, gone at 4500 m). In range from 0.35. Stored per frame as `horse_wild` (% suitability, 0 in the deep epochs).
- **Taming:** one date per run (the anchor x lognormal(0, 0.2), within 0.7-1.5x; its own random stream, so the peoples' draws are the same with horses off) and a homeland: the first step from the date on when a people with a herding way of life (herd share >= 0.4 in `landuse.shares`, i.e. the weight of the `grazing` good in its [[use]] rows: nomads, herders, steppe orcs) holds ground (>= 0.25) on the wild range of a landmass with >= 0.25 Mkm2 of it (>= 3 overlapping cells). The landmass is drawn in proportion to herders x wild range there, the cell likewise. The homeland blob is the peopled cells within 2 rings. Taming again: each other landmass with herders on its wild range and no riding yet tames independently at 0.06 per kyr (one homogeneous stock: "just horses"). The event is in the run's events (kind `horses`), `meta.horses.tamed` and `meta.present.horses`.
- **Riding spreads** (`rd`, stored per frame as `horse_riding`, 0 or 100): a front over peopled land at 1.8 km/yr (the pressure spread of `spread.py`; a gap of unpeopled land costs 0.8 per cell, the sea stops it), and `_carry`: every 0.5 kyr a patch of a people that rides over >= 30% of its land (propensity >= 0.3) that the front has not reached rides too (settled over the sea). A people's adoption is the presence-weighted share of its land with riding x its propensity (herders 1; others 0.15 + 0.85 x herd share; 0 for fliers, swimmers, cave dwellers, sparse giants).
- **Effects:** the people's speed x(1 + 1.5 x adoption x open share of its land) (speed 2.5x at most, on open ground); the capacity of a herding people's grazing land x(1 + 0.3 x adoption x herd share x grazing) where riding is known; in the land-use overlay (`landuse.py`) the land a herding person works x(1 + 0.5 x riding x propensity), so pasture and burned grassland grow.
- **Viewer:** globe layer `horses` (wild range green, riding amber; legend with the taming; hover row), the workbench's Results tab (Horses block: wild range, where and when, riding share per people), the report (`run.txt` "Horses") and each people's story ("the first to tame the horse, ~5.2 kyr ago on the steppe of ...", "took up riding ~4.6 kyr ago").
- **Numbers (L7, two tries, same seeds; horses off = `meta.horses = false`, which reproduces the earlier runs exactly: off on 1df1c3 is 9819bb's 0.803 / 14.5% empty; "empty" = PW-677's habitable land with no people):**

| world | horses | wish score (tries) | empty habitable / warm | riding known over | wild range |
|---|---|---|---|---|---|
| 1df1c3 | off | 0.803 (0.641, 0.803) | 14.4% / 11.4% | - | - |
| 1df1c3 | on, run 1b969d | 0.802 (0.611, 0.802) | 11.9% / 8.8% | 65.0 Mkm2 (11.2 on the wild range) | 27.6 Mkm2 |
| 3e9e7d | off | 0.775 (0.775, 0.761) | 1.7% / 0.2% | - | - |
| 3e9e7d | on, run b53bf6 | 0.776 (0.776, 0.758) | 2.0% / 0.3% | 139.4 Mkm2 (29.3 on the wild range) | 29.5 Mkm2 |

  1df1c3: the orcs tame horses 7.0 kyr ago (drawn 7.0; anchor 5.5) on the open grassland of the 68 Mkm2 southern continent (9.0 Mkm2 of wild range), the herder groups and steppe orcs ride within ~1 kyr, most peoples within 1.5 kyr, the gnomes and kenku 3-4 kyr later, and the dragonborn (on a continent apart) hardly at all. 3e9e7d: orcs again, 6.0 kyr ago, 78 Mkm2 continent (13.0 Mkm2 of range); riding reaches every people by 3.5 kyr ago. Single tries (try 0 of 1df1c3, tries = 1): off 0.641 / 4.46% empty, on 0.611 / 4.52%. So riding changes the empty land by +-0.3 points (a try's own noise; the 1df1c3 best-of-2 happened to pick a better try 1 with horses on), the wish score by -0.03 / +0.001 / -0.003, and who wins is unchanged; the effect is in the spread rates and the pasture, not the map of peoples. Cost: +6% of a try (the adoption loop; 266 s vs 257 s for one try at L7).
- **Judgement calls made:** (1) riding is carried with a people across the sea at once (draft draft-riding-carried-instantly-across-seas; without `_carry` the front stopped at the sea at 35 of 159 Mkm2); (2) the taming people on both worlds is "orcs" (the nomadic orc stem with its steppe orc group), not the human herders: both have herd share 1; the draw is proportional to presence x wild range; (3) no tuning attempts were needed beyond the carry (0 of ~5).

### Next animals (a design note, not built)
Same shape as the horse for each: a wild range from the land, a homeland and date among peoples that suit it, a front, and one effect on land use or speed. One `Animal` table (range function, anchor date, who takes it up, effect) would replace the horse-specific constants; the stock stays homogeneous per animal until the epic proper (separate stocks).
- **Dog (anchor ~15+ kyr):** wild range: wolf-like canid, anywhere with prey (all land outside ice and the driest desert), so the homeland is chosen by the hunter-gatherer peoples (low density, foraging use) at the date drawn; tamed early and often, so it spreads with *everyone* (propensity 1 for hunters and herders, 0.6 farmers); effect: x speed 1.15 and foraging capacity x1.1 (hunting), nothing for sea or flying peoples. The body traits matter here: a canid people's alliums toxicity is already modelled (PW-694); dogs must not be a food for them.
- **Sheep and goat (anchor ~11 kyr) and cattle (~10.5 kyr):** wild range: sheep and goat on hills and dry open ground (rain 200-800 mm, slopes: `hills`, steppe, mediterranean), cattle (aurochs) on moist grassland and open woodland (rain 600-1800 mm, tree cover < 50%); homeland among *farmers and herders* where the range overlaps fertile land (the Fertile Crescent was both). They are the herding stock: effect on land use: pasture and meadow per person x1.5 for herders, and the `grazing` [[use]] weight of herders and farmers rises with the stock (the herd share of the food goods), which the horse's K bump already does for riders; cattle add draft: farmers' cropland per person x0.8 (plough) from a later date. Milk (PW-694 `milk`) becomes meaningful: a people with `milk` and cattle or sheep has dairy.
- **Fowl (junglefowl ~8 kyr; geese, ducks):** wild range: tropical forest edge and wetland (jungle, wetland tags); homeland where farmers or foragers sit on it; cheap to carry, so it travels with all farming peoples and by sea. Effect: foraging/farm density bonus x1.05 and a cuisine marker only; useful mostly as a flag for PW-692.
- **Shared mechanics to do first:** (1) move the horse's constants into the animal table; (2) give each animal its own `rd` layer (`animal_<id>` frames) or one uint8 layer of bit flags; (3) carry across seas only with boats of the right size (draft draft-riding-carried-instantly-across-seas); (4) stocks per landmass (the epic proper); (5) fantasy-mode animals (PW-695) are extra table rows with a rarity and `force` for tests.
