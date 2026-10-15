# Vegetation: proposal (PW-186, for owner review)

*2026-10-14, branch `vegprop`. Implemented in PW-187 once approved. Parent epic PW-184 (life and the land surface); siblings PW-185 (soils) and PW-188 (coastal and shallow-sea life). Numbered decisions for the owner are in §9.*

**In one paragraph:** each land cell (and each zoom pixel) gets the **fractions of 21 plant functional types**: tropical evergreen trees, boreal larch, C4 grass, peat moss and so on. A plant functional type is a group of plants that behave alike: same leaf habit, height, climate limits and drought strategy. Each type's growth is computed from light, warmth and water. The types compete for space and light, and fire takes back what dry fuel allows. A classifier turns each cell's mix into one of **56 named vegetation types** ("boreal larch taiga", "miombo woodland", "raised bog") for maps, legends and game text. Vegetation then feeds back on erosion, rock weathering, evaporation and (later) temperature through albedo, and it sets soil carbon and peat for PW-185. In the long run it is computed in equilibrium at each climate update (cheap, about 5–10% of run time). In the glacial time zoom it migrates with a lag, so you get refugia. In worlds and zooms it is computed in full detail, downscaled in zooms by slope, aspect, soil and wetness.

---

## 1. What exists today, and what vegetation can use

### 1.1 The current biome map

`climate.biomes()` is a **Whittaker lookup**: a fixed table on *annual mean temperature × annual rainfall* that gives 16 classes, 11 of them vegetated land (tundra, boreal forest, cold desert, temperate grassland / forest / rainforest, hot desert, savanna, tropical seasonal forest, tropical rainforest, alpine/bare rock). (Robert Whittaker's 1975 diagram plots the world's biomes on those two axes.) The zoom calls the same function on its lapse-corrected pixels. Köppen classes (`climate.koppen`, Peel 2007 rules) are separate and stay as they are.

What the lookup can't do:
- **Seasonality.** 600 mm falling in winter (Mediterranean scrub) and 600 mm in summer (savanna) look the same to it. The Köppen classes see seasons, but the biome map doesn't.
- **Fire, soils, groundwater and slope.** Savanna versus forest at the same rainfall, heath on poor sand, gallery forests along desert rivers, and north- and south-facing slopes all come out the same.
- **Mixtures and gradients.** One class per cell; no tree cover or productivity.
- **History.** Nothing lags behind its climate.

### 1.2 The run's "veg" term

The run already has a crude plant cover (`tectonics/earth.py: erode`):
`veg = [t ≥ plants_from] × clip(P/800) × clip((t_warm−5)/10) × land`. It is used twice:
- **erosion:** `k_mult × (1 + 0.6·wet·(1 − veg))`, so bare wet ground erodes up to 1.6× faster;
- **weathering:** `warm × (1 + 0.5·veg)` in the CO₂ sink (roots and soil acids speed up silicate weathering), which closes the long-term carbon-cycle loop.

It also gates coal: swamps need `veg > 0.5`. The proposed model replaces this term with a real cover and productivity, keeping both uses (§4.5).

### 1.3 Climate fields per cell

| Field | Run (sim state, every 4 Myr) | Run keyframe on disk | World | Zoom pixel | Time zoom (500 yr) |
|---|---|---|---|---|---|
| annual, warmest-, coldest-month temperature (`temp`, `t_warm`, `t_cold`) | yes | annual only | yes (+ July/January) | annual and warmest month (lapse-corrected) | yes (shifted each step, recomputed every 10 kyr) |
| rain per half-year (`p_jul`, `p_jan`) | yes | annual only | yes | annual only (PW-139) | yes |
| potential / actual evaporation (`pet`, `aet`), runoff | yes | no | yes | runoff only | in memory |
| cloud, sunshine (per half-year) | computed, not kept | no | yes | no | no |
| humidity, dew point | computed, not kept | no | yes | no | no |
| land ice, lakes and their kind, river flow | yes | yes | yes | yes (finer) | ice yes |
| rock, strata, landform age, glaciated_myr | yes | some | yes | rock yes | frozen |
| tide range, wave power, SST | no | no | yes | interpolated | no |
| slope, aspect, drainage area | cell-scale only | — | — | yes (from the heightmap; drainage area stored) | — |

What vegetation needs and how it gets it:
- **Months.** Nothing is stored monthly, but every month can be rebuilt the way `koppen()` and `pet_months()` already do: a sinusoid between the coldest and warmest month for temperature, and a sinusoid through the two half-year rain rates. Monthly PET (potential evaporation: what a wet surface would evaporate, here Oudin's formula from sunshine and temperature) is `climate.pet_months()`, already written.
- **Derived indices** (all from those months):
  - **GDD5** (growing degree-days above 5 °C, the sum over the year of each day's warmth above 5 °C; the standard "is the summer long and warm enough" measure);
  - **snowpack** (precipitation in months below 0 °C, melted by degree-days, as the zoom's glacier code already does);
  - an **absolute minimum temperature** estimated from the coldest month (BIOME4's empirical fit, `Tmin ≈ 0.006·Tc² + 1.316·Tc − 21.9`), because frost kill, not the monthly mean, limits palms and tropical trees;
  - a **moisture index α = AET/PET** per month from a soil water bucket (§3.1). It runs from 0 (bone dry) to 1 (never water-stressed).
- **Light** (PAR, photosynthetically active radiation: the ~45% of sunlight plants can use) = top-of-atmosphere sun (`climate.insolation`) × clear-sky transmission × (1 − 0.6·cloud). Worlds have cloud. The run computes it in `climate.compute` but drops it: keep the two arrays on the sim.

So **no new climate physics is required**. One helper that builds the 12 months once and shares them is worth writing (draft `climate-monthly-fields`). Seasonal fields in zooms (PW-139) and slope/aspect/wetness indices in zooms (draft `zoom-terrain-indices`) are needed for the zoom step.

### 1.4 Grid sizes

| Grid | Cells | Cell area | Land cells (~30–37%) |
|---|---|---|---|
| L6 | 40,962 | ~12,450 km² (~110 km) | ~13–15k |
| L7 | 163,842 | ~3,110 km² (~55 km) | ~50–60k |
| Zoom | 500 × 500 = 250,000 px | 0.25–16 km² | up to 250k |

---

## 2. The type system

### 2.1 Why this shape

The owner asked for at least ~30 types and well under ~2000. Two layers serve the two jobs:
- **21 plant functional types (PFTs)** are the *state* that the physics computes. Real dynamic global vegetation models (DGVMs) use 5–20: TRIFFID in JULES 5–9, LPJ 10, CLM 15–16, BIOME4 13. Each PFT costs compute and needs parameters that can be checked against something. 21 is at the high end, but our extra types (succulents, heath, peat moss, wetland herbs, two coastal types) are exactly the ones that give maps and games character and that standard DGVMs lump together.
- **56 named vegetation types** (plus 4 non-vegetated classes) are *derived* each time from the PFT mix, structure (cover, height, LAI) and site (climate, wetness, elevation, salt). They cost nothing to add, so the list can grow to 80 later without touching the physics.

A single list of ~60 directly modelled types would need ~60 sets of physiological parameters with no data to tune them against, and would fragment competition (60 kinds of tree all within 1% of each other). A list of ~500 would effectively be species, which belongs to PW-103.

**Jargon used below:**
- **LAI** (leaf area index): m² of leaf per m² of ground. Desert ~0.2, grassland 1–3, temperate forest 4–6, rainforest 6–8.
- **Evergreen / summergreen / raingreen:** leaves all year, leaves only in the warm season (oak, larch), leaves only in the wet season (drought-deciduous, like the teak forests).
- **C3 / C4 / CAM:** three kinds of photosynthesis. C3 is the ancestral one (trees, wheat, cool grasses). C4 grasses (maize, sugarcane, savanna grasses) concentrate CO₂ and win in hot, bright, seasonally dry climates and at low CO₂. CAM plants (cacti, agaves) open their pores only at night and save water.
- **Sclerophyll:** hard, leathery-leaved evergreen shrubs and trees adapted to summer drought and fire (Mediterranean maquis, chaparral, fynbos).

### 2.2 The 21 PFTs and their climate envelopes

Tc = coldest-month mean temperature; Tmin = estimated absolute minimum (§1.3); GDD5 = degree-days above 5 °C per year; α = AET/PET over the growing season. Limits are where a PFT can *establish*. Inside them it still has to win the competition. Starting values come from LPJ (Sitch et al. 2003) and BIOME4 (Kaplan et al. 2003), and they are tuning knobs, not targets.

| # | Code | PFT | Earth examples | Tc min | Tc max | GDD5 min | Drought tolerance (α min) | Roots | Leaf habit | Max height | Fire response |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | TrBE | tropical broadleaf evergreen tree | Amazon, Congo, Borneo rainforest trees | 15.5 °C (Tmin > 0) | – | – | 0.70 | deep | evergreen | 45 m | killed (thin bark) |
| 2 | TrBR | tropical broadleaf raingreen tree | teak, miombo, baobab | 15.5 °C | – | – | 0.35 | deep | raingreen | 25 m | partly resists |
| 3 | TeBE | temperate broadleaf evergreen tree | live oak, laurel, eucalypt, southern beech | 3 °C (Tmin > −15) | 18.8 °C | 1200 | 0.40 | deep | evergreen | 40 m | eucalypts resprout |
| 4 | TeBS | temperate broadleaf summergreen tree | oak, beech, maple | −17 °C | 15.5 °C | 1200 | 0.50 | deep | summergreen | 35 m | partly resists |
| 5 | TeNE | temperate needleleaf evergreen tree | pines, Douglas fir, redwood, cedar | −2 °C | 22 °C | 900 | 0.30 | deep | evergreen | 60 m | thick-barked pines resist |
| 6 | BoNE | boreal needleleaf evergreen tree | spruce, fir | −32.5 °C | −2 °C | 600 | 0.45 | shallow | evergreen | 25 m | stand-replacing fire |
| 7 | BoNS | boreal needleleaf summergreen tree | larch | – | −2 °C | 350 | 0.35 | shallow (permafrost) | summergreen | 20 m | resists ground fires |
| 8 | BoBS | boreal broadleaf summergreen tree | birch, aspen, alder | – | 5 °C | 350 | 0.45 | shallow | summergreen | 20 m | killed, quick to return |
| 9 | SclS | sclerophyll evergreen shrub | maquis, chaparral, fynbos, mallee | −5 °C | 18 °C | 1500 | 0.20 (summer) | deep | evergreen | 4 m | resprouts; fire-adapted |
| 10 | XerS | xeric (desert) shrub | creosote, saltbush, sagebrush | −35 °C | – | 500 | 0.05 | deep, wide | evergreen or drought-deciduous | 2 m | rarely burns (no fuel) |
| 11 | DecS | cold-deciduous shrub | dwarf birch, willow and alder scrub | – | 5 °C | 150 | 0.35 | shallow | summergreen | 3 m | resprouts |
| 12 | HthS | evergreen dwarf heath shrub | heather, crowberry, Labrador tea | −35 °C | 10 °C | 100 | 0.50 | shallow | evergreen | 1 m | burns; regrows (moor burning) |
| 13 | C4G | C4 grass | savanna and prairie tall grasses | ≥ 22 °C warm-season months (Collatz 1998) | – | – | 0.10 | shallow | raingreen | 2 m | resprouts; main fire fuel |
| 14 | C3G | C3 grass and forbs | steppe and meadow grasses, wildflowers | – | 15.5 °C | 200 | 0.15 | shallow | summergreen | 1 m | resprouts |
| 15 | TunH | tundra graminoids and forbs | sedges, cotton grass, cushion plants | – | 5 °C | 50 | 0.25 | very shallow | summergreen | 0.3 m | resprouts |
| 16 | Succ | succulents (CAM) | cacti, agaves, aloes, euphorbias | 0 °C (Tmin > −10) | – | 2000 | 0.02 | shallow, water-storing | evergreen | 3–12 m | killed (rare fire) |
| 17 | Moss | moss, lichen and soil crust | reindeer lichen, feather moss, desert biocrust | – | – | 0 | 0.00 (dries and revives) | none | evergreen | 0.05 m | killed, slow to return |
| 18 | WetH | wetland emergent herbs | reeds, sedges, papyrus, cattails | – | – | 100 | needs flooding | in water | summergreen (tropics evergreen) | 4 m | resprouts |
| 19 | Sph | peat moss | Sphagnum | – | 18 °C | 50 | needs waterlogging | none | evergreen | 0.1 m | peat fires smoulder |
| 20 | Mang | mangrove tree | red and black mangroves | Tmin > 0 °C (Tc ≳ 15 °C) | – | – | tidal, saline | aerial roots | evergreen | 20 m | – |
| 21 | Salt | salt marsh halophytes | cordgrass, glasswort, saltbush on tidal flats | – | – | 100 | tidal, saline | shallow | summergreen | 1 m | – |

Other PFT parameters (one row each in a table in code): light-use efficiency (C3 trees ~1.1, C4 ~1.4 g C per MJ of absorbed PAR, before stress), optimal and limiting temperature for growth, a growing-season start rule (GDD for summergreen, α > 0.35 for raingreen), maximum LAI, leaf and wood turnover times, wood density / allometry (for height and biomass), fire resistance (0–1) and resprouting, albedo with and without snow, and the share of roots in the top soil layer.

**Deliberately absent:** crops and pasture (no humans; PW-103/PW-098 later), and bamboo, palms and tree ferns. These are folded into TrBE/TrBR for now; any of them could become PFT 22+ later, e.g. for a fantasy flora.

### 2.3 Named vegetation types (derived)

**How they're derived.** A cell is classified in order, first rule wins (the same idea as BIOME4's biome assignment from its dominant PFT and LAI, and the IGBP land-cover legend's cover thresholds):
1. **Non-vegetated:** ice, lake, or total plant cover under 5% (split by temperature and terrain).
2. **Coastal:** mangrove or salt-marsh PFTs over 30% of the cell.
3. **Wetland:** wetland herbs plus peat moss over 40%, or the hydrology says flooded (lake margin, floodplain, delta, low-gradient wet ground; §3.6).
4. **Forest:** tree cover ≥ 60%. Named by the dominant tree PFTs and a climate qualifier (montane, cloud, rain).
5. **Woodland / savanna:** tree cover 10–60%. Named by the tree PFT and the herb layer (C4 vs C3).
6. **Shrubland:** shrubs over herbs, tree cover < 10%.
7. **Grassland / herbland:** herbs dominate.
8. **Sparse:** total cover 5–25%, named by climate.

"Alpine" versus "arctic" comes from where the cell sits relative to its latitude's treeline: high ground versus high latitude.

**The list (56 vegetated + 4 non-vegetated).** "Mix" gives the defining PFTs, with typical shares. The description is the game-facing line. Travel, timber and other game attributes are computed continuously (§7), not fixed per type.

| # | Named type | Group | Mix / condition | Game-facing description |
|---|---|---|---|---|
| 1 | Tropical lowland rainforest | tropical forest | TrBE ≥ 70%, LAI ≥ 6, no dry month | Towering three-layer canopy 40 m up, dim and humid at ground level; vines, buttress roots, endless insects. Slow going, few sightlines. |
| 2 | Tropical montane cloud forest | tropical forest | TrBE dominant, t_warm < 20 °C, cloud ≥ 70% | Gnarled, moss-draped trees in near-constant fog on tropical mountains; epiphytes, orchids, dripping wet. |
| 3 | Tropical monsoon (semi-evergreen) forest | tropical forest | TrBE + TrBR, 2–4 dry months | Tall forest that partly drops its leaves in the dry season; teak and sal, bamboo thickets. |
| 4 | Tropical dry deciduous forest | tropical forest | TrBR ≥ 60%, 5–7 dry months | Leafless and dusty in the dry season, green and dense in the rains. |
| 5 | Tropical swamp forest | tropical forest | TrBE + flooding (WetH under canopy) | Flooded forest along big rivers; travel by boat for half the year. |
| 6 | Tropical peat swamp forest | tropical forest | TrBE + Sph/peat, waterlogged, low relief | Forest on metres of black peat; tea-coloured water, smouldering fires in drought years. |
| 7 | Tropical thorn woodland | tropical woodland | TrBR 20–40% + XerS + C4G, 7–9 dry months | Low, spiny, drought-deciduous scrub-forest; acacia, cactus-like euphorbias. |
| 8 | Moist savanna woodland | savanna | TrBR 30–60% + C4G, frequent fire | Open woodland over tall grass (miombo, cerrado); burns most years, so the trees have thick bark. |
| 9 | Dry savanna | savanna | TrBR 10–30% + C4G | Scattered flat-topped trees in a sea of grass; big herds and their predators. |
| 10 | Tropical grassland | savanna | C4G ≥ 70%, trees < 10% (fire or seasonal flooding) | Open tall-grass plains to the horizon, burned and regrown each year. |
| 11 | Seasonally flooded grassland | savanna | C4G + WetH, flooded in the wet season | Vast flats that become shallow lakes each wet season (Pantanal, Sudd); birds, caimans, cattle-country. |
| 12 | Tropical alpine (páramo) | alpine | C3G + HthS + TunH, tropical latitude above treeline | Cold, misty grassland with giant rosette plants; frost every night, sun every day. |
| 13 | Succulent desert | desert | Succ ≥ 20% + XerS, warm | Columnar cacti or tree-aloes over bare stony ground; fog or rare rain. |
| 14 | Hot desert scrub | desert | XerS 5–25%, warm | Creosote-bush or saltbush spaced metres apart on gravel; water is everything. |
| 15 | Semi-desert grassland | desert | C4G/C3G + XerS, 15–40% cover | Bunchgrass and scattered shrubs; good grazing after rain, nothing in drought. |
| 16 | Cold desert scrub | desert | XerS (sagebrush-like) + C3G, cold winters | Grey-green aromatic shrubland on high plateaus; snow in winter, dust in summer. |
| 17 | Salt desert scrub | desert | XerS (halophytic) + Salt, on salt pans and closed-lake margins | Succulent saltbushes around white salt flats; brackish water only. |
| 18 | Oasis / desert riparian woodland | desert | TeBS/TrBR/palms along rivers or springs in a desert | A green ribbon of poplars, tamarisk or date palms along a desert river; the only shade for days. |
| 19 | Mediterranean scrub (maquis, chaparral, fynbos) | Mediterranean | SclS ≥ 50% | Dense, aromatic, head-high evergreen thicket; summer fire season, spring flowers. |
| 20 | Mediterranean evergreen woodland | Mediterranean | TeBE (evergreen oak) 30–60% + SclS + C3G | Open stands of evergreen oak or olive over golden summer grass. |
| 21 | Mediterranean pine forest | Mediterranean | TeNE + SclS, hot dry summers | Resinous pinewoods on rocky hills; dry needles underfoot, fire-prone. |
| 22 | Warm temperate evergreen (laurel) forest | warm temperate | TeBE ≥ 50%, humid subtropical | Glossy-leaved evergreen broadleaf forest, misty and lush; camphor, laurel, magnolia. |
| 23 | Warm temperate mixed forest | warm temperate | TeBE + TeBS + TeNE | Varied forest of evergreen and deciduous trees; rich in nuts, fruit and game. |
| 24 | Warm temperate pine forest | warm temperate | TeNE ≥ 50%, warm, frequent ground fires | Open, park-like pine forest over grass, kept open by frequent low fires. |
| 25 | Temperate rainforest | temperate forest | TeNE and/or TeBE, P > 1500 mm, mild maritime | Giant conifers (or southern beeches) dripping with moss; fallen logs everywhere; the biggest timber on the planet. |
| 26 | Temperate deciduous forest | temperate forest | TeBS ≥ 60% | Oak, beech and maple; bare in winter, a blaze of colour in autumn. |
| 27 | Temperate mixed forest | temperate forest | TeBS + TeNE/BoNE | Broadleaves and conifers together; good hunting, good timber. |
| 28 | Temperate conifer forest | temperate forest | TeNE ≥ 60%, drier or montane | Dry, open conifer forest of the mountains and plateaus; ponderosa-like pines, fir higher up. |
| 29 | Montane conifer forest | temperate forest | TeNE/BoNE on mountains below treeline in warm-temperate or subtropical latitudes | Dark fir and spruce on the upper slopes of warm-climate mountains. |
| 30 | Temperate woodland and parkland | temperate woodland | TeBS/TeNE 10–60% + C3G | Open woods and glades; easy travel, good pasture, scattered great trees. |
| 31 | Tall-grass prairie | temperate grassland | C3G + C4G, LAI ≥ 2, moist | Shoulder-high grass and flowers on deep black soil; fire every few years. |
| 32 | Short-grass steppe | temperate grassland | C3G (+ C4G), dry | Short, tough grass under a huge sky; horse country, dust storms. |
| 33 | Shrub steppe | temperate grassland | C3G + XerS, dry and cold | Grass and wormwood or sagebrush; harsh winters. |
| 34 | Forest steppe | temperate woodland | TeBS/BoBS groves 10–30% + C3G | Islands of birch or oak in a grassland sea, at the forest's dry edge. |
| 35 | Heathland and moorland | temperate shrubland | HthS ≥ 40%, mild wet maritime, poor soil | Purple heather and wind; bog pools in hollows; sheep and grouse. |
| 36 | Temperate scrub and thicket | temperate shrubland | DecS/SclS after fire or on thin soil | Bramble, hazel and thornbush; tough going off the paths. |
| 37 | Boreal spruce-fir taiga | boreal forest | BoNE ≥ 60% | Dark, endless spruce forest over moss; mosquitoes in summer, deep snow in winter. |
| 38 | Boreal larch taiga | boreal forest | BoNS ≥ 50%, extreme continental (Tc < −35 °C), permafrost | Sparse larch that turns gold and drops its needles; the coldest forest on the planet. |
| 39 | Boreal birch-aspen forest | boreal forest | BoBS ≥ 40% (young, after fire) | Bright, white-trunked forest regrowing after a fire; spruce coming up underneath. |
| 40 | Boreal mixed forest | boreal forest | BoNE + BoBS + TeBS (southern taiga) | Spruce and fir with birch, aspen and the odd lime or oak at the southern edge. |
| 41 | Lichen woodland | boreal woodland | BoNE 10–40% + Moss (lichen) | Widely spaced spruce on a pale carpet of reindeer lichen; caribou winter range. |
| 42 | Forest-tundra | boreal woodland | trees 5–20% + DecS + TunH at the treeline | The treeline: stunted trees in sheltered hollows, tundra between. |
| 43 | Shrub tundra | tundra | DecS ≥ 30% + TunH | Knee- to head-high willow and dwarf birch; thick, wet going in summer. |
| 44 | Tussock and sedge tundra | tundra | TunH ≥ 40%, wet | Ankle-breaking tussocks and wet sedge meadows over permafrost; birds by the million in summer. |
| 45 | Dwarf-shrub and lichen tundra | tundra | HthS + Moss + TunH, drier | Low heath and lichen; dry walking, wide views. |
| 46 | Polar desert and fellfield | tundra | cover < 25%, GDD5 < 50 | Frost-shattered stones with scattered moss and cushion plants; nearly lifeless. |
| 47 | Alpine meadow | alpine | C3G/TunH above treeline (temperate) | Flower-filled summer pastures above the forest; snow until June. |
| 48 | Alpine scrub (krummholz) | alpine | DecS/HthS + stunted conifers at treeline | Wind-flattened, twisted trees and scrub; impassable in places. |
| 49 | Alpine fellfield and scree | alpine | cover < 25%, mountain | Rock, scree and lichen between the meadows and the ice. |
| 50 | Freshwater marsh and reedbed | wetland | WetH ≥ 50%, fresh | Reeds taller than a person around lakes and in deltas; wildfowl, fish, fever. |
| 51 | Temperate and boreal swamp forest | wetland | TeBS/BoNE/BoBS with flooding | Alder, cypress or black spruce standing in water. |
| 52 | Raised bog | wetland | Sph ≥ 50%, rain-fed, cool and wet | A dome of living moss over metres of peat; treacherous pools, preserved bodies. |
| 53 | Fen | wetland | WetH + Sph, groundwater-fed | Sedge and moss over peat, fed by springs; richer than bog, still soggy. |
| 54 | Permafrost peatland (palsa and polygon mire) | wetland | Sph + TunH on permafrost | Frost-heaved peat mounds and polygon ponds; firm in winter, a maze in summer. |
| 55 | Mangrove forest | coastal | Mang ≥ 30%, tidal, warm | Stilt-rooted trees in tidal mud; crocodiles, crabs, a maze of creeks. |
| 56 | Salt marsh | coastal | Salt ≥ 30%, tidal, cool–temperate | Flat green marsh cut by tidal creeks, flooded at spring tides; salt and wildfowl. |
| 57 | Ice | non-vegetated | land ice | – |
| 58 | Bare rock and scree | non-vegetated | cover < 5%, steep or high | – |
| 59 | Barren desert (sand or stone) | non-vegetated | cover < 5%, dry | Dunes or gravel plains with no plants at all. |
| 60 | Lake | non-vegetated | lake cell | – |

Riparian and gallery forest outside deserts (forest strips along rivers through savanna and steppe) shows up in zooms as a pattern, not a cell class: a 55 km cell is too coarse for a river strip (§3.7). Coastal dune grass and sea cliffs are zoom patterns too.

### 2.4 Layers stored per cell

**Per PFT** (21 layers): `veg_frac_<code>`, 0–100% of the cell, uint8. This is the core state; everything else is derived.

**Per cell, summary:**

| Layer | Units | Type | Meaning |
|---|---|---|---|
| `vegetation` | id | u1 | named type (§2.3); legend `vegetation` |
| `tree_cover` | % | u1 | woody canopy cover of trees (cf. MODIS VCF) |
| `cover` | % | u1 | all plant cover (1 − bare) |
| `lai_jul`, `lai_jan` | m²/m² | u1 (×0.1) | leaf area in each half-year (phenology; drives the "satellite" colours, PW-083) |
| `canopy_height` | m | u1 | height of the tallest layer |
| `npp` | g C/m²/yr | u2 | net primary productivity (§3.2) |
| `biomass` | t C/ha | u2 | living carbon, mostly wood (timber) |
| `fire_return` | yr | u2 | mean years between fires (log scale); 0 = never |
| `stand_age` | yr | u2 | mean time since the last stand-replacing disturbance |
| `litter_c` / `soil_c` | kg C/m² | u1 | handed to PW-185 (owner of soil carbon and peat) |

**Memory and disk** (fractions as whole percent):

| Where | What | L6 | L7 | Zoom (500²) |
|---|---|---|---|---|
| In memory while computing | 21 PFTs × ~8 float32 state arrays | 28 MB | 110 MB | 170 MB (land pixels only: less) |
| World JSON (inline text) | 21 fractions + 11 summary layers | +1.5–2.5 MB (now ~5–11 MB) | +7–12 MB (now 30–45 MB) | – |
| Run keyframes (`.bin`) | `vegetation`, `tree_cover`, `npp` (3 × u1) | 120 kB per frame, 31 MB per Gyr | 0.5 MB per frame, 123 MB per Gyr (now ~1.5 GB) | – |
| Zoom | `vegetation`, `tree_cover`, `cover`, `lai`, `canopy_height`, `npp`, `fire_return` (7 layers, 1–2 bytes) | – | – | ~2 MB (now 11–12 MB) |
| Zoom with all PFT fractions | +21 × u1 | – | – | +5 MB (decision 9) |
| Time zoom | `vegetation`, `tree_cover` per 2 kyr frame | 41 MB per Myr | 164 MB per Myr | – |

---

## 3. The model

### 3.1 Months, snow and soil water

For each land cell, build 12 months of temperature, rain, PET and PAR (§1.3). Run a **two-layer soil water bucket** for two to three model years until it repeats:
- rain (or snowmelt) fills the top layer (0–0.3 m), which overflows into the deep layer (0.3–1.5 m), which overflows to runoff;
- plants draw from each layer by their root shares: grasses mostly from the top, trees and shrubs from both;
- water-holding capacity comes from PW-185 soils (texture × depth). Until soils exist, use a default of ~150 mm, the same as climate's `soil_mm`, thinned on steep or rocky cells and deepened on alluvium.

The two layers are the classic explanation of tree–grass coexistence in savannas (Walter's hypothesis): grasses use the frequent topsoil water, trees the deeper water. That gives each PFT its own monthly water stress α_p, not one per cell.

Snow: precipitation in months below 0 °C accumulates as snowpack and melts by degree-days (the time zoom's and zoom glacier code's rule). It insulates (relevant to permafrost and peat) and masks albedo (§4.2).

### 3.2 Productivity: a light-use-efficiency scheme

**Choice: light-use efficiency (LUE) with PFT-specific stress factors**, the approach of the CASA model and of MODIS's own NPP product (MOD17). Per PFT, per month:

```
GPP_p,m = ε_p × fAPAR(LAI_p,m) × PAR_m × f_T,p(T_m) × f_W,p(α_p,m) × f_soil
NPP_p   = Σ_m GPP_p,m − R_p           (autotrophic respiration)
```

- **GPP** (gross primary productivity) is what photosynthesis fixes. **NPP** (net primary productivity) is what is left after the plant's own respiration: the carbon available for leaves, wood, roots and seeds. Land NPP on Earth is ~56 Pg C/yr, about half the GPP (~120).
- **fAPAR** = 1 − e^(−0.5·LAI): the share of light the canopy catches (Beer's law).
- **f_T**: a hump between the PFT's minimum, optimum and maximum temperatures. C4 has a hotter optimum and a higher efficiency in heat and bright light. Below 0 °C there is no growth, and summergreen PFTs get none outside their leaf season.
- **f_W** = clip((α − α_min)/(1 − α_min)): the PFT's drought tolerance from §2.2.
- **f_soil**: fertility from PW-185 (0.5–1), default 1. Nutrients are otherwise ignored.
- **Respiration** R: a temperature-dependent maintenance cost on the standing biomass (Q10 ≈ 2) plus 25% growth respiration. This is what makes NPP/GPP fall from ~0.5 in boreal forest toward ~0.3–0.4 in hot rainforest, as measured.
- **LAI** is not free. As in BIOME4, each PFT's LAI is the value that **maximises its NPP given the water**: more leaf catches more light but transpires more and dries the soil. The search is a short golden-section search (6–8 evaluations).
- **CO₂** (optional, decision 12): the run's CO₂ index nudges C3 efficiency (~+0.3 per doubling, a "fertilisation" factor) and water use. At low CO₂ C4 wins at cooler temperatures (the crossover temperature falls, after Ehleringer 1997). This lets icehouse and greenhouse eras look different.

**Why this and not the alternatives:**
- The **Miami model** (Lieth 1975: NPP from annual T and P) is one line, but it has no PFTs, no seasons and nothing to compete with.
- **LPJ/CLM-style biochemical photosynthesis** (Farquhar/Collatz equations, daily steps, nitrogen) is the real thing, but costs 30–100× more. It needs daily weather we don't have (PW-156), and its extra accuracy is lost on our diagnostic, sinusoidal climate.
- LUE matches the data we'd validate against (MOD17 is itself LUE-based), has a dozen parameters per PFT with published values, and vectorises well in numba.

### 3.3 Competition and cover: TRIFFID-style dynamics

Fractions move by **Lotka–Volterra competition with a height hierarchy**, the scheme of TRIFFID, the vegetation model in the UK Met Office's JULES and HadCM3:

```
dν_p/dt = (λ_p × NPP_p / c_p) × ν_p × (1 − Σ_q C_pq ν_q) − γ_p ν_p − fire_p
```

- ν_p is PFT p's cover fraction. λ_p × NPP_p / c_p is how fast it spreads: the share of its NPP spent on spreading, divided by the carbon a square metre of it costs (a forest square metre costs much more than a grass one, so grass recovers in a year and forest in a century).
- **C_pq** is the competition matrix:
  - taller beats shorter: trees shade shrubs, shrubs shade herbs, herbs shade moss (C = 1 for the taller, ~0.2 back);
  - within a height class the higher-NPP PFT gradually displaces the others;
  - moss and lichen live *under* everything, using the light left over.
- γ_p is background mortality (old age, storms, disease, browsing: grazing is implicit here, decision 8).
- **Water caps woody cover.** In seasonally dry climates, maximum tree cover rises with rainfall up to ~650 mm (Sankaran et al. 2005, African savannas). Below that, trees can't close their canopy whatever the competition, which keeps dry savannas open without fire.
- **Establishment:** a PFT can only start (seed fraction 0.5%) in a cell inside its envelope (§2.2) with NPP > 0. In equilibrium mode every viable PFT is available everywhere: over a Myr seeds reach everything. In the time zoom it needs a neighbour that has it (§3.5).

**Equilibrium:** iterate the equations (implicit steps of ~5 model years) until fractions change by less than 0.1% per step. Start from the previous keyframe or a uniform mix, typically 30–100 iterations.

**Bistability is a feature.** With fire (§3.4), forest and savanna are *both* stable over ~1000–2500 mm of rain (Staver et al. 2011): grass fuels fire, fire kills young trees, and closed forest is too humid to burn. Which state a cell is in depends on its history. Warm-starting from the previous keyframe keeps that memory, and an equilibrium from scratch picks the state its neighbours favour (one diffusion term). On Earth that produces the forest–savanna mosaics of Africa and Brazil instead of a straight line.

### 3.4 Disturbance: fire

**GlobFIRM-lite** (Thonicke et al. 2001, LPJ's fire module), extended with per-PFT resistance:
- **Fuel:** litter from leaf and grass turnover, decomposing at a rate set by temperature and moisture. No fire below ~200 g C/m² of fuel, which keeps deserts and polar regions fire-free.
- **Dryness:** a month is fire weather when the topsoil water α_top < 0.3 and, in worlds, humidity is low. The fire season length s = dry months / 12.
- **Burned fraction per year:** GlobFIRM's curve of s (≈ s·e^(…), from ~0 at s = 0 to ~0.5 at a 7–8 month dry season), × fuel availability, × an ignition factor. Lightning is not limiting where there are summer thunderstorms, and is less likely under stable dry winters.
- **Effects:** each PFT loses burned fraction × (1 − resistance) of its cover. Survivors that resprout keep their roots, so grass is back next year, eucalypts and maquis resprout, spruce must start over. The burned share is returned to bare ground for re-colonisation, so frequent fire shifts the mix to grass and fire-tolerant shrubs.
- **Outputs:** `fire_return` = 1 / burned fraction; the stand-age distribution (§3.6).

Peat fires (smouldering) and fires in lightning-free regions are ignored. There is no human burning.

Left out: grazing and browsing as explicit processes (decision 8), windthrow, insects, floods as disturbance (flooded vegetation is handled as a habitat in §3.6), and volcanic eruptions (young lava is handled through soil age, §3.6).

### 3.5 Succession, and how the model runs at each scale

**Succession** is the sequence of communities after a disturbance: bare ground → herbs → shrubs → pioneer trees (birch, aspen) → late trees (spruce, beech). In the cover equations it emerges by itself, because cheap PFTs spread fast and tall ones win slowly. For maps, an equilibrium cell is a *mosaic* of stand ages. With disturbance rate b, the stand age distribution is exponential with mean 1/b (Van Wagner 1978). From it we derive the share of the cell in early, mid and late stages and `stand_age`. A boreal cell burning every 80 years is mostly birch-aspen and young spruce, while one burning every 400 years is old spruce.

**Primary succession** (on brand-new ground) is limited by soil. PW-185's soil age and depth enter f_soil and the water-holding capacity, so young lava, fresh moraines and new deltas start poor.

| Scale | Time step | What runs | Lag? |
|---|---|---|---|
| **Main run** (`simulate`) | at each climate update (4 Myr) | **Equilibrium**, cheap variant: annual means, warm-started from the last update, no stand ages, fire included. Replaces `sim.veg`. Stored per keyframe: `vegetation`, `tree_cover`, `npp`. | No: plants re-equilibrate in centuries, far inside a 4 Myr step. |
| **Glacial time zoom** | 500 yr (each step; potential NPP recomputed at each 10 kyr climate refresh) | **Dynamic**: the cover equations in real years, plus **migration**: a PFT may establish in a cell only from neighbours that have it, at a spread rate of 100–500 m/yr (Holocene tree migration). That is about one L6 cell (~110 km) per 200–1100 years, so a 500 yr step is the natural unit. Newly ice-free ground starts bare. | Yes: forests lag the warming by thousands of years, and **refugia** (cells that kept forest through a glacial) appear and are recorded, for PW-103. |
| **World** (`slice`, Zoom button, finished world PW-091) | once | **Full equilibrium** with monthly water, fire, stand ages, wetlands, named types. A world finished from a time zoom (PW-091) starts from the time zoom's end state and is *not* re-equilibrated, keeping the disequilibrium. | Only via PW-091. |
| **Regional zoom** | once | **Per-pixel equilibrium** (§3.7), starting from the coarse cell's fractions. | No. |

### 3.6 Wetlands, peat and coastal ground (the hydrology link)

- **Flooded** cells and pixels are those with water at or above the ground for part of the year:
  - lake margins (`lake_kind`);
  - floodplains and deltas (high `flow` through low-gradient cells);
  - flat, poorly drained wet ground (α ≈ 1 with little slope, a positive water balance, or permafrost blocking drainage).

  There, WetH, Sph, swamp trees (any tree PFT with a flood-tolerance flag) and Mang/Salt (where saline) can establish, and dryland PFTs are penalised for waterlogging.
- **Peat** accumulates where waterlogged NPP outpaces the slow decay of waterlogged, cold litter. The bookkeeping (kg C/m², bog vs fen) is shared with PW-185, which owns histosols.
- **Salt pans and closed-lake margins** (lake kinds 2 and 3) get halophytic shrubs (salt desert scrub).

### 3.7 Downscaling in the regional zoom

A zoom pixel (0.5–4 km) runs the same per-pixel equilibrium on local inputs:
1. **Temperature** from the zoom's lapse-corrected fields (already there) gives treelines, alpine belts and cloud forest on tropical mountains. PW-101's cold pools and inversions would add frost hollows.
2. **Aspect and slope radiation:** a radiation index from slope and aspect relative to the noon sun. Poleward slopes get less light and lower PET (and are about 1–2 °C cooler in summer at mid-latitudes on 30° slopes), so they stay moister: north-facing forest and south-facing grassland in semi-arid mountains, the classic pattern.
3. **Soil water from slope and position:** steep slopes and ridges have thin soils (low bucket capacity, PW-185); valley floors are deep.
4. **Topographic wetness index** (TWI = ln(upslope area / tan slope), from the zoom's `drainage_area` and heightmap) adds groundwater to the bucket. Hollows and valley floors become riparian forest, fen or marsh.
5. **Rivers:** pixels within a few hundred metres of a river get its water. That makes **gallery forest** through savanna and steppe, and **oasis woodland** along desert rivers.
6. **Coast:** tidal muddy pixels with warm sea get mangrove, cool ones salt marsh (placed together with PW-188). Beaches and barrier islands get dune grass; the existing `wetland` marshes become a vegetation outcome (relates PW-178).
7. **Fire mosaic:** stand age is sampled from the cell's exponential distribution with planet-fixed 3D noise (the zoom's existing approach), so overlapping zooms agree and burn scars have patch shapes.
8. **Fractions stay tied to the coarse cell:** a light correction pulls the mean of each PFT over the cell's pixels back toward the world's fraction, as the zoom already does for elevation, except where the zoom's terrain clearly differs (a peak the coarse cell couldn't see).

---

## 4. Feedbacks

### 4.1 Evapotranspiration (the Budyko / `evap_cool` path)

Today `climate.water_balance` uses **Fu's form of the Budyko curve** with one global `budyko_w = 2.6`. This curve says how much rain goes back to the air (AET) versus runs off, given the ratio PET/P. `_land_finish` warms dry summers and cools wet ones by up to ±1.5 °C (`evap_cool`), based on summer rain alone. Vegetation should set both:
- **Budyko w per cell** from vegetation. Forests with deep roots and large leaf areas give more water back than grassland or bare ground (Zhang et al. 2001 fit w ≈ 2.8 for forest vs ≈ 2.0 for grass in the equivalent form; Donohue et al. 2007 tie it to vegetation). Use w = 2.0 + 1.0 × woody cover (+0.3 for deep-rooted evergreen), renormalised so Earth's land mean stays ~2.6. Effect: forests lower runoff and dry rivers a little; deserts shed more of their rare rain to wadis.
- **`evap_cool`**: replace the summer-rain "dryness" proxy by the summer AET/PET. Irrigated-looking cells are cooler; bare deserts hotter.
- **Not in the first round:** feeding vegetation into the rain kernel's land recycling (`et = 0.5`). The Amazon recycles a large share of its rain, and deforestation studies hinge on it, but in a diagnostic model it is the most likely loop to run away. Revisit after the Earth checks.

### 4.2 Albedo

Albedo is the share of sunlight reflected:
- rainforest ~0.12, conifer forest 0.08–0.12, deciduous forest 0.15–0.18, grassland 0.18–0.25, desert sand 0.30–0.45;
- snow-covered tundra 0.7–0.8, but **snow under boreal conifers only 0.2–0.3**. Dark trees sticking out of the snow are the boreal forest's big climate effect (Bonan 1992).

The climate today has no explicit land albedo: temperature comes from an energy-balance curve by latitude, plus ice cooling. Proposal: a capped local nudge, ΔT = k × (α_ref − α_veg) × absorbed sunshine, with α_ref the bare-ground value the curve was tuned for. Applied per half-year (so snow-masking acts in winter and spring), capped at ±2 °C, and tuned so Earth's temperatures don't move on average. It makes the tundra-taiga edge sharper and lets a "green Sahara" or a deforested continent show a few degrees' difference. Second priority.

### 4.3 Roughness

Forests are aerodynamically rough and slow surface winds. The model's winds are prescribed patterns with deflection by terrain, so there's nothing for roughness to act on. **Skip**, except as an input to the zoom's dune and wave work later (vegetated dunes don't move).

### 4.4 Soil carbon and peat (PW-185)

Vegetation supplies **litter**: leaf, wood and root turnover per year (= NPP in equilibrium). Soil organic carbon in equilibrium is roughly litter / decay rate. The decay rate follows temperature (Q10 ≈ 2) and moisture, and is very slow when waterlogged or frozen (the CENTURY model's logic). This gives:
- black-earth (mollisol) carbon under grassland;
- thin carbon under rainforest (fast decay);
- peat (histosol) and permafrost carbon in the north.

PW-185 owns the soil types. Vegetation hands it `litter_c` and the waterlogging mask, and gets back water-holding capacity and fertility. Earth targets: ~1500 Pg C in the top metre of soil; peatlands ~3% of land holding ~500 Pg C. In the run, wet productive lowlands with peat also replace the `veg > 0.5` swamp rule for **coal** (coal is buried peat).

### 4.5 Erosion and weathering protection (in the run)

Erosion today: stream power × rain factor, with `k_mult = 1 + 0.6·wet·(1 − veg)`. Replace `veg` by **ground cover** = 1 − e^(−0.7·LAI_total) blended with litter and moss cover. This is the same idea as the cover factor in soil-loss equations (forest C ≈ 0.001, grass ≈ 0.01–0.05, bare = 1), but deliberately kept as a modest multiplier (~1–2×), not a 1000× one. Over Myr, erosion is set by uplift and channel incision, and plant cover mostly changes how fast hillslope soil is stripped. Weathering: replace `(1 + 0.5·veg)` by a term in NPP (roots and soil CO₂ scale with productivity; the "biological weathering factor" of Berner's GEOCARB). Both are drop-in replacements for existing terms, so the risk is low.

### 4.6 Order

1. **Erosion and weathering in the run** (replaces `sim.veg`; tiny code change, but it changes the run, so golden hashes and the scorecard need updating).
2. **Budyko w and evap_cool** (world first, then the run once checked).
3. **Soil carbon and peat**, together with PW-185.
4. **Albedo** nudge.
5. Rain recycling (maybe never).

---

## 5. Coastal and aquatic: what belongs here vs PW-188

| Habitat | Owner | Why |
|---|---|---|
| **Mangroves** | PFT here (fractions, NPP, carbon, named type 55); **placement suitability from PW-188** (warm sea, Tmin > 0, tides, muddy sheltered coast, river sediment) | They are trees on land, with roots and canopy; they belong in the land fractions, the satellite view and soil carbon (mangrove peat). Where they can grow is a coastal question. |
| **Salt marsh** | same split as mangroves | Herbaceous land cover on tidal flats; where mangroves can't grow (too cold), salt marsh takes over. |
| **Coastal dune grass, sea-cliff vegetation** | here (zoom patterns) | Land plants; need wave power and sand from the coast layers. |
| **Seagrass meadows** | PW-188 | Marine, in sea cells: light at the bed (depth, turbidity), shelter, warmth. |
| **Kelp forests** | PW-188 | Marine: cool, nutrient-rich, rocky, upwelling. |
| **Coral reefs** | PW-188 (the run already makes reef limestone; atolls in the zoom) | Animals, not plants; built by the carbonate system. |
| **Freshwater wetlands, lake-edge reeds** | here | §3.6. |
| **Aquatic plants in lakes, phytoplankton** | out of scope | No visible map effect at our scales. |

Interface: PW-188 provides a per-coast-cell "intertidal habitat" score (tide range, shelter from wave power, mud from river sediment, salinity). Vegetation runs Mang and Salt only where that score allows. PW-188's marine layers (`seagrass`, `kelp`, `reef`) live in sea cells and never compete with land PFTs.

---

## 6. Compute cost

Estimates for numba (parallel over cells, 4–8 cores); land cells only. Counting: 21 PFTs × 12 months × ~7 LAI search evaluations × ~60 floating-point operations, plus a 2–3-year bucket spin-up, plus 30–100 competition iterations.

| Where | Work | L6 | L7 | Notes |
|---|---|---|---|---|
| Run, per climate update (every 4 Myr) | equilibrium, warm-started, LAI from the last update, ~20 iterations | ~0.1–0.2 s | ~0.4–0.6 s | ×250 updates per Gyr: **~40 s per Gyr at L6, ~2 min per Gyr at L7** (5–10% of run time) |
| World | full equilibrium, fire, stand ages, named types | ~0.5–1 s | ~1.5–3 s | worlds take 1.5–5 s (L6) and 13–28 s (L7) today |
| Regional zoom | per-pixel equilibrium on up to 250k px | – | – | ~2–4 s, or ~1 s with NPP computed on a 4× coarser lattice and only the water and wetness parts per pixel; zooms take 1–7 s today |
| Time zoom, per Myr | potential NPP at each 10 kyr refresh (100×) + cover and migration every 500 yr (2000×, ~0.03 s each) | ~1.5 min | ~6 min | +40% on the time zoom (~4 min per Myr at L6); halve it with a 1 kyr vegetation step |
| Earth check | one world-equivalent on the Earth grid, plus a second pass on observed climate | ~2 × world | | |

Memory stays well under the run's ~1 GB at L7.

---

## 7. Earth checks

Run the model on Earth's terrain (world dc3732) **twice**: once on the model's own climate, once on the observed climate the Earth world carries (`obs_temperature`, `obs_precipitation`, `obs_warm_month`, `obs_cold_month`; observed half-year rain needs adding, see draft `earth-vegetation-data`). The gap between the two runs tells **vegetation errors** apart from **climate errors**. A new `tools/veg_check.py` (or a section in `earth_check.py`) reports:

| Check | Observation | "Good enough" |
|---|---|---|
| Global land NPP | ~56 Pg C/yr (Field et al. 1998; MODIS MOD17 ~53) | 45–70 Pg C/yr (DGVMs span ~40–80) |
| NPP by latitude band | MOD17 zonal means | within ±30% in each 10° band with real vegetation |
| Land cover, 8 groups (forest, woodland/savanna, shrubland, grassland, tundra, desert/barren, wetland, ice) | **potential natural vegetation** (Ramankutty & Foley 1999), not today's land cover: humans cleared ~a third of forests | area-weighted agreement ≥ 60% on observed climate, ≥ 50% on model climate (cf. Köppen main groups 70.7%) |
| Tree cover | MODIS VCF / Hansen tree cover, in little-disturbed regions | correlation r ≥ 0.7; boreal and tropical forest belts present and closed |
| Biome areas | potential forest ~55–60 Mkm²; boreal ~12–17; tropical savanna and grassland ~20; desert and xeric shrubland ~25–30; tundra ~8–11 | each within ±35% |
| Northern treeline | observed latitude by longitude sector | within ~3–5° of latitude |
| Savanna–forest boundary | Africa, South America | in the right rainfall band (~1000–1800 mm); mosaic allowed |
| Burned area | GFED4s ~4–5 Mkm²/yr, ~70% in savannas | 2–8 Mkm²/yr; most in the tropical wet–dry belt; little in rainforest and desert |
| Vegetation carbon | ~450–650 Pg C | 300–800 Pg C |
| Mediterranean scrub | the five Mediterranean regions | present in at least four |
| C4 share of grassland | C4 dominates below ~30–35° latitude (Still et al. 2003) | crossover band within ~10° of latitude |

**Not a target:** IGBP class-by-class agreement (it includes crops and cities), exact peat extent (needs PW-185 and finer hydrology), and regional anomalies that come from known climate errors (East Antarctica and NE Canada too warm, PW-038/039; patchy rain, PW-013). Earth is an analogue: the goal is that the *mechanisms* place forest, savanna, desert and tundra where Earth's climate puts them, not a pixel match.

**On generated planets:** envelope tests in pytest (vegetated share of land, forest share, global NPP per land area in a plausible range, no vegetation on ice, deserts sparse), plus golden hashes once stable.

---

## 8. Viewer and game outputs

### 8.1 Map layers

- **Vegetation** (globe and zoom): the 60 named types with a legend grouped as §2.3. It becomes the default "nature" layer next to Biome.
- **Tree cover, plant cover, canopy height, LAI** (July/January picker, as other seasonal layers), **NPP, biomass, fire return interval, stand age.**
- **PFT picker:** a dropdown to show any one PFT's fraction ("where are the larches?").
- **Satellite view** (PW-083): colour = Σ fraction × PFT colour × LAI greenness in that season + soil/rock colour for bare ground + snow. With `lai_jul/jan` it changes with the seasons.
- **Hover card:** "Boreal spruce-fir taiga · 72% boreal needleleaf evergreen, 15% birch-aspen, 8% moss · canopy 18 m · NPP 310 g C/m²/yr · fires every ~120 yr · leafless Oct–May (broadleaves)".

### 8.2 What a TTRPG or game user gets

Computed from the layers (not fixed per named type), so a gallery forest in a savanna or a burned patch of taiga gets its own values. Each attribute is on a 0–5 scale or a multiplier, with a short phrase:

| Attribute | From | Example |
|---|---|---|
| **Travel cost** (× road-less walking) | stem density (tree cover × height class), understory LAI, wetness, slope (zoom), deadfall from stand age | grassland ×1, open woodland ×1.3, temperate forest ×2, rainforest ×3, mangrove / raised bog ×4 |
| **Visibility** | canopy closure and understory | "sightlines 30 m" (rainforest) to "to the horizon" (steppe) |
| **Forage / game** | herb NPP + fruit and nut PFTs (TeBS, TrBR) | savanna and prairie high; taiga and rainforest floor low |
| **Timber** | woody biomass, height, straightness (needleleaf) | temperate rainforest: "the finest timber on the planet" |
| **Fuel and firewood** | dead wood, peat | peatlands: "peat for fuel" |
| **Water** | runoff, wetness, rivers | desert scrub: "water every few days' travel" |
| **Fire season** | dry months, fire return | "fire risk Jul–Sep; big fires every ~30 yr" |
| **Hazards** | type and climate | thorns, bogs, insects (wet tropics), deep snow (taiga), crocodiles (mangrove) |
| **Seasonal look** | phenology | "leafless Nov–Apr", "green only in the rains (Jun–Sep)" |

Example line: *"Dense temperate rainforest. Travel slow (×2.5, deadfall, wet), sightlines 30–50 m, excellent timber (60 m conifers), poor forage, rain most days Oct–Apr; fire almost never."*

### 8.3 Hooks for later epics

- **Resources (PW-155):**
  - timber volume and quality (biomass, height, PFT);
  - fuel (wood, peat);
  - fibre and thatch (reeds, papyrus, grasses);
  - resins and naval stores (TeNE);
  - pasture (herb NPP);
  - fertile land (NPP × PW-185 soil);
  - and, from the run, coal from buried peat.
- **Species placement (PW-103):** habitat suitability for each species as a function of the PFT fractions, the named type, NPP and stand age (e.g. "an elf-like species needs ≥ 60% broadleaf forest older than 200 years"). The time zoom's vegetation history gives **refugia** and **corridors** (land bridges with grassland at low sea level). The "where did each species survive the ice age, and where do ranges meet" questions in PW-103 come straight from these layers.
- **Settlement and travel (later):** travel cost feeds route-finding; forage and soil feed carrying capacity.

---

## 9. Staging and decisions

### 9.1 Steps for PW-187

| Step | What | Effort | Depends on |
|---|---|---|---|
| 1 | `planet/vegetation.py`: the PFT table, a shared 12-month climate builder (with `climate.py`), snow, two-layer bucket, envelopes, LUE NPP with LAI search. World layer `npp` and "potential dominant PFT". Unit tests (NPP sane per climate, envelopes respected). | m | climate-monthly draft (can be done inside the step) |
| 2 | Cover dynamics (TRIFFID-style) to equilibrium; GlobFIRM-lite fire; stand ages; wetlands from hydrology; named-type classifier; world layers; `vegetation` legend in `store.legends`; viewer layers, hover card and PFT picker. | l | 1 |
| 3 | Earth check: datasets in `tools/earth_data.py`, `tools/veg_check.py`, two-climate comparison, tuning to §7 targets. | m | 2, earth-vegetation-data draft |
| 4 | Run: replace `sim.veg` with the cheap equilibrium (warm-started), erosion cover and weathering by NPP, keyframe layers; update golden hashes; scorecard. | s–m | 2 (3 preferable) |
| 5 | Zoom downscaling: radiation index, TWI, river and coast water, regional fractions, fire mosaic noise; zoom layers and viewer. | m | 2, zoom-terrain-indices draft, PW-139 helpful, PW-185 for soils |
| 6 | Climate feedbacks: Budyko w and evap_cool from vegetation (world, then run); albedo nudge; re-run earth_check and the scorecard. | m | 3, 4 |
| 7 | Time zoom: dynamic cover with migration, refugia record, frames; PW-091 finished worlds start from it. | m | 2, PW-091 |
| 8 | Soil carbon and peat hand-off with PW-185; coal from peat in the run. | s | 2, PW-185 |
| 9 | Game attributes (§8.2), satellite colouring (PW-083), and export fields for PW-100. | s–m | 2 |

Steps 1–3 give a reviewable world-level vegetation map with Earth numbers (~2–3 agent-days). Steps 4–6 make it part of the planet's physics. Steps 7–9 can run in parallel with other work.

### 9.2 Decisions for the owner

1. **Shape of the type system.**
   - (A) 21 PFTs computed, plus 56 named types derived (60 with non-vegetated).
   - (B) ~12 PFTs (standard DGVM size) plus ~40 named types: faster to build, but heath, succulent, peat and wetland types would be faked by rules.
   - (C) ~40 PFTs: more distinct types, many with no data to tune.

   **Recommend A.**
2. **What happens to the current `biome` layer.**
   - (A) The named vegetation types become the map's main land-cover layer, and `biome` is kept as a coarse grouping derived from them, so highlights and old views keep working.
   - (B) Keep the Whittaker lookup alongside.
   - (C) Drop `biome`.

   **Recommend A.** Köppen is unaffected.
3. **Flora through deep time.**
   - (A) A modern, Earth-like set of PFTs at every moment of every run. Only the existing `plants_from` switch decides whether land plants exist, plus an optional per-run list of disabled PFTs (e.g. "no grasses", for an alien or a pre-grass world).
   - (B) Gate PFTs by Earth's history (forests from ~385 Ma, grasses ~70 Ma, C4 ~10 Ma) scaled to run time.
   - (C) A fantasy flora table per seed.

   **Recommend A.** No evolution is simulated (PW-184), and B would tie generated planets to Earth's calendar.
4. **Equilibrium or dynamic in worlds.**
   - (A) Equilibrium with stand-age mosaics; the dynamic model only in the time zoom, and in PW-091 finished worlds through it.
   - (B) Run a few thousand years of dynamics for every world.

   **Recommend A.** B costs more and adds little that the stand ages don't give.
5. **Vegetation inside the main run.**
   - (A) Yes, the cheap equilibrium at every climate update, feeding erosion and weathering only, with climate feedbacks added later once checked on Earth.
   - (B) Worlds only, keeping the crude `sim.veg`.
   - (C) Full feedbacks in the run from the start.

   **Recommend A** (~5–10% run time).
6. **Climate feedbacks and their strength.**
   - (A) Budyko w and evap_cool first, then the albedo nudge capped at ±2 °C; no rain-recycling feedback for now.
   - (B) All three including rain recycling.
   - (C) None: vegetation is diagnostic only.

   **Recommend A.** "Nudge, don't force."
7. **Mangroves and salt marsh.**
   - (A) PFTs in the vegetation fractions, placed where PW-188's intertidal habitat score allows; seagrass, kelp and reefs are PW-188's marine layers.
   - (B) All coastal life in PW-188, as separate layers.

   **Recommend A.**
8. **Disturbances.**
   - (A) Lightning fire with fuel and dryness (GlobFIRM-lite); grazing and browsing only implicit in background mortality; no humans.
   - (B) Add an explicit grazing pressure (herbivores keep grasslands open).
   - (C) No fire.

   **Recommend A.** Fire is what makes savannas and Mediterranean scrub. Grazing can come with fauna (PW-103).
9. **Storage.**
   - (A) Worlds store all 21 PFT fractions plus the summary layers (+7–12 MB at L7). Runs store type, tree cover and NPP per keyframe (+123 MB per Gyr at L7). Zooms store the 7 summary layers only (+2 MB).
   - (B) Also all PFT fractions in zooms (+5 MB per zoom).
   - (C) Fractions only in memory, never stored.

   **Recommend A.**
10. **Forest–savanna bistability.**
    - (A) Let history decide (warm start from the previous keyframe), with a neighbour term, and zoom-scale noise for mosaics.
    - (B) Force a single deterministic boundary by rainfall.

    **Recommend A.** It gives realistic mosaics, and the history is part of what makes a world feel lived-in.
11. **Game attributes.**
    - (A) Computed continuously from layers (travel cost, visibility, forage, timber…).
    - (B) A fixed table per named type.

    **Recommend A**, with B's table as the fallback text.
12. **CO₂ effect on plants.**
    - (A) A mild nudge from the run's CO₂ index on C3 efficiency and on the C3/C4 crossover temperature.
    - (B) None.

    **Recommend A.** It makes icehouse eras more C4-grassy and greenhouse eras more forested, as on Earth.

---

## References (brief)

- **LPJ:** Sitch et al. 2003, *Global Change Biology* 9:161. PFTs and bioclimatic limits; GlobFIRM fire: Thonicke et al. 2001.
- **BIOME4:** Kaplan et al. 2003. LAI optimisation, biome assignment from PFTs, absolute-minimum temperature fit.
- **TRIFFID / JULES:** Cox 2001 (Hadley Centre tech. note 24); Clark et al. 2011. Lotka–Volterra cover competition.
- **CLM:** Lawrence et al. 2019 (CLM5). PFT set for comparison.
- **ED** (Ecosystem Demography): Moorcroft et al. 2001. Stand-age (cohort) structure; our exponential stand ages are its simplest version.
- **LUE / CASA:** Potter et al. 1993; MODIS MOD17: Running et al. 2004.
- **Whittaker** 1975 (biome diagram); **Holdridge** 1947 (life zones from biotemperature, rain and PET ratio: the closest classic analogue to our envelope + water approach); **Köppen**, Peel et al. 2007.
- **Savannas:** Sankaran et al. 2005 (*Nature* 438:846); Staver et al. 2011 (*Science* 334:230).
- **C4:** Collatz et al. 1998; Ehleringer et al. 1997; Still et al. 2003.
- **Budyko and vegetation:** Zhang et al. 2001 (*WRR* 37:701); Donohue et al. 2007. **Albedo:** Bonan 1992; Bonan 2008 (*Science* 320:1444).
- **Earth data:** Field et al. 1998 (NPP); Ramankutty & Foley 1999 (potential vegetation); Hansen et al. 2013 / MODIS VCF (tree cover); GFED4s (van der Werf et al. 2017).
