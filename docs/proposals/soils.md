# Soils: proposal (PW-185, for owner review)

**Status 2026-10-16: steps 1–6 and 8 built (`planet/soils.py`, `tools/soil_check.py`, `tools/zoom_soil_check.py`, viewer; docs/overview.md §2.21 has what was built and the Earth numbers; step 6, the zoom, PW-331: per pixel around the zoom vegetation, the pixel's slope converted to the cells' measure, no climate memory); steps 7 (coal from peat in the run) and 9 (game attributes, satellite) not yet. Deviations from the text below: erosion rises with the slope squared plus wind deflation; lime and salt follow the present climate (memory moves W only); mollic soils also need bases; podzols need sand, or acid rock or till under conifers and heath; frozen soil = continuous permafrost; thin soils hold some water in fissured rock below; the fertility factor multiplies each stand's NPP, not light-use efficiency (coordinator, option C: 0.85–1.1 on plants), and Earth's NPP is left at 57.6 Pg C/yr (was 62.7; agreement 62.4 → 60.6%) rather than renormalised back.**

*2026-10-15. Implemented once approved. Parent epic PW-184 (life and the land surface); it takes in PW-212 (vegetation to soils, coal from peat) and the old PW-095 (permafrost, wetlands, peat). Numbered owner decisions are in §9.*

**In one paragraph:** every land cell of a world, and every zoom pixel, gets a **soil**: one of **19 named types** ("black earth", "leached red tropical soil", "ash-grey podzol"), plus continuous fields for **depth, texture, fertility, water capacity, drainage, soil carbon, peat, permafrost and loess**. Two short passes sit either side of the existing vegetation. The **mineral** pass (parent rock, slope, erosion, surface age, climate) gives depth, texture, leaching and water capacity; vegetation then uses that capacity and a mild fertility factor instead of today's fixed values. The **organic** pass turns the vegetation's litter and flooded share into soil carbon, peat and the types that need them (peat, black earth). The order is fixed, so there is no loop. In the run, coal comes from peat accumulation instead of `veg > 0.5`; nothing else runs there. Cost: under a second per world or zoom. The Earth check is against SoilGrids on observed climate, so the rain rework (PW-013) can't move it.

---

## 1. What already exists that soils can use

Checked in the code (main 57d8abe). Nothing new is needed from the run.

- **Parent rock** (world layers from the run's record): `strata_top` (the exposed stratum, else the basement), `strata_top_km`, `strata_next`, `rock`, `surface_rock`, `sediment_cover`. The rocks are ocean crust, hotspot basalt, arc, sediment-born continent, orogen, craton, granite, limestone, dolomite, sandstone, quartzite, shale, evaporite, coal, flood basalt and tuff: enough for texture and base richness.
- **Surface age:** `glaciated_myr` (Myr since last under ice; 9999 never), `landform_age` (since rifting, folding or eruption, or when the top stratum last grew; 0 for hills), `crust_age`, and the volcano table in the world meta. Exhumation (`record.EXHUMED`) and per-stratum ages live only in checkpoints, not in keyframes or Zoom-button worlds, so a general soil age has to come from an erosion estimate (§3.2).
- **Landform:** `landform` (arcs and hotspots mean ash, dunes loose sand, coastal plains young sediment, karst limestone, shields old rock).
- **Climate and water:** `temperature`, `warm_month`, `cold_month`, `precipitation` (+ `_jul`/`_jan`), `pet`, `evaporation`, `runoff` (the water that drains through the soil and leaches it), `climate.months` (twelve months with **snowpack**), `river_frozen`, `flow`, `flood_ratio`, `lake_kind` (fresh / salt / pan), winds `wind_e/n` (annual, July, January), `ice`.
- **Vegetation:** `npp` (litter in equilibrium), the 19 `veg_<PFT>` covers (grass, conifers, heath, peat moss `Sph`), `fire_return`, and `flooded` (share of the cell under water part of the year: floodplains, flat wet ground, flat permafrost, lake shores), which is the waterlogging mask.
- **What vegetation takes from soils today:** fixed `TOP_MM, DEEP_MM = 50, 150` mm ("PW-185 will set them"), the subsoil thinned on steep cells; in the zoom `SOIL_THIN` (slopes) and `DEEP_SOIL` (wet hollows). No soil factor in its light-use efficiency yet (PW-212's `f_soil`).
- **Zoom pixels:** `elevation` (so slope), `rock`, `surface_rock`, `landform`, `ice` (the zoom's own glaciers), `discharge`, `drainage_area`, `twi`, `river_dist`, `coast_dist`, `wetland`, lapse-corrected `temperature`, `precipitation`, and the zoom vegetation's `npp`.
- **The run:** `sim.npp`, `sim.veg`, `sim.flow`, lakes, ice at every climate update. Coal today: `swamp = land & (e < 250) & (P > 1000) & (sim.veg > 0.5)` in `earth.deposit()`, which also knows each cell's net deposition `net`.
- **Missing:** no permafrost layer (vegetation uses `temp < −2 °C` on flat ground as a stand-in in `vegetation.flooded`) and no dust or loess anywhere (loess is on PW-037's list for the time zoom, not built).

---

## 2. The soil types

### 2.1 Why this shape

The world's soil maps use WRB (FAO's World Reference Base, 32 groups) or USDA Soil Taxonomy (12 orders). Both name soils by what formed them, which is exactly what we can compute. We take **19 types**, mostly WRB groups with a few merged, named for a player first, with the WRB and USDA names on the hover card. SoilGrids (the Earth check, §7) maps WRB, so the check stays simple.

### 2.2 The 19 types and their rules

Ordered rules: a cell takes the first that holds. Thresholds are starting values for the Earth tuning. *W* is the weathering stage (§3.3: how much water has drained through the soil over its lifetime, scaled by warmth), *h* the soil depth, *P/PET* the moisture index.

| # | Name (player) | WRB / USDA | Rule (first that holds) | Earth example |
|---|---|---|---|---|
| 0 | no soil | – | under ice, lake, or bare rock with h < 5 cm | Antarctica, fresh lava |
| 1 | **peat** | Histosol | peat ≥ 0.4 m (§3.4) | Hudson Bay lowlands, W Siberia, Borneo peat swamps |
| 2 | **frozen tundra soil** | Cryosol / Gelisol | permafrost within 1 m (§3.5) | Arctic Siberia, N Canada |
| 3 | **thin stony soil** | Leptosol / Entisol (lithic) | h < 0.25 m: steep ground, young lava, ice-scoured shield | Alps, Canadian Shield, Tibet's slopes |
| 4 | **salt-crusted soil** | Solonchak / Solonetz | salt pan or salt-lake shore (`lake_kind` 2–3 within a cell), evaporite parent, or a dry closed basin floor | Aral, Great Salt Lake, Danakil |
| 5 | **river-laid alluvium** | Fluvisol / Entisol (fluvent) | flooded share from floodplains and deltas ≥ 30%, or a coastal plain still aggrading | Nile, Ganges, Mekong deltas |
| 6 | **waterlogged grey clay** | Gleysol / Aquept | flooded share ≥ 30% (not alluvium, not peat) | W Siberia margins, Amazon backswamps |
| 7 | **volcanic ash soil** | Andosol | arc or hotspot landform with a volcano active or dead ≤ ~1 Myr nearby, or `strata_top` tuff; P/PET ≥ 0.5 | Java, Japan, Cascades, Andes |
| 8 | **loose sand** | Arenosol / Psamment | dune field, or sand-rich parent (sandstone, quartzite, sand cover) that is dry (P/PET < 0.5) or young (W low) | Kalahari, Sahel sand belt |
| 9 | **desert pavement soil** | Gypsisol / Aridisol (gypsid) | P/PET < 0.1 | central Sahara, Atacama |
| 10 | **caliche desert soil** | Calcisol / Aridisol (calcid) | P/PET < 0.35: lime accumulates where rain can't wash it out | Sonora, Iran, inland Australia |
| 11 | **cracking black clay** | Vertisol | clay-rich parent (basalt, flood basalt, shale) on flat ground, ≥ 4 dry months, P/PET 0.35–1 | Deccan, Sudan Gezira, Texas |
| 12 | **chestnut steppe soil** | Kastanozem / Mollisol (ustoll) | grass share ≥ 50%, P/PET 0.35–0.6, soil carbon ≥ mollic threshold | Kazakh steppe, Mongolia, high plains |
| 13 | **black earth** | Chernozem / Phaeozem / Mollisol | grass share ≥ 40%, P/PET 0.6–1.2, soil carbon ≥ mollic threshold | Ukraine, Pampas, US Corn Belt |
| 14 | **ash-grey podzol** | Podzol / Spodosol | humid (P/PET ≥ 1) and cool (warmest month < 20 °C), on sandy or acid parent (sandstone, quartzite, granite, till), or under conifers and heath | Scandinavia, boreal forest, New England |
| 15 | **dark limestone soil** | Rendzina (Leptosol rendzic, WRB) / Rendoll | limestone or dolomite parent, humid, h < 0.5 m | karst uplands, chalk downs |
| 16 | **leached red tropical soil** | Ferralsol / Oxisol | warm (> 18 °C), very high W (old, stable, wet) | Amazon and Congo basins, Brazil's shield |
| 17 | **red clay forest soil** | Acrisol / Lixisol / Ultisol | warm (mean > 12 °C), high W | SE United States, S China, Indochina |
| 18 | **brown forest soil** | Luvisol / Albeluvisol / Alfisol | moderate W, humid enough to move clay down (P/PET ≥ 0.6) | W Europe, Great Lakes, NE China |
| 19 | **young brown soil** | Cambisol / Regosol / Inceptisol | everything else: young or moderately weathered | mountains, recently glaciated lowlands, hill country |

("No soil" plus 19 types. Merges: Phaeozem into black earth, Lixisol and Alisol into red clay, Albeluvisol into brown forest, Regosol into young brown, Nitisol and Plinthosol into the tropical reds; Durisols, Planosols, Stagnosols and Umbrisols are too rare or too subtle to show.)

Earth shares for scale, from the SoilGrids map (pixel shares, not area-weighted, so the high latitudes count too much): Cambisols 21%, Cryosols 9%, Luvisols 8%, Arenosols 7%, Ferralsols 7%, Leptosols 7%, Acrisols 6%, Histosols 4.5%, Podzols 4%, Kastanozems 3.5%, Chernozems + Phaeozems 5%, Calcisols 3%, Vertisols 2.4%, Fluvisols + Gleysols 2.5%, Andosols 0.8%, Solonchaks + Solonetz 1.3%.

### 2.3 Continuous fields (world layers, also per zoom pixel)

| Layer | Unit | What it is |
|---|---|---|
| `soil` | id | the named type (legend `soils`) |
| `soil_depth` | m (0–3) | rootable soil above rock or saprolite |
| `soil_texture` | id | sand / loam / silt / clay / peat (from parent and weathering) |
| `soil_water` | mm | water the root zone holds (top 0.3 m + subsoil to 1.5 m): what vegetation's bucket uses |
| `soil_fertility` | 0–1 | nutrient and base status (for plants and farming) |
| `soil_drainage` | class 1–5 | excessive, well, moderate, poor, very poor |
| `soil_carbon` | kg C/m² | organic carbon in the top metre (peat included) |
| `peat_depth` | m | peat thickness (0 where none) |
| `permafrost` | class 0–3 | none, sporadic, discontinuous, continuous |
| `loess` | m | wind-blown silt thickness |

About 10 one-byte layers: +1.6 MB on an L7 world (today 60 MB), +2.5 MB per zoom.

---

## 3. The model

Everything is per cell (or pixel), with no state carried between worlds. It is simple enough to read in one file (`planet/soils.py`).

### 3.1 Parent material

Each rock gets a **texture** (sand, loam, clay) and a **base richness** (0–1: how much calcium, magnesium and potassium it releases):

| Parent | Texture | Base richness |
|---|---|---|
| sandstone, quartzite, sand cover, dunes | sand | 0.2 |
| granite, craton, orogen gneiss | sandy loam | 0.35 |
| shale, sediment-born continent | clay | 0.55 |
| arc, tuff | loam | 0.8 (ash: also "andic") |
| hotspot and ocean basalt, flood basalt | clay | 0.85 |
| limestone, dolomite | clay (thin residue) | 0.9 |
| evaporite | – | salt |
| coal | – | acid, 0.2 |
| **loess** (≥ 1 m, §3.6) | silt | 0.8 |
| **alluvium** (floodplain share, aggrading coastal plain) | silt loam | 0.7 (fresh sediment) |
| **till** (glaciated ≤ 2 Myr ago, not steep) | loam, stony | 0.5 |

Loess, alluvium and till override the rock where they apply.

### 3.2 Erosion, depth and soil age

A soil is as deep and as old as erosion lets it be. Rock turns into soil fastest under a thin soil, P(h) = P₀ e^(−h/h₀) (Heimsath et al. 1997), and erosion E strips the top, so the steady depth is h* = h₀ ln(P₀/E) and the soil's **age** (residence time) is τ = h/E:
- **E** is estimated from the world's terrain with the run's own laws: ∝ relief (vegetation's `relief`) × the run's rain factor ((P/800)^0.8), scaled so shields wear at ~0.001–0.01 mm/yr and steep wet mountains at ~0.5–2 mm/yr, as on Earth (decision 2).
- **P₀** ~0.05–0.2 mm/yr, faster where warm and wet; h₀ ≈ 0.5 m. Depth is capped at 3 m.
- **Resets** cap the age: `glaciated_myr` (the ice scraped the soil off), the eruption age on lavas, arcs and hotspots, the aggradation age on alluvium; the depth grows towards h* over that age.

So shields and old plains get deep, ancient soils, mountains thin young ones, and a just-deglaciated shield bare rock and till.

### 3.3 Weathering stage

The weathering stage is **W = log₁₀(leaching water × warmth × age)**: runoff (mm/yr, the water that passes through the soil) × e^(0.07 (T − 15 °C)) × τ, in metres of warm water. It sorts the humid soils:
- young brown soil (W low) → brown forest soil (clay washed down) → red clay (bases gone, acid) → leached red tropical soil (only iron, aluminium oxides and kaolinite left).
- In dry climates runoff is small, so W stays low however old the surface. Lime and gypsum stay in the soil (caliche, desert pavement), and salts where the water evaporates.

**Fertility** = base richness × e^(−W/W₀) (leaching removes it), + loess, alluvium and ash bonuses (fresh minerals), − salt, − waterlogging, + organic matter (pass 2, for the display only, §4.2). So a deep red tropical soil is poor, ash and black earth rich: Earth's well-known pattern.

**Water capacity** = available water per metre (sand ~70 mm/m, loam ~150, silt and loess ~200, clay ~130, peat ~300) × depth, split into the vegetation's two layers: top = AWC × min(h, 0.3 m), deep = AWC × clip(h − 0.3, 0, 1.2 m). It is renormalised once, so Earth's land mean stays at today's 50/150 mm and the vegetation's Earth calibration doesn't shift on average (it only moves where soils differ).

**Drainage** from slope, texture (clay drains slowly), the flooded share and permafrost.

### 3.4 Soil carbon and peat (pass 2, after vegetation)

As vegetation §4.4 laid out (CENTURY's logic):
- **Soil carbon** = litter (NPP) / decay, with decay ∝ 2^((T − 10)/10) × a moisture curve (slow when dry or waterlogged) × the unfrozen share of the year. Grass puts its litter into the soil as roots, forest on the surface (partly burnt, `fire_return`), so grassland stores more per unit NPP: that makes black earths (mollic: ≥ ~10 kg C/m² and a grass share).
- **Peat** grows on the flooded share, where litter decays ~10× slower, towards Clymo's (1984) equilibrium M* = input / α (α ~ 10⁻³/yr, reached in a few kyr); depth = M* / ~50 kg C/m³; peat moss (`Sph`) slows decay further. Histosol where peat ≥ 0.4 m.

### 3.5 Permafrost

Ground temperature = the air's annual mean + a snow offset (the snowpack from `climate.months` insulates: up to ~+6 °C under deep early snow; after Smith & Riseborough 2002) − a little under peat and moss. Continuous below ~−5 °C, discontinuous −5 to −2, sporadic −2 to 0. It replaces vegetation's `temp < −2` stand-in in `flooded()`.

### 3.6 Loess

- **Sources:** loose cover on dry, bare ground (P/PET < 0.2, plant cover < 30%), most from dune fields and dry lake beds; and **glacial outwash** beside today's ice margins or ground glaciated within ~2 Myr.
- **Transport:** downwind along the seasonal winds (`wind_jan/jul_e/n`), decaying over ~500 km, settling ∝ plant cover (grass traps dust), in a few sweeps on the grid.
- **Thickness** = deposition × a fixed ~1 Myr, scaled so a big source gives tens of metres nearby (China's Loess Plateau reaches ~300 m; the Mississippi's and Danube's loess a few to tens of metres).

The crudest part; PW-037 would replace its glacial half (decision 4).

### 3.7 Climate memory

A soil integrates its climate over its age: thousands of years for a young soil, millions for an oxisol. Today's climate alone misses relic soils, like Australia's laterites under a now-dry sky. A world from a run can average the keyframes' stored annual `temperature` and `precipitation` over each soil's age for W and the lime and salt rules (decision 3). Earth and `generate` worlds use the present climate.

---

## 4. What soils hand back, and in what order

### 4.1 To vegetation

- **Water capacity:** `cap1`, `cap2` per cell from §3.3, replacing `TOP_MM`/`DEEP_MM` and the `steep` thinning in `vegetation.site`, and `SOIL_THIN`/`DEEP_SOIL` in the zoom.
- **Fertility factor** in the light-use efficiency: f_soil = 0.85 + 0.25 × fertility (0.85–1.1), renormalised so Earth's land NPP stays where it is (63 Pg C/yr on observed climate). It is a nudge: heath and conifers on poor podzols, and richer savanna on basalt, both already mostly come from the climate (decision 6).
- **Permafrost** for `vegetation.flooded` (§3.5).

### 4.2 Order (no circularity)

The world's finishing (`world.finish`) becomes:
1. climate, erosion, rivers and lakes (as now);
2. **soils pass 1, mineral:** parent, erosion, depth, age, W, texture, water capacity, fertility, drainage, permafrost, loess. It needs only geology and climate.
3. vegetation (both its runs, the cheap one for the climate feedback and the full one), reading pass 1;
4. **soils pass 2, organic:** soil carbon, peat, the mollic test, then the classification;
5. the rest as now (waves, seasons, sea, satellite).

Pass 2 never changes what vegetation saw, so there is no loop. On Earth organic matter does raise water capacity and fertility (more NPP, more carbon, more water, more NPP); one fixed-point pass would capture it for a second vegetation run (~1.5–3 s at L7) and a few percent. The lean is to skip it: organic matter shows in the displayed fertility only (decision 5). The climate's own soil carry-over (`TUNE["soil_mm"]` = 150 mm) stays fixed for the same reason.

### 4.3 In the run: coal from peat (PW-212)

Replace the swamp rule with **peat accumulation**: the flooded share (`vegetation.flooded` on the run's flow, lakes and ice; cheap) × NPP × the share that escapes waterlogged decay, laid down as coal **where sediment is piling up** (`net ≥ 0` in `deposit()`: a sinking or aggrading basin buries the peat; elsewhere it rots or erodes; decision 7). `coal_rate` is rescaled to keep a typical run's coal volume. Coal then also comes from cool peatlands. No soil layer is added to the run, but its strata change: golden hashes and the scorecard need updating.

---

## 5. Where it's computed, and cost

| Where | What | Cost (estimate) |
|---|---|---|
| **Run** | only the coal-from-peat rule | negligible (one `flooded()` per climate update) |
| **World** (slice, Zoom button, finished worlds) | both passes, full layers | ~0.1–0.3 s at L7 (element-wise, plus ~20 loess sweeps); reading ~50 keyframes of climate for §3.7 ~0.2 s. Worlds take 13–28 s at L7 today. |
| **Regional zoom** | both passes per pixel, around the zoom's vegetation step | ~0.3–0.5 s for 250k pixels; zooms take ~10–15 s at L7 |
| **Glacial time zoom** | none | – |
| **World finished from a time zoom** | as any world | its `glaciated_myr` and ice are the frame's, so a just-deglaciated shield gets fresh thin soils |

**Zoom pixels** use the same rules on local inputs: slope for erosion and depth (thin on ridges, thick colluvium at slope feet), `river_dist` and discharge for alluvium strips, `twi` and `wetland` for gleys and peat, the zoom's own glaciers for bare ground and till below their tongues, `surface_rock` and `landform` for parent rock, the lapse-corrected temperature for mountain podzols and permafrost, and the coarse cell's loess interpolated. Soils have no history, so nothing pulls the pixels back to the coarse cell: an alpine cell's zoom shows brown valley soils, thin slopes and frozen summits.

**Time zoom:** skipped; nobody looks at a soil map per 2 kyr frame. What it should give soils is PW-037's imprint (maximum ice, till, outwash, loess), read by the finished world.

---

## 6. Viewer, hover and game attributes

- **Globe:** a `soil` layer (WRB-like colours: oxisol red, chernozem black, podzol ash-grey, aridisol buff), plus pickable `soil_depth`, `soil_fertility`, `soil_water`, `soil_carbon`, `peat_depth`, `permafrost`, `loess`. Same in the zoom viewer.
- **Hover card:** "Black earth (Chernozem / Mollisol) on loess 6 m · 1.4 m deep · fertility 0.9 · holds 210 mm · 18 kg C/m² · well drained". Each type has a one-line description in the legend, like the vegetation types ("Deep, dark, crumbly and rich: the world's breadbaskets").
- **Satellite view:** bare ground coloured by soil type (red tropical soils, black earths, grey podzols, white salt) instead of today's climate-and-rock guess (relates PW-224).
- **Game attributes**, light and computed from the fields (as vegetation decision 11): **farming** (fertility × water × drainage × slope × growing season), **building ground** (rock good; peat, cracking clay, thawing permafrost, salt bad), **digging** (depth, stones), **mud season** (clay + wet months), and **peat fuel, brick clay, ironstone** (laterite). With PW-206 / PW-100.

---

## 7. How to check it: Earth as an analogue

### 7.1 Data

- **SoilGrids 2.0, WRB most probable group** (ISRIC, **CC BY 4.0**): `files.isric.org/soilgrids/latest/data/wrb/MostProbable.vrt` and its overviews `MostProbable.vrt.ovr` (**32 MB**, a BigTIFF of deflate-compressed tiles, levels from ~1 km down; 30 WRB groups, legend in `MostProbable.qml`). One coarse level (~4–8 km) is a few MB by HTTP range request; a short `zlib` + `numpy` reader handles it (no GDAL needed). Each cell takes the area mode, grouped into our 19 types.
- **Alternative, HWSD v2.0** (FAO & IIASA 2023): a 22 MB zipped 1 km raster (1.9 GB unpacked) plus a 9 MB Access database; CC BY-NC-SA 3.0 IGO (non-commercial). Harder to read, less free.
- **Earth's parent rock:** the Earth world has no rock record (PW-132). **GLiM** (Hartmann & Moosdorf 2012; 0.5° raster, 38 kB, CC BY 3.0) maps lithology classes onto our rocks.
- **Earth's glaciation:** `glaciated_myr` ≈ 0.02 inside the Last Glacial Maximum ice, from an observed LGM mask (or the Earth time zoom's maximum, with PW-033's errors). Without it Canada and Scandinavia count as ancient surfaces.

### 7.2 Insulated from the model's climate, as vegetation was

Vegetation was tuned on Earth's **observed** climate (`tools/veg_check.py`: 62% agreement on it, 44% on the model's), so the climate's errors weren't tuned in. Soils do the same: `tools/soil_check.py` runs on Earth's terrain with the observed climate, the vegetation computed on it, GLiM rock and the LGM mask, and tunes only on that. The model-climate run is reported, not tuned. When PW-013 changes the rain, the tuned scores don't move.

### 7.3 Checks ("good enough", as an analogue)

| Check | Observation | Good enough |
|---|---|---|
| Type agreement, area-weighted, ~10 groups (organic, frozen, thin, desert, steppe and black earth, podzol, temperate forest, tropical red, wet and alluvial, young) | SoilGrids WRB | ≥ 50% on observed climate (cf. vegetation 62%, Köppen 71%) |
| Type placement | Ferralsols in the Amazon and Congo, Chernozems from Ukraine to Kazakhstan and the Great Plains, Podzols across the boreal belt, Andosols on arcs, Vertisols on the Deccan and in Sudan, Calcisols and Gypsisols in deserts | each present in its main regions |
| Soil carbon, top metre | ~1500 Pg C | 1000–2200 |
| Peat area and carbon | ~4 Mkm², ~500 Pg C | 2–8 Mkm²; 200–900 Pg C; boreal and tropical both present |
| Permafrost region | ~20 Mkm² | 13–28 Mkm²; the southern limit within ~5° |
| Loess | China's plateau, central Europe, the Mississippi valley, the Pampas | present downwind of deserts and old ice |
| NPP after the soil hand-off | 63 Pg C/yr today | unchanged within ±5%; potential vegetation agreement not lower |

**Not targets:** pixel agreement of any one group, farmland soils changed by people, and errors from known climate misses.

**Generated planets:** pytest envelope tests (no soil on ice, shares of each type within broad ranges, thin soils on steep ground, deep old soils on shields) and golden hashes once stable.

---

## 8. Insulation from the run work in flight

Soils keep no state and recompute on whatever world exists. After each of these lands:
- **PW-013 (rain):** the Earth tuning is insulated. On generated worlds desert, steppe and leached-soil shares follow the new rain: re-run the model-climate check and look at a showcase world.
- **PW-293 (sea level):** moves how much low coastal plain is land (alluvium, salt). Re-look at the type shares on the health seeds; nothing to retune.
- **PW-308 (runs barely glaciate):** with little run ice, `glaciated_myr` is mostly "never", so little till, glacial loess or young glacial soil. Right for those runs; re-check once runs glaciate again. Also, `glaciated_myr` is the run's orbit-averaged ice, not an ice-age maximum, so LGM-style resets need PW-037 or a world finished from a time zoom.
- **Coal (§4.3)**, the one run change, should follow PW-308 (both move the scorecard).

---

## 9. Staging and decisions

### 9.1 Steps

| Step | What | Effort | Depends on |
|---|---|---|---|
| 1 | `planet/soils.py` pass 1: parent material, erosion estimate, depth and age, W, texture, water capacity, fertility, drainage, permafrost; world layers in `store.LAYERS`; unit tests | m | – |
| 2 | Loess: sources, wind transport, deposition | s | 1 |
| 3 | Pass 2 and the hand-off: vegetation reads `cap1/cap2`, `f_soil` and permafrost; soil carbon, peat, mollic, the classification and legend; `world.finish` order; renormalisation | m | 1 |
| 4 | Earth check: SoilGrids overview reader, GLiM, LGM mask in `tools/earth_data.py`; `tools/soil_check.py` on observed and model climate; tuning to §7 | m | 3, draft earth-soil-data |
| 5 | Viewer: soil layers, legend, hover card | s | 3 |
| 6 | Zoom: per-pixel passes around the zoom vegetation, replacing `SOIL_THIN`/`DEEP_SOIL`; zoom layers | m | 3 |
| 7 | Run: coal from peat (PW-212); golden hashes; scorecard | s | 3 (PW-308 preferably first) |
| 8 | Climate memory from keyframes (§3.7), if decision 3 is B | s | 1 |
| 9 | Game attributes and satellite soil colours (with PW-206, PW-224) | s | 5 |

Steps 1–5 give a reviewable world soil map with Earth numbers (~1.5–2 agent-days). Steps 6–9 can run in parallel after that.

### 9.2 Decisions for the owner

1. **The type set.**
   - (A) 19 WRB-based types with player names, WRB and USDA names on the hover card.
   - (B) USDA's 12 orders: fewer, but no salt, sand or limestone soils, and aridisols lumped together.
   - (C) ~30 WRB groups: matches SoilGrids one to one, but many differ in ways a world map can't show.

   **Lean A.**
2. **Where the soil's age and erosion rate come from.**
   - (A) Estimated in the world from relief and rain with the run's erosion laws (§3.2), capped by glaciation, eruption and deposition ages. No run change; works for Zoom-button worlds.
   - (B) Store the run's own denudation rate per keyframe (+1 byte per cell per frame, ~80 MB per Gyr at L7).

   **Lean A**, checked once against the run's own erosion on a sliced world.
3. **Climate memory.**
   - (A) Present climate only.
   - (B) For worlds from runs, the keyframes' climate averaged over each soil's age (§3.7), so relic laterites and old salt survive a climate change; present climate for Earth and `generate`.

   **Lean B**, a small step after the rest works.
4. **Loess.**
   - (A) World-level dust from today's deserts and recent ice margins (§3.6).
   - (B) Wait for the time zoom's glacial imprint (PW-037).
   - (C) A now; PW-037 replaces the glacial source when it lands.

   **Lean C.**
5. **Feedback loop.**
   - (A) One-way: mineral soil → vegetation → organic soil; organic matter shows in the displayed fertility only; the climate's 150 mm carry-over stays fixed.
   - (B) One fixed-point pass so organic matter also raises vegetation's water and fertility (+1.5–3 s per L7 world).

   **Lean A.** Nudge, don't loop.
6. **How strongly fertility moves plants.**
   - (A) A mild LUE factor, 0.85–1.1, renormalised on Earth.
   - (B) Real nutrient limitation (0.5–1.1): heath and poor forests from soils, not climate. That needs retuning the vegetation.
   - (C) None: fertility only for players.

   **Lean A.**
7. **Coal from peat in the run.**
   - (A) Peat accumulation where sediment is piling up (`net ≥ 0`), replacing the elevation, rain and `veg` cuts.
   - (B) Peat accumulation, keeping the `e < 250 m` cut.

   **Lean A**: burial, not altitude, is what turns peat into coal.

(Earth data is SoilGrids rather than HWSD for licence and format, §7.1; not a decision unless the owner prefers HWSD.)

---

## References (brief)

Clymo 1984 (peat accumulation); Heimsath et al. 1997 (soil production); Parton et al. 1987 (CENTURY); Smith & Riseborough 2002 (permafrost and snow); Jenny 1941 (soil-forming factors); IUSS Working Group WRB 2022; Soil Survey Staff 1999 (Soil Taxonomy); Poggio et al. 2021 (SoilGrids 2.0); FAO & IIASA 2023 (HWSD v2.0); Hartmann & Moosdorf 2012 (GLiM); Scharlemann et al. 2014 (soil carbon); Yu et al. 2010 (peatland carbon); Obu et al. 2019 (permafrost extent).
