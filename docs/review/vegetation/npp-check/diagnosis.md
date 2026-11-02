# Plant productivity against sourced NPP–climate data (PW-1261, D34 B broadened; lane 123)

**In plain words.** The ticket said the plants grow too little above ground for Africa's herds. On Earth's *observed*
climate they don't: the model's grassland and savanna grow 1.4–1.8 times *more* above ground than field measurements at
the same rain, and the Earth herds already come out at Coe et al.'s measured numbers. The worlds' herds are thin for
other reasons: their climate is cloudier and has cooler winters than Africa's at the same rain, and one of the two worlds
(067778) has a low CO2 (221 ppm) that cuts water-limited growth by about a third. So "raise the plants" is the wrong fix.
Two real plant errors do show up across biomes:
1. **Grass and other herbs keep ~70% of what they photosynthesise** (NPP/GPP ~0.7); measured plants keep ~46%. Their
   roots pay no upkeep in the model. This makes every grassland, steppe, savanna and tundra too productive.
2. **Wet tropical forest grows about half of what is measured** (~630 against ~1160 g C/m2/yr). Its photosynthesis is
   low, not its respiration.
The cross-biome total looks right (59.6 Pg C/yr against ~56) only because these two errors cancel (with a global
efficiency cut, EPS_SCALE = 0.8, tuned on that total).

Candidate 1 (herbs' roots respire) fixes the first and is screened below; it lowers the herds on Earth from Coe's level
to ~0.65x of it, which exposes a second, separate gap: McNaughton et al. 1989's cross-ecosystem herd fit sits ~1.5x
below Africa's measured parks at field-measured grass production. That is a herd question, not a plant one (draft).

## Method

`vegetation.model` run on Earth's L6 terrain (world 506694) with the **observed** climate (NCEP temperature, GPCC
half-year rain, CRU sunshine; `tools/veg_check.py::run`, soils on), so rain errors (lanes 120/121) don't count against
the plants. Scripts (scratch, copied here): `npp_check.py` (NPP by biome / climate box against the yardsticks below;
`--herb-rl`, `--eps`, `--trop-eps` patch `vegetation._KP` for screens), `pft_probe.py` (per-PFT GPP, NPP, LAI),
`world_check.py` and `inputs_cmp.py` (the worlds' herd inputs and climate). Earth data from a private copy of
data/earth in the worktree (data/earth untouched).

Yardsticks, each read for this check (none from memory):
- **Miami model** (Lieth): NPP = min(3000 (1 − e^(−0.000664 P)), 3000 / (1 + e^(1.315 − 0.119 T))) g dry/m2/yr; read in the
  R package soilassessment 1.3.1, `R/NPPmodel.R` (CRAN source), and confirmed by an Embrapa paper's statement of the same
  two curves (search snippet). Converted at 0.45 g C/g dry (`lineages/prey.py::C_FRAC`). A cross-check only: a 1970s
  two-curve fit, and Del Grosso et al. 2008 (Ecology 89:2117; abstract read on OSTI 1017332) say it overestimates
  non-tree systems because tree systems have more NPP at a given rain (their own equations are paywalled, not read).
- **MOD17A3** NPP (2000–2015, `tools/earth_data.py::earth_mod17_npp`): a satellite model of today's land use, not a
  measurement.
- **Deshmukh 1984** (Afr J Ecol 22:181; abstract via the-eis.com record): East and southern African herb-layer *peak
  biomass* (kg/ha) = 8.488 P − 195.768. Peak standing crop is a lower bound on above-ground NPP.
- **Yang et al. 2020** (Land Degrad Dev, doi:10.1002/ldr.3715; PDF par.nsf.gov 10222325, p. 844–845): 32 ungrazed
  grassland sites, ≥ 6 years each: mean ANPP = 0.7 MAP − 41.7 g/m2/yr (r2 0.72).
- **Rosenzweig 1968 as Coe et al. 1976 use it** (Coe p. 345, on file): log10 NAAP = 1.66 log10 AE − 1.66, AE taken = rain
  up to 700 mm. Coe's own caution: "Validation of Rosenzweig's formula for the African savannas has not been attempted".
- **Malhi, Doughty & Galbraith 2011** (Phil Trans R Soc B 366:3225, PMC3179639, Table 3): total NPP of 35 tropical forest
  plots; the 17 lowland plots (MAT ≥ 23 C, MAP ≥ 1480 mm) have a median ~11.6 Mg C/ha/yr (8.8–16.5).
- **Collalti & Prentice 2019** (Tree Physiol, doi:10.1093/treephys/tpz034; abstract, Imperial Spiral): NPP/GPP over 200+
  studies 0.46 ± 0.12 (range 0.22–0.79), forests.
- **Gherardi & Sala 2020** (PNAS, PMC7443884; re-read): the below-ground share used by the herds; Table 1 shrublands and
  savannas 61 ± 4.8%, grasslands 64 ± 5%; BNPP there = satellite NPP − field ANPP.

ORNL DAAC's EMDI / NPP Multi-Biome site tables (Scurlock & Olson) would be the best site set, but the downloads now need an
Earthdata login (HTTP 400 without one); not used. Owner fetch if wanted (draft).

## Results: per biome, model on observed climate

Total NPP, g C/m2/yr, by potential natural vegetation (Ramankutty & Foley) group, area-weighted:

| group (potveg) | MAP mm | MAT C | model | Miami | MOD17 | field | verdict |
|---|---|---|---|---|---|---|---|
| tropical wet forest (P > 1500, T > 18; climate box) | ~2500 | ~25 | 628–647 | 961–1099 | 920–1011 | ~1160 (Malhi 2011, lowland median) | **~0.55x low** |
| forest/woodland (all) | 1203 | 10.3 | 513 | 576 | 634 | | slightly low (the tropics) |
| temperate forest (P 800–1500, T 10–18) | | | 659–788 | 590–734 | 684–741 | | in range |
| savanna | 928 | 20.0 | 692 | 583 | 501 | | high |
| grassland | 504 | 9.9 | 489 | 338 | 292 | | **~1.5x high** |
| shrubland | 375 | 17.9 | 406 | 280 | 211 | | **~1.5x high** |
| tundra | 368 | −9.2 | 185 | 120 | 123 | | **~1.5x high** |
| desert | 81 | 21.0 | 93 | 68 | 82 | | in range |
| warm semi-arid (T 18–32, P 250–1000; climate box) | | | 474–799 | 286–593 | 144–476 | | **1.35–1.65x Miami** |

Above-ground NPP of the grass layer, g dry/m2/yr (herb NPP x Gherardi & Sala's above-ground share / 0.45):

| rain band | MAP | model, warm Africa grassy | Deshmukh peak biomass | Yang ANPP | Rosenzweig (Coe) | model, grassland world-wide (all NPP above ground) | Yang |
|---|---|---|---|---|---|---|---|
| 250–400 | 328 / 326 | 334 | 259 | 188 | 328 | 319 | 186 |
| 400–550/600 | 468 / 476 | 544 | 377 | 286 | 592 | 495 | 291 |
| 550–700 | 626 | 711 | 512 | 397 | 961 | | |
| 600–900 | 731 | | | | | 653 | 470 |
| 700–900 | 804 | 832 | 662 | 521 | 1156 | | |

So the model's grass ANPP is 1.3–1.4x Deshmukh's peak biomass and 1.4–1.8x Yang's ANPP; it is Rosenzweig's NAAP that sits
2–2.5x above both field fits (it was fitted to above-ground production across all ecosystems, forests' wood included, and
Coe took AE = rain). The ticket's "~2.4x too little above ground" compared the model with Rosenzweig, not with grass data.

Herds on Earth (model's `prey.wild`, observed climate, warm African grassy cells, median t/km2): 0.5 / 1.3 / 2.6 / 4.1 /
5.5 / 6.3 for the bands 150–250 … 900–1200 mm, against Coe's measured 2.0 (375 mm), 1.7–2.9 (406–425), 4.0–4.4 (553–650),
4.8–8.4 (784–878). On observed climate the herds already match.

**Why the worlds' herds are thinner** (`world_check.py`, warm land at 550–700 mm; `inputs_cmp.py`):

| | NPP g C | shade | PAR | coldest month C | pCO2 ppm | herds t/km2 |
|---|---|---|---|---|---|---|
| Earth Africa, observed | 748 | 0.29 | 3620 | 19.9 | 350 | 4.1 |
| world 067778 | 392 | 0.41 | 3090 | 15.3 | 221 | 1.5 |
| world 6909cb | 512 | 0.44 | 2895 | 12.5 | 349 | 2.1 |
| world dba204 | 538 | 0.40 | 3165 | 17.2 | 399 | 2.3 |

The worlds' semi-arid tropics are cloudier (15–20% less light), have cooler winters (C4 grass grows from 10 C to full at
25 C, `vegetation.py::_ft`), and on 067778 the low CO2 scales the water-use efficiency by 221/350 (`vegetation.py::potential`,
PW-644; sourced). These are climate inputs (the model's cloud and winter temperatures; base-climate lanes), not the plant
response.

## Which step departs

1. **Herb carbon-use efficiency** (`vegetation.py::_year`, the respiration `(rl * leaf + rw) * q10`). Herbs have rw = 0 and
   rl = 4 (per LAI, the leaves); nothing respires for their roots and rhizomes. Probe (`pft_probe.py`): C4 grass in
   African savanna GPP 1186, NPP 801, NPP/GPP 0.68; C3 grass in temperate steppe 0.72; tundra herbs 0.73; trees 0.33–0.60.
   Measured whole-plant NPP/GPP is 0.46 ± 0.12 (Collalti & Prentice 2019; forests — no grass compilation read). The
   GPP itself is plausible: ~1.9 g C per mm of rain in the semi-arid savanna. The water-use and leaf-area steps are not
   where it departs; the light-use step is not limiting there (water-limited, `g_m = wue * dryf * aet`).
2. **Tropical forest GPP** (`_year`, `g_m = eps * eff * fap * PAR * ...`). TrBE/TrBR on wet tropical cells: GPP 2012 / 1772,
   NPP/GPP 0.33 / 0.36 (in line with measured tropical CUE), optimum LAI 3.4 / 3.1. The shortfall is GPP: the
   efficiencies (1.10 x EPS_SCALE 0.8 = 0.88 g C/MJ) and the cloud-dimmed light. EPS_SCALE was tuned down to hit the global
   total, which the herbs' surplus inflated: the two errors compensate.
3. Temperature response: cold land (T < 0) is 1.2–1.8x Miami but within MOD17 (except the driest), so no clear error from the
   temperature hump; the excess in tundra is the herbs' (1).
4. Allocation (above vs below ground): not modelled in the plants; the herds take Gherardi & Sala's share, sourced, with
   their savanna/shrubland value (61%) consistent with the rain fit at 625 mm (56%). Not the departing step.

## Candidates and screens (Earth observed climate, L6)

| variant | land NPP Pg | agreement % | savanna Mkm2 | burned Mkm2/yr | Africa grass ANPP at 626 mm (g dry) | herds 550–700 mm t/km2 | wet tropics NPP |
|---|---|---|---|---|---|---|---|
| base | 59.6 | 61.7 | 21.6 | 5.67 | 711 | 4.1 | 628–647 |
| **C1: herbs' roots respire, rl x3** | 53.2 | 62.8 | 17.7 | 3.73 | 545 | 2.8 | 605–621 |
| herbs rl x2 | 56.1 | 62.4 | 19.6 | 4.74 | 625 | 3.4 | 623 |
| C2: tropical trees eps x1.3 | 65.6 | 62.5 | 16.9 | 5.27 | 710 | 4.0 | 925–1013 |
| C1 + C2 | 60.5 | 62.8 | 13.8 | 3.38 | 536 | 2.7 | 921–1009 |
| C1 + tropical x1.5 | 66.4 | 62.3 | 11.6 | 3.20 | 536 | 2.7 | 1151–1281 |
| all efficiencies x1.25 (EPS_SCALE 1.0) | 74.2 | 62.8 | 19.9 | 5.99 | 716 | 4.2 | 981 (but cold and temperate land overshoot) |

C1 at x3 gives herb NPP/GPP 0.54 (savanna C4) / 0.55–0.62 (steppe), within one SD of 0.46; grass ANPP 545 g at 626 mm
(Deshmukh 512, Yang 397); grassland/shrubland NPP down 12–18% (still above Miami); potveg agreement +1.1; savanna area
17.7 (target band 13–27); burned area 3.7 (target 2–8, GFED ~4.7: less fuel). Global NPP 53.2 (target 45–70, obs ~56).
C2 fixes the wet tropics but tips the savanna–forest balance (savanna 13.8 Mkm2 with C1, at the band's floor; African
900–1200 mm savanna becomes forest) and is a calibration knob without a measured light-use efficiency read: not
recommended now, ticketed.

Coded and parked: C1 as `vegetation.py::HERB_ROOT_RESP` = 2.5 on the herb PFTs' rl (`candidate1-herb-root-resp.patch`,
not on the branch). x2.5 screens: land NPP 54.6 Pg, agreement 62.7%, savanna 18.7 Mkm2, burned 4.25 Mkm2/yr, Africa
grass ANPP 586 g dry at 626 mm, herds 1.9 / 3.1 / 4.1 t/km2 at 400-550 / 550-700 / 700-900 mm. Why 2.5 and not 3: at x3
one ideal desert cell of `tests/test_vegetation.py::test_npp_and_types_on_ideal_climates` reaches 30.5% cover against
the test's < 30% (29.5% before; 26.5% at x2, 29.7% at x2.5: a one-cell flicker, from crust replacing grass); 2-3 are equally
defensible, so the middle was taken. The patch is **not merge-ready**: see `screens.md` (the Mediterranean scrub test
stops burning: the fire's fine-fuel threshold was set with the inflated grass growth).

## Recommendation

1. Take C1 (herbs' roots respire), but as one change with two re-anchors it exposes: the run's weathering factor reads
   NPP (two L6 seeds warm 3.4-4.8 C with C1; draft `draft-weathering-npp-reference-after-grass-cue.md`) and the fire's
   fine-fuel floor (Mediterranean scrub stops burning; draft `draft-fire-fuel-threshold-after-grass-cue.md`). It is a
   mechanism the model lacked and moves every grass biome toward the field data; global NPP stays in range.
2. Do **not** raise the herds through the plants. With C1 the Earth herds fall to ~0.65x Coe's parks: the remaining gap
   is McNaughton's cross-ecosystem fit (r2 0.58), which McNaughton et al. themselves found runs below grasslands for
   consumption (p. 143: "forests fell below the line and grasslands above"). That needs its own decision (draft
   `draft-herd-fit-grassland-offset.md`): A accept, B a grassland/savanna offset fitted on Coe's measured herds against
   Deshmukh's measured grass production, C Coe's own rain fit for warm savanna.
3. Tropical forest GPP (C2) as its own ticket (draft `draft-tropical-forest-gpp-low.md`), after a read of a measured light-use
   efficiency and a check of the light under the observed cloud; with EPS_SCALE revisited once the herbs no longer
   inflate the total.
4. The worlds' thin herds at a given rain trace to the climate (cloud, cool winters, low CO2): for the base-climate lanes
   (draft `draft-semiarid-tropics-cloudy-cool.md`).
