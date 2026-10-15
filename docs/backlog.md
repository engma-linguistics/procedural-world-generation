# Backlog

*Snapshot of the board on 2026-10-14 (main at 382b370). The tickets in `issue-tracking/` are the source of truth; this page explains them from the epics down. Refresh it when the priorities change, not after every merge.*

**How to read the tables.** Each ticket shows `effort / impact`. Effort is agent time: **xs** under 30 min, **s** under 2 h, **m** about half a day, **l** a day or more, **xl** a multi-agent project. Impact: **high** means it shows on most worlds, is a key Earth check, or unblocks an epic; **med** means it shows in some places; **low** means cosmetic, rare or internal. "Blocked by" means a formal `blocked_by` on the board; "needs" means a practical dependency the board doesn't record yet.

---

## 1. Summary

**In flight: no model work.** The tectonics set (`tectsea`: PW-053 sea level, PW-024 plate count) merged as 0fd35e5 and its drafts were taken in (382b370). The only other worktrees are documentation agents (`docoverview`, and this one). The board has **115 open tickets**: 6 epics, 22 stories and 87 tasks. One ticket needs a decision (PW-117). None are blocked by unfinished in-flight work.

**Priority order** (set by the owner on 2026-10-14, `docs/coordination.md` §3b and §5). The planetary simulation is the focus; viewer and zoom polish come after.

| # | Work | Why this is its place |
|---|---|---|
| 1 | **PW-189 glacial isostasy**: ice sheets push the crust down, and it rebounds after they melt | The owner put it top of the queue. It is small (s) and high impact. It is the physics behind Hudson Bay, the Baltic and raised beaches, and the finishing pass needs it (PW-091, PW-093, PW-104). It also changes ice volume, so do it before or together with PW-190. |
| 2 | **PW-184 life epic**: PW-185 soils and PW-186 vegetation proposal in parallel, then PW-187 vegetation model and PW-188 coastal life | The owner calls soils and vegetation "must-haves, as soon as reasonable and parallelisable". Soils are world-level only (no new runs needed). The proposal is a document the owner reviews before any model code is written. |
| 3 | **Tectonics-quality leftovers**: PW-052 thin L7 continents (with retuned targets, per PW-169), PW-054 interior basins, PW-191 late plate collapse at L7, PW-190 too much land ice | These are what remains after the tectonics set (PW-108, PW-053, PW-024 done). L7 is now the showcase level and these are L7 problems. The planned L8 showcase waits for this set. |
| 4 | **PW-090 world finishing pass**: a ~1 Myr ice-age pass from a chosen world becomes the world's final phase, plus fine features for real use | This is the owner's "worlds are for using" goal. PW-091 is the first step. |
| 5 | **PW-013 rain and ocean overturning** | Many climate misses share one root: the rain model doesn't carry water vapour far enough. The first story, PW-014, is a diagnosis, uses separate files, and can start at any time. |
| 6 | **PW-156 weather generator**: days-scale animated storms and clouds | Wanted, not urgent. The climate fields it needs are already stored. |
| 7 | **PW-155 resources** (ores, coal, gems, Dwarf Fortress-style) | Wanted for games. Not scheduled. |
| 8 | **PW-103 multiscale time**: species, migrations, then fantasy races and civilisation | The vision epic, for the very end. For now the only ask is to keep the architecture able to support it. |

After step 3 (and a big batch of closed tickets) comes the **L8 showcase run** the owner approved: Earth-like, ~1.2 Gyr, plus a matching L7 (`coordination.md` §4).

**Suggested start** (details in §4): five parallel agents with no file overlap: (A) PW-189 then PW-190, (B) the tectonics leftovers, (C) soils, (D) the vegetation proposal, (E) the PW-014 rain diagnosis.

**Housekeeping** (§3.11): 7 duplicate or overlapping groups and 4 tickets that look stale or partly done. **Applied by the coordinator (f836fd4):** PW-048→172, PW-095→185, PW-071→129, PW-088→131, PW-077→097 merged; PW-083/096/097/098/188 rescoped; PW-089 closed (already done); PW-117 decided (A). Counts below predate these (now ~108 open).

### A few terms
- **Isostasy**: crust floats on the mantle like ice on water. Thick or light crust stands high; a load (an ice sheet, a volcano) pushes it down. **Flexure**: a stiff plate spreads a load sideways over hundreds of km.
- **Cell, level**: the globe is a grid of cells. Level 6 (L6) cells are ~110 km across, L7 ~55 km, L8 ~28 km. A **run** is the simulation over time; a **world** is one moment sliced out of it; a **zoom** is a 1–4 km/px regional refinement of a world; the **time zoom** is a ~1 Myr glacial-cycle simulation (kyr steps).
- **Endorheic (closed) basin**: land that drains to an inland lake or salt flat, not to the sea (the Caspian, the Great Basin).
- **Overturning (AMOC)**: dense, salty, cold water sinks near the poles and drives a slow global ocean conveyor. Measured in **Sv** (sverdrup, 10⁶ m³/s). **psu**: salinity units (‰).
- **E−P**: evaporation minus precipitation. A basin with E−P > 0 gets saltier.
- **Plate churn**: cells flipping owner or crust type from frame to frame because each plate's grid is re-sampled onto the world grid.
- **Strata, caprock, cuesta, karst**: rock layers; a hard top layer protecting soft rock below; the tilted ridge such a layer makes; landscapes dissolved out of limestone.
- **Arc, hotspot, craton, suture**: a volcano chain above a subducting plate; a mantle plume making island chains (Hawaii); old stable continental core; the seam where two continents welded.
- **LGM**: the Last Glacial Maximum, ~20 kyr ago, with sea level ~120–130 m lower than today.

---

## 2. Epics and workstreams, in priority order

### 2.1 Ice load on the crust: PW-189 (top of the queue; no epic)

**Goal.** Ice sheets weigh on the crust. Under 3 km of ice the ground sinks ~800–900 m (ice thickness × ρ_ice/ρ_mantle ≈ 0.3). After the ice melts the ground rebounds over ~10 kyr, which is why Hudson Bay and the Baltic are shallow seas and why old beaches stand above today's sea. In the main run (4 Myr climate steps) the load can be in equilibrium. In the time zoom (kyr steps) the crust should relax toward equilibrium over ~3–10 kyr, smoothed over hundreds of km by flexure.

| Ticket | What | Effort / impact |
|---|---|---|
| PW-189 | Ice load in isostasy: instant in the run, relaxing in the time zoom | s / high |
| PW-190 | Land ice lowers the sea by up to −340 m on some seeds (~4× Antarctica). Either justify it or bring it to the LGM's scale (~−150 to −200 m) | s / med |
| PW-050 | Tidy-up: `planet.tectonics.isostasy` is the function, so the module is shadowed (same files) | xs / low |

**Dependencies.** None blocking. PW-189 feeds PW-091 (finished world), PW-093 (raised beaches), PW-104 (embedded ice ages) and PW-037 (the imprint's "depression and rebound" layer, which should record what PW-189 computes, not reimplement it). PW-190 should come after PW-189: a depressed ice sheet sits lower and warmer, which changes its volume. PW-159 (one snowline rule for run and zoom) also touches `earth.ice_sheets`, so keep it out of this batch.

**Done looks like.** A 3 km sheet depresses its bed ~800–900 m. In the time zoom, deglaciated basins flood and then rise at Hudson Bay-like rates (~1 cm/yr). The largest ice-driven sea-level drop over 4 L6 seeds × 1 Gyr is explained, or brought to roughly LGM scale. The scorecard holds.

### 2.2 Life and the land surface: PW-184 (epic, xl / high)

**Goal.** Give every world cell and zoom pixel a soil and a vegetation cover, plus coastal and shallow-sea life, all derived from rock, climate, slope and history. No evolution is simulated. Species come much later, at the fine time scale (PW-103).

| Ticket | What | Effort / impact |
|---|---|---|
| PW-185 | **Soils**: ~12–20 types (oxisols, mollisols, podzols, cryosols, histosols/peat, andosols, …) plus fertility and depth, from the exposed stratum, climate, slope, surface age, ice and loess. A world layer, zoom pixels, a viewer layer, an Earth check against a soil map. No run cost. | m / high |
| PW-186 | **Vegetation proposal** (`docs/proposals/vegetation.md`): ~15–20 plant functional types crossed with structure and phenology to give ~40–80 named types (owner: ≥30, ≪2000); productivity, competition, fire, feedbacks (albedo, evapotranspiration, soil carbon); cost; Earth checks (MODIS land cover, NPP). For owner review. | s / high |
| PW-187 | **Vegetation model** per the approved proposal: type fractions per cell, productivity, fire, feedbacks. It replaces the Köppen lookup's role in the biome map. | l / high |
| PW-188 | **Coastal life**: reefs, mangroves, kelp, seagrass from SST, tides, waves, turbidity and shelf depth | m / med |

**Dependencies.** PW-185 and PW-186 can run in parallel now. PW-187 needs the owner's approval of PW-186 (not yet recorded as `blocked_by`). PW-188 comes after PW-185/186. Downstream: PW-099 (fertile land) needs soils; PW-083 (satellite view) needs PW-187; PW-097/077 (coast detail) take PW-188's layers.

**Overlaps to fix first** (§3.11): PW-095 (soils, permafrost, wetlands, peat, under PW-090) duplicates PW-185. PW-083 still lists "vegetation". Mangroves and reefs appear in PW-188, PW-097 and PW-077.

**Done looks like.** Worlds carry soil and vegetation layers that look right on Earth (major soil groups and land-cover classes in the right places) and on generated worlds. Zooms inherit them at pixel scale. The viewer shows them. The coastal-life layers feed the coast detail.

### 2.3 Tectonics-quality leftovers (no epic)

**Goal.** Make L7 runs as good as L6. Continents should be as thick and high as at L6, interiors should keep some closed basins, plate counts shouldn't collapse for hundreds of Myr, and ice shouldn't swing sea level by 300 m.

| Ticket | What | Effort / impact |
|---|---|---|
| PW-052 | L7 continents are ~2 km thinner and ~300 m lower than at L6, with twice the land near sea level and 3× the small specks. Find the resolution-dependent term (erosion, thermostat, diffusion) and **retune the continental targets** here rather than weakening the coherence welds (owner, via PW-169). | m / high |
| PW-054 | Generated worlds lose their closed basins: 0–4% of land drains inland, against ~20% on Earth. Needs tectonic sources of basins (foreland, intermontane like Tarim or the Altiplano, rift-flank highs), possibly less filling. The owner agreed this is the right fix. | l / high |
| PW-191 | L7 seed 21 falls to 3–6 plates for 300+ Myr despite PW-024's warm-mantle nudge, which ages the ocean and holds sea level low. Run 2–3 more L7 seeds before changing anything. | m / med |
| PW-190 | Ice sea level (listed in §2.1; batched with PW-189) | s / med |

**Closely related, worth doing in the same pass:** PW-135 (rift flanks get no uplift, m/med; this is a source of the "rift-flank highs" PW-054 wants, and the likely fix for PW-056, drainage switching outlet in one step). PW-051 (old oceans, now mostly the PW-191 problem; see §3.11). PW-046 (land fraction 34–36% vs Earth's 29%; retune with PW-052's targets).

**Dependencies.** None formal. Every ticket here needs L7 runs (~30–40 min per Gyr), so this batch is the most expensive in compute. PW-172 (hotspot spikes) edits `isostasy.py` like PW-189, so do it after batch A merges.

**Done looks like.** L7 median continental crust within ~1 km of L6's. Closed-basin land share visibly up (toward 10–20%) without lake blow-ups. On 2–3 L7 seeds, ≤4 plates for more than 100 Myr is explained or rare. The scorecard shows these numbers. Then the L8 showcase can run.

### 2.4 World finishing pass: PW-090 (epic, xl / high)

**Goal.** Turn a moment of a run into a world you can *use*. Run the ~1 Myr glacial time zoom from a chosen world, so an ice age or two comes and goes and glaciers carve valleys, and keep what it leaves behind as the world's last phase. Then add the fine features games need, and export.

**Ice-age engine (do first)**

| Ticket | What | Effort / impact |
|---|---|---|
| PW-091 | **First step.** `planet finish <world>`: run the time zoom from a world and write a new "finished world" (elevation, ice, lakes, sea level at the chosen "now"), with provenance and a viewer button | l / high |
| PW-031 | Time zoom glaciates generated worlds ~3× too hard (−400 m sea level, one at −520 m). *Needs fixing for PW-091*, or finished worlds come out buried in ice. Unparented. | m / high |
| PW-037 | Record the glacial imprint while the time zoom runs: maximum ice, erosion depth, moraines, outwash, proglacial lakes, loess, rebound | l / high |
| PW-104 | Embedded ice-age episodes in the main run (at most 3, default on), feeding their imprint back into the coarse state | l / med |

**What the ice leaves, drawn in the zoom**

| Ticket | What | Effort / impact |
|---|---|---|
| PW-092 | U-valleys, cirques, arêtes, fjords, hanging valleys with waterfalls, moraines, drumlins, eskers, kettle lakes. *Blocked by PW-037.* | l / high |
| PW-093 | Sea-level marks: rias (drowned valleys), raised beaches, exposed shelves and land bridges. *Blocked by PW-091.* | m / med |

**Fine features**

| Ticket | What | Effort / impact |
|---|---|---|
| PW-094 | River detail in the zoom: meanders, oxbows, terraces, alluvial fans, floodplains, wetlands | l / med |
| PW-101 | Zoom microclimate: lapse rate on fine elevation, valley cold pools, local rain shadows, snow line | m / med |
| PW-097 | Coast detail: reefs (non-volcanic), mangroves, barrier islands, cliffs vs beaches (overlaps PW-188 and PW-077) | l / med |
| PW-096 | Wind-made features. Dune fields are done (PW-012, PW-176), so **loess** is what's left. | m / low |
| PW-177 | Dune detail: seams between patches, network dunes, barchans (child of PW-096) | m / low |
| PW-095 | Soils, permafrost, wetlands, peat. **Duplicate of PW-185**, see §3.11. | m / med |

**Using a world**

| Ticket | What | Effort / impact |
|---|---|---|
| PW-100 | Export for game engines: 16-bit heightmap tiles, splat/land-cover maps, feature GeoJSON | m / high |
| PW-099 | Human-use layers: navigable rivers, harbours, passes, fertile land, fresh water (needs soils, PW-185) | m / med |
| PW-098 | Resources and hazards. Resources overlap the PW-155 epic. Owner: hazards matter mainly at fine time scales; static hazard maps are cheap. | l / med |

**Unparented time-zoom calibration that feeds this epic:** PW-030 (no 100-kyr sawtooth: ice only ratchets up, with no terminations), PW-033 (Earth reaches only −52 m and grows no Laurentide or Fennoscandian ice), PW-035 (a start-anchor cooling crutch outlives the starting ice), PW-114 (an Eemian-like start melts Antarctica, not Greenland), PW-115 (the ablation zone is one cell wide). See §3.6.

**Dependencies.** PW-189 first (rebound). PW-031 before or with PW-091. PW-037 → PW-092; PW-091 → PW-093. PW-104 reuses PW-037/091's machinery, so it comes last. PW-099 needs PW-185. PW-100 is independent and could go any time.

**Done looks like.** `planet finish` turns a world into a finished one with a believable glacial history (ice peaking near −100 to −150 m sea level, not −400). Zooms of formerly glaciated land show fjords, U-valleys and moraines. Coasts show rias and raised beaches. A finished world exports to a game engine with heightmaps, splat maps and a feature list.

### 2.5 Rain / moisture transport and the overturning: PW-013 (epic, xl / high)

**Goal.** The rain model drops water vapour too close to where it evaporated. That one root explains a cluster of misses: the Atlantic isn't saltier than the Pacific (so the ocean overturning needs a spin-up rule to turn on), rain is patchy, monsoons are weak, the Ganges is ~10× too small and the Nile 19× too big. Fix the transport, then let the overturning run on its own physics. Earth is a test analogue, not a parity target.

| Order | Ticket | What | Effort / impact |
|---|---|---|---|
| 1 | PW-014 | **Diagnose**: E−P per ocean basin and vapour transport across land bridges (Atlantic → Pacific across Central America ≈ 0.25 Sv observed), in `tools/earth_check.py` | m / high |
| 2 | PW-015 | **Fix moisture transport** (merges the Sahel/monsoon/Ganges/Nile discharge misses). *Blocked by PW-014.* | l / high |
| 3 | PW-016 | Remove the overturning spin-up rule; the Atlantic should turn on and the Pacific stay off by themselves. *Blocked by PW-015.* | m / high |
| – | PW-017 | Antarctic bottom water: Weddell/Ross too fresh, ~2.5 Sv vs 10–20; brine from wind-driven sea-ice export | m / med |
| – | PW-018 | Time zoom: carry salinity between climate refreshes so the overturning can stay off (Heinrich events, Younger Dryas) | l / med |
| – | PW-019 | Rain patchy cell to cell on flat ground, with diagonal streaks | m / med |

**Unparented climate tickets likely to move with it:** PW-026 (winter maritime air should reach 1000–2000 km inland; W Europe ~5 °C too cold), PW-162 (cloud misses that inherit rain errors), PW-122 (the Nile ends in a pit), PW-152 (Mediterranean too fresh), PW-038 (Labrador too warm). See §3.5.

**Dependencies.** A strict chain 014 → 015 → 016. PW-017 and PW-019 are independent. PW-018 relates to PW-030 (the 100-kyr cycle). PW-014 only touches tools, so it can start now.

**Done looks like.** Basin E−P contrast close to observed. Atlantic saltier than Pacific without a spin-up rule. Monsoon and big-river discharges in the right range. Rain maps without cell-scale lattice. Earth AMOC nearer 17 Sv than 11, and AABW stronger.

### 2.6 Weather generator: PW-156 (epic, l / med)

**Goal.** Watch one to five years of clouds and storms move over a world: mid-latitude lows along the storm tracks, hurricanes where the sea is warm enough, recurving into the westerlies. This is a stochastic generator whose statistics match the stored climate (the catastrophe-modelling approach), not a forecast model. It is cheap and computed on demand.

**Open stories:** none yet. The description lists five pieces: a daily seasonal cycle from the July/January fields; extratropical lows and highs; tropical cyclones; cloud and rain fields as climatology plus storm anomalies; and a viewer animation, track overlays and per-world storm stats.

**Dependencies.** The inputs exist already: seasonal winds, temperature, rain, SST and clouds on worlds. It would look better after PW-042 (the jet stream is too broad and zonal) and PW-074 (Southern Ocean storm tracks too weak). It is the finest phase of PW-103.

**Done looks like.** A viewer button plays a few years of weather on any world in seconds to a minute. Hurricane-prone coasts show up in highlights.

**First step:** split it into stories (the five pieces above) once it's scheduled.

### 2.7 Resources: PW-155 (epic, xl / med)

**Goal.** Dwarf Fortress-style resources from the geology that makes them: coal measures, evaporite salt, building stone, porphyry copper and gold at arcs, banded iron and diamonds on cratons, placers downstream of ore-bearing uplands, bauxite, oil and gas, hydrothermal deposits. The run gives each cell coarse likelihoods; zooms and fine passes place real seams, veins and pipes.

**Open stories:** none. **Overlap:** PW-098 (resources and hazards, under PW-090) covers the same resources. Move them here and leave PW-098 as hazards (§3.11).

**Dependencies.** The geological record it reads exists (strata, rock, history, volcano table; PW-005 done). Not scheduled. **Done looks like:** a resource layer and feature list per world, consistent with its geology, and deposits placed in zooms.

### 2.8 Multiscale time: PW-103 (epic, xl / high; vision, not scheduled)

**Goal.** One grand timeline, all visible together. Phase 1 is the tectonic run (Myr steps). Phase 2 is the ~1 Myr glacial pass (PW-090). Phase 3 is the last ~20 kyr down to centuries ("over this 500-year span part of Continent 4 cooled, forcing migrations"). On top of that, at the very end: real-world-like species placed by climate (no evolution), possibly biogeographic realms from landmass isolation, fantasy races (backwards from a target phylogeny, or forward Dwarf Fortress-style), and civilisation as a separate project.

**Open stories:** none. The near-term ask is architectural only: keep the state at an end point, sub-runs with finer steps, and per-period layers. Provenance in the viewer (PW-128) was the first step and is done.

**Dependencies.** PW-090 (Phase 2), PW-184 (habitats), PW-156 (finest weather).

### 2.9 Moons and planet bodies: PW-216 (epic, xl / low; bottom of the backlog)

**Goal.** Tides, day length and the planet body stop being Earth's fixed values (owner, 2026-10-15: not core functionality). **Stories:** PW-217, the moon recedes and the day lengthens over a run (tidal friction; the likeliest first step); PW-218, configurable moons, including more than one; PW-219, a stretch goal of its own: planets of other size, density and makeup.

---

## 3. Open tickets with no epic, by theme

80 tickets. 13 of them still carry a parent epic that is already done: PW-001 (discrete volcanoes) or PW-005 (landform classes). They are leftovers of finished projects and are listed here. Tickets already covered in §2 (PW-189, 190, 052, 054, 191) are not repeated.

### 3.1 Tectonics artefacts (cell-scale glitches)
Each plate keeps its crust on its own grid, and every step the world grid samples the nearest plate cell. Most of these are side effects of that sampling. PW-108 (done) halved the churn; these are what's left. None are urgent individually, but together they make frames flicker and leave odd pits and spikes.

| Ticket | What | Effort / impact |
|---|---|---|
| PW-172 | One-frame 11–18 km peaks: thick sediment-filled hotspot cells get volcano isostasy (350 m/km). Diagnosed, with options; lean A+B. **Supersedes PW-048.** | s / med |
| PW-048 | Single-sample 12–13 km spikes (the original report; PW-172 is its diagnosis) | s / med |
| PW-171 | Pits in continents, 2+ km below their neighbours, from suture seams and welded inlets | m / med |
| PW-170 | Plate ownership still flickers along collision fronts (ghost cells win cells back) | m / med |
| PW-134 | Per-cell records, rock and cover flicker frame to frame as the world resamples the plates | m / med |
| PW-174 | Plate cells no world cell samples miss each step's physics (~7%); an attempted fix was dropped | s / low |
| PW-173 | New ocean floor appears in sampling gaps where plates converge; an attempted fix showed no gain | s / low |
| PW-047 | Ocean plate boundaries look ragged. Not re-checked since B′, so may be stale. | m / low |

### 3.2 Tectonics realism and calibration
| Ticket | What | Effort / impact |
|---|---|---|
| PW-135 | Rifted margins get no flank uplift, so few great escarpments (Drakensberg, Western Ghats) stand high. Also feeds PW-054 and PW-056. | m / med |
| PW-133 | Continental plume heads pile 7–16 km of flood basalt (Deccan ~2 km); cap it or count the dynamic swell | s / med |
| PW-046 | Land fraction 34–36% (Earth 29%); continental volume drifts +2–5% mid-run | m / med |
| PW-051 | Mean ocean age 83 Myr at L6 (Earth ~60), 140–185 at L7 in few-plate phases. **Partly stale**, see §3.11. | m / med |
| PW-165 | Record the fold strike (direction of shortening) so zoom fold belts don't guess it | m / med |
| PW-117 | **needs-decision.** Hotspot islands are smaller than an L6 cell, so the grid shows a bank, not land. Options: A accept, B widen cones at coarse levels, C raise island cells at world build. Lean A (plus C if the globe looks empty). | s / med |
| PW-025 | Supercontinent cycle regularity. Pinned by the owner; better since PW-024. | l / low |

### 3.3 Geological record and landform leftovers (PW-005 done)
The run records each cell's strata and history; the zoom turns landform classes into terrain (escarpments, caprock, karst, coastal plains). These tickets would make the record richer, so the zoom has more to draw.

| Ticket | What | Effort / impact |
|---|---|---|
| PW-136 | Option C only (B is done): erosion reads the exposed stratum, so caprock protects soft rock in the run itself. Moves erosion everywhere; expect retuning. | m / med |
| PW-130 | Carbonate (limestone) reaches the surface on <1% of land (Earth ~10–15%), so there is little karst. Add shelf carbonate in shallow seas. | m / med |
| PW-147 | Caprock is recorded as near-flat, so no cuestas. Owner chose B (record a broad tilt in the run): wanted, low priority. | m / low |
| PW-175 | Coastal-plain beds have no seaward dip, so their cuestas follow the contours (same family as PW-147) | m / low |
| PW-179 | Tilted caprock in a big zone measures its tilt from a far origin. *Blocked by PW-147.* | s / low |
| PW-049 | Sediment compaction isn't remembered after uplift | m / low |
| PW-132 | The Earth reference world has no geological record, so no landform classes. Only matters if Earth class shares become a target. | m / low |
| PW-182 | Showcase world a08983 still has the old dune classes. Resolves itself at the next showcase run. | xs / low |

### 3.4 Volcano leftovers (PW-001 done)
| Ticket | What | Effort / impact |
|---|---|---|
| PW-116 | Arcs read as blocky islands with a few cones; real arcs have a volcano every ~50–70 km | m / med |
| PW-118 | Continental hotspot vents drawn as shields; should be calderas on a lava plain (Yellowstone, Snake River) | s / low |
| PW-119 | Highlights: find island chains and atolls from the volcano table | s / low |
| PW-117 | Decision on sub-cell hotspot islands (listed in §3.2) | s / med |

### 3.5 Climate and ocean misses vs Earth
Earth is used as a test analogue: the model runs on Earth's terrain and is compared with observations. Several of these share the rain-transport root (§2.5) and should be re-measured after PW-015 before anyone works on them.

| Ticket | What | Effort / impact |
|---|---|---|
| PW-026 | Winter maritime air should reach 1000–2000 km inland under the westerlies (W Europe ~5 °C, Scandinavia ~14 °C too cold in winter) | m / high |
| PW-112 | Bare polar lowland summers far too warm (Antarctica's bedrock at +15 °C); ice survives only through compensating terms | m / med |
| PW-039 | East Antarctic interior ~10 °C too warm (probably the same polar profile as PW-112) | m / med |
| PW-038 | NE Canada, the Labrador Sea and Greenland's margins too warm; this also blocks Laurentide ice in the time zoom | m / med |
| PW-041 | Gulf Stream and Kuroshio separate from the coast too far north | l / med |
| PW-042 | Jet stream broad and zonal, with modest meanders | m / low |
| PW-162 | Clouds: summer continents too clear, wet tropics too gloomy, winter trade-wind seas too cloudy | s / low |
| PW-152 | Mediterranean and Red Sea too fresh and cool (coarse ocean grid mixes them through their straits) | m / low |

### 3.6 Glacial time zoom calibration (feeds PW-090)
| Ticket | What | Effort / impact |
|---|---|---|
| PW-031 | Generated worlds glaciate ~3× too hard; needed for PW-091 | m / high |
| PW-033 | Earth: weak glaciation (−52 m), no Laurentide or Fennoscandian ice (partly PW-038) | l / med |
| PW-030 | No real 100-kyr sawtooth: needs CO₂, proglacial lakes, dust, meltwater coupling (PW-018) | l / med |
| PW-035 | A start-anchor cooling persists after the starting ice is gone | m / low |
| PW-115 | The ablation (melt) zone is one cell wide; needs sub-cell melt at margins | m / low |
| PW-114 | An Eemian-like Earth start melts Antarctica instead of Greenland | s / low |

### 3.7 Rivers and lakes
| Ticket | What | Effort / impact |
|---|---|---|
| PW-055 | Giant open lakes (up to 2.3 M km²) never drain: outlets should cut down | m / high |
| PW-028 | Arctic rivers: seasonal flow (frozen 6–8 months, spring flood), at least a stored flood ratio | m / med |
| PW-122 | Earth check: the Nile ends in a cell-scale pit in Nubia (a gorge narrower than a cell) | m / low |
| PW-056 | Drainage switches outlet in one step when a rift opens; likely fixed by rift-flank uplift (PW-135) | l / low |
| PW-057 | Run lakes and sliced-world lakes disagree | m / low |

### 3.8 Coast: waves and tides
| Ticket | What | Effort / impact |
|---|---|---|
| PW-074 | Wave power: Southern Hemisphere westerly coasts too weak, N Atlantic too strong (storm-track model) | m / med |
| PW-077 | Coast detail: spits, beach ridges, dendritic tidal channels (and mangroves: overlaps PW-188/097) | l / med |
| PW-075 | Wave power too high in enclosed seas, too low on India's west coast | s / low |
| PW-076 | Tides: Fundy too small, Caribbean too big, no amphidromic points (where the tide range is zero) | m / low |
| PW-106 | Arctic tides 2–5× too big: the Arctic basin counts as open ocean | s / low |

### 3.9 Zoom polish and new zoom capabilities
The zoom is in good shape after five batches (landforms, falls, ice, polish). What's left is mostly small artefacts and two new capabilities: a 3D view and finer nested zooms, both wanted by the owner ("see a big ole waterfall").

**New capabilities**

| Ticket | What | Effort / impact |
|---|---|---|
| PW-072 | Zoom 3D view: a low-poly three.js heightmap with water and rivers (subsystem viewer) | m / high |
| PW-129 | Nested fine zoom (~100–250 m/px) of a small area of a zoom, tied to the 3D view | m / med |
| PW-071 | Finer zooms, 100–250 m pixels. **Near-duplicate of PW-129.** | m / med |
| PW-139 | July/January temperature and rain layers in zooms (season picker) | s / low |
| PW-073 | The Earth world can't be zoomed (no rock layers) | s / low |

**Artefacts**

| Ticket | What | Effort / impact |
|---|---|---|
| PW-061 | Delta fans small, branches straight, river mouth up to ~100 km from the coarse mouth | m / med |
| PW-124 | Some river stretches still perched above the land beside them | m / low |
| PW-125 | Remaining undesigned drops on mid-size streams, hanging joins, edge steps | s / low |
| PW-123 | Outflow ramps of high mountain lakes stand up to ~440 m above the land | s / low |
| PW-183 | Review discharge thresholds now that streams carry runoff, not rain | s / low |
| PW-159 | Snowline set by the coarse ice footprint. Decided: snowfall-dependent snowline in **both** run and zoom (touches `earth.ice_sheets`). | s / low |
| PW-160 | Ice-free pixels next to coarse ice inherit the ice's cooled temperature | s / low |
| PW-168 | Shield domes ringed by streams (a moat look) | s / low |
| PW-178 | Marshes only on coastal plains; none on deltas, floodplains or lake shores | s / low |
| PW-060 | A zoom sees only part of a big lake's catchment | m / low |

### 3.10 Viewer, highlights, store and infra

| Ticket | Subsystem | What | Effort / impact |
|---|---|---|---|
| PW-083 | viewer | Vegetation and a "satellite view". The vegetation part is now PW-187. | l / med |
| PW-082 | viewer | Lake display: hover needs elevation, confusable colours, "~0 m" depths | s / low |
| PW-154 | viewer | Overturning schematic: deep limbs missing or roundabout on some worlds | s / low |
| PW-079 | highlights | Highlights at 110 km cells: canyons weak, some Earth picks off | m / low |
| PW-080 | highlights | Fastest plate (only with something visible) | s / low |
| PW-164 | highlights | Mild-winter retreats should rank by winter sunshine | xs / low |
| PW-131 | store | Checkpoints carry stale crust of unowned cells (~3× their size; L7 90–170 MB each); a volcano reads it | s / low |
| PW-088 | store | Checkpoints are big. **Near-duplicate of PW-131.** | m / low |
| PW-089 | store | Replay falls back to t=0 when the code changed. **Looks done**, see below. | m / low |
| PW-107 | store | July/January winds in run keyframes | s / low |
| PW-138 | store | July/January rain (and temperature) in run keyframes; lean B, with PW-107 | s / low |
| PW-153 | store | Overturning strength per frame in run.json (cheap); per-cell ocean layers (likely not) | m / low |
| PW-084 | infra | Numba parallel kernels aren't safe for concurrent calls from threads (one compute lock) | s / low |
| PW-085 | infra | `api.Jobs` state is lost on server restart | s / low |

### 3.11 Housekeeping: duplicates, overlaps and stale tickets
Applied by the coordinator in f836fd4 (see the summary); the list below is kept as the record.

**Duplicates and overlaps**
1. **PW-048 → PW-172.** PW-172 is the diagnosis of PW-048's spikes, with options. Merge PW-048 into PW-172 and close it.
2. **PW-095 → PW-185.** Both are soils. PW-185 is the fuller spec, and its soil set already includes permafrost (cryosols) and peat (histosols). Close PW-095 into PW-185, carrying "permafrost extent" and "wetlands" into PW-185's checklist (wetland drawing in zooms is also PW-178 and PW-094).
3. **PW-083 vs PW-187.** Vegetation is now PW-187. Retitle PW-083 to "Satellite (true-colour) view of globe and zooms", add `blocked_by: [PW-187]`, and consider parent PW-184. Its old condition ("after PW-005 and PW-001") is met: both are done.
4. **PW-097 / PW-077 vs PW-188.** Mangroves are in all three, reefs in PW-097 and PW-188. Proposal: PW-188 owns the biology (reefs on non-volcanic coasts, mangroves, kelp, seagrass). Merge PW-077 (spits, beach ridges, tidal channels) into PW-097. Retitle PW-097 to coast *form*: cliffs vs beaches, spits, beach ridges, tidal channels, and barrier islands beyond coastal plains (the zoom already draws barrier islands and lagoons on coastal plains since PW-012).
5. **PW-071 → PW-129.** "Finer zooms 100–250 m" and "nested fine zoom 100–250 m" are one feature. Merge PW-071 into PW-129.
6. **PW-088 → PW-131.** PW-131 is the concrete fix for PW-088's big checkpoints. Merge PW-088 into PW-131, keeping its "dead plates keep full arrays" idea.
7. **PW-098 vs PW-155.** Resources are in both. Move PW-098's resource list to PW-155, and retitle PW-098 to "Hazard maps (static): earthquake, volcanic, tsunami, flood zones" (low priority per the owner).

**Stale or partly done**
8. **PW-089** (replay falls back to t=0): the ticket asks for a clear message. `slice_world` already warns when the run's code differs, and `ReplayMismatch` says "use --force". Suggest closing it as done.
9. **PW-051** (old oceans; basin term on its clip): the clip is gone. PW-053 replaced it with a 30-Myr smoothing and a tanh limit, and set equilibrium start ages (mean 60 Myr). What's left (old oceans in few-plate L7 phases) is PW-191's problem. Re-measure the mean ocean age at L6, then close into PW-191.
10. **PW-096** (dune fields and loess): dune fields are done (landform class PW-176, zoom synthesis PW-012). Retitle it to loess; PW-177 stays as its child for dune detail.
11. **PW-047** (ragged ocean plate boundaries): last seen on v1 worlds. Re-check on a current showcase plate layer and close it if it's gone.

**Minor**
- 13 open tickets sit under the closed epics PW-001 and PW-005 (PW-116, 117, 118, 119; PW-130, 132, 135, 136, 147, 165, 168, 175, 179). That's legal, but `tree` shows them under "done" epics. Leave them, or set parent to null.
- Add `blocked_by: [PW-186]` to PW-187 (the model waits on the approved proposal). Consider `PW-031` as a blocker of PW-091.
- Link PW-056 to PW-135 (rift-flank uplift is its likely fix), and PW-039 to PW-112 (same polar warm bias).
- PW-037 lists "isostatic depression and rebound" as an imprint layer. Note there that PW-189 owns the mechanism.
- PW-182 resolves at the next showcase run; close it then.
- PW-117 is the only `needs-decision`. Under the owner's north star (decide routine calls) the coordinator could take the lean (A).

---

## 4. Suggested next batches

Five parallel agents, consistent with the owner's order, with no two touching the same file. Two more fill-in batches are listed for agents that free up.

| Batch | Tickets | Files it owns | Notes |
|---|---|---|---|
| **A. Ice load** | PW-189 → PW-190, plus PW-050 | `planet/tectonics/isostasy.py`, `tectonics/__init__.py`, `tectonics/earth.py` (ice and sea level), `planet/timezoom.py` / `timezoom_kernels.py`, `tools/sealevel.py` | Top priority. L6 checks, then one L7. Keep PW-159 (snowline in `earth.ice_sheets`) for later. |
| **B. Tectonics quality** | PW-052 (+ PW-046 targets), PW-191, PW-054 with PW-135 (rift flanks) | `tectonics/crust.py`, `events.py`, `params.py`, `planet/surface.py`, `tools/scorecard.py`, `tools/supercontinent.py` | Compute-heavy (L7 runs). Start with PW-191's extra seeds (they also give baselines for PW-052). PW-172/048 join after A merges (`isostasy.py`). Must not edit `earth.py`'s ice code. |
| **C. Soils** | PW-185 (absorbing PW-095) | new `planet/soils.py`, `planet/world.py` (finish), soil specs in `store.LAYERS`, viewer layer in `viewer/index.html`; zoom pixels in `planet/zoom.py` last | World-level only, so no runs. Earth check against a soil map. |
| **D. Vegetation proposal** | PW-186 | `docs/proposals/vegetation.md` only | For owner review. The agent can also suggest the PW-083 / PW-097 / PW-188 rescoping. |
| **E. Rain diagnosis** | PW-014 | `tools/earth_check.py` (diagnostics only, reads `climate.py`) | Starts PW-013 cheaply. Its findings decide PW-015's approach. |
| *F. Fill-in: highlights and infra* | PW-164, PW-119, PW-080, PW-084 | `planet/highlights.py`, `planet/api.py` | Small and independent of A–E. |
| *G. Fill-in: store* | PW-131 (+ PW-088), PW-107 + PW-138 | `planet/store.py` checkpoints, `tectonics/output.py`, `planet/timeline.py`, `tectonics/volcanism.py` | Conflicts with C on `store.LAYERS` (different entries), and PW-107/138 touch the snapshot. Best after A and B merge. |

**What comes after these:** PW-031 + PW-091 (the finishing pass's first step; needs A merged since both touch `timezoom.py`); PW-187 once the proposal is approved; PW-015 after PW-014; the L8 showcase once B is done; then the zoom 3D view (PW-072 + PW-129).

---

## 5. Size of the backlog

**115 open tickets:** 6 epics, 22 stories, 87 tasks. 114 todo, 1 needs-decision, 0 in progress, 0 blocked by status (5 have a formal `blocked_by` on another open ticket: PW-015, 016, 092, 093, 179). For comparison: 74 done, 2 won't-do.

**By subsystem**

| Subsystem | Open | xs | s | m | l | xl | high | med | low |
|---|---|---|---|---|---|---|---|---|---|
| zoom | 22 | 0 | 11 | 9 | 2 | 0 | 1 | 7 | 14 |
| tectonics | 20 | 1 | 7 | 10 | 2 | 0 | 3 | 12 | 5 |
| surface | 16 | 1 | 1 | 10 | 2 | 2 | 4 | 6 | 6 |
| timezoom | 12 | 0 | 1 | 3 | 6 | 2 | 5 | 4 | 3 |
| climate | 11 | 0 | 2 | 6 | 2 | 1 | 4 | 5 | 2 |
| coast | 7 | 0 | 2 | 3 | 2 | 0 | 0 | 4 | 3 |
| store | 7 | 0 | 3 | 4 | 0 | 0 | 1 | 0 | 6 |
| hydrology | 5 | 0 | 0 | 4 | 1 | 0 | 1 | 1 | 3 |
| ocean | 5 | 0 | 0 | 4 | 1 | 0 | 1 | 3 | 1 |
| highlights | 4 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 4 |
| viewer | 4 | 0 | 2 | 1 | 1 | 0 | 1 | 1 | 2 |
| infra | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| **total** | **115** | **3** | **33** | **55** | **19** | **5** | **21** | **43** | **51** |

**Effort × impact**

| | high | med | low |
|---|---|---|---|
| xs | 0 | 0 | 3 |
| s | 2 | 5 | 26 |
| m | 9 | 26 | 20 |
| l | 6 | 11 | 2 |
| xl | 4 | 1 | 0 |

**Reading it.** Only two tickets are both cheap (s or less) and high impact: PW-189 and PW-186, the top of the owner's list. The high-impact work is mostly m–xl and sits in the epics and the tectonics set. The 29 xs/s low-impact tickets (mostly zoom and store polish) are good fill-in work but won't move the planets much. If the housekeeping in §3.11 is applied, the board drops by about 8 tickets (6 merges, 1–2 closures).
