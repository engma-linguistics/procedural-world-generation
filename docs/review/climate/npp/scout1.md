# Scout 173: why wet tropical forest grows too little, and one lever (PW-1331, PW-1261, PW-1332)

**In plain words.** On Earth's observed climate the model's rainforest makes about 620 g C/m2/yr; field plots measure about
1160. I looked for the step that holds it down. It is not the light and not the carbon-use efficiency (both look right). It is
the leaf area: the model's forests settle at a leaf area index (LAI) of about 3.0-3.5, where real rainforest is about 5. The
reason is that every leaf, however deep in the shade, is charged the full upkeep (respiration) of a sunlit one, so adding
leaves stops paying early. In a real canopy the shaded leaves carry less photosynthetic enzyme and breathe less. Making leaf
upkeep fall with canopy depth (a sourced profile, one constant) lifts rainforest from 620 to about 820 (0.55x to 0.71x of the
field median) with global land NPP unchanged (59.9 against 59.6 Pg C/yr, observed about 56). It does not close the whole gap,
and it nudges wet temperate forest up about 12%. Grass is a separate error (the herbs' roots, candidate C1 of lane 123);
this lever does not fix grass and I do not claim it does.

## Measured (all runs: model on Earth's L6 terrain, world 506694, observed climate, soils on; script `docs/review/vegetation/npp-check/npp_check.py`, my copy adds `--kn`)

Baseline for every "before": current main (dd75bdc4), land NPP 59.6 Pg C/yr. Yardsticks as read by lane 123 in
`docs/review/vegetation/npp-check/diagnosis.md` (MOD17A3 from `tools/earth_data.py::earth_mod17_npp`; Miami model, CRAN
soilassessment source; Malhi, Doughty & Galbraith 2011 Table 3, PMC3179639). I re-read Malhi 2011 this session: it states
tropical forest GPP "approximately 30 Mg C/ha/yr" (= 3000 g C/m2/yr), NPP/GPP "approximately 30 per cent", typical LAI 5.0, and
median NPP 11.6 Mg C/ha/yr of 10 Amazonian sites (the 1160 figure in the ticket is the 17-lowland-plot median of lane 123).
Malhi gives no canopy light-use efficiency, so none is quoted here.

NPP, g C/m2/yr, area-weighted by climate box:

| box | main | MOD17 | Miami | field |
|---|---|---|---|---|
| T 18-32 C, P 2500+ mm (wet tropics) | 628 | 1011 | 1099 | ~1160 |
| T 18-32 C, P 1500-2500 | 647 | 920 | 961 | |
| T 10-18 C, P 1000-1500 (wet temperate) | 788 | 741 | 734 | |
| T 18-32 C, P 750-1000 (savanna) | 799 | 476 | 593 | |
| grassland group (potveg) | 489 | 292 | 338 | grass ANPP 1.4-1.8x Yang (lane 123) |
| tundra group | 185 | 123 | 120 | |
| desert group | 93 | 82 | 68 | |
| shrubland group | 406 | 211 | 280 | |
| boreal-ish T 0-10 C, P 500-750 | 451 | 469 | 392 | |

Boreal and desert are already in range; grass, shrub and tundra are 1.4-1.9x high (the herb error); wet tropics 0.6x low.

## Where the wet tropics are limited (`vegetation.py::_year`, current main)

Wet tropical cells (T > 22 C, P > 2000 mm, 679 cells) against wet temperate cells (T 10-18 C, P 1000-2500, 424 cells):

| | wet tropical | wet temperate |
|---|---|---|
| annual PAR into the model, MJ/m2 | 2992 | 2746 |
| TrBE GPP / NPP, g C | 2053 / 687 | (TeBS) 1742 / 879 |
| optimum LAI | 3.5 | 3.6 |
| leaf-on months | 12 | 10.8 |
| water stress alpha | 0.97 | 0.98 |

- Not water: alpha 0.97, twelve leaf-on months.
- Not the temperature hump: the tropics sit inside the full-growth plateau (20-32 C).
- Not carbon-use efficiency: NPP/GPP 0.33 against Malhi's "approximately 30%".
- It is GPP: 2053 against ~3000, and the tropics get only 9% more light than the temperate cells. With absorbed light
  fap = 1 - exp(-0.5 LAI) = 0.82 at LAI 3.4 and a light-use efficiency of 0.88 g C/MJ (1.10 x EPS_SCALE 0.8), GPP follows.
- The LAI is chosen to maximise net NPP: `_potential` golden-section search over LAI, objective `out[1]` = NPP minus leaf
  turnover. Leaf respiration is `rl * LAI * Q10` with rl = 7.4 g C/m2/month per LAI at 20 C for tropical trees (~90 g C per LAI
  per year). Marginal GPP per LAI at LAI 3.4 is ~220 g C against ~120 g C of upkeep and turnover, so the search stops at 3.4
  even though laimax is 7. That is the limiter.

## The lever: leaf respiration falls with canopy depth

Leaf respiration per unit LAI becomes the canopy integral (1 - exp(-KN L)) / KN instead of L (Vcmax, and with it leaf
respiration, declines exponentially down a canopy: Lloyd et al. 2010; Bonan et al. 2011. I cite these from memory of the
literature, not from a read this session; the exponential-profile form is standard, the value of KN is not read). One constant,
`KN_RESP`, applied to trees, shrubs and ground cover; herbs keep the linear form. A mechanism, no per-biome term. Patch on this
branch (`planet/vegetation.py`: `KN_RESP`, column 20 of `_KP`, 4 lines in `_year`).

Offline estimate: the same NPP function on the same observed climate (no simulation; each run is 10 s). Baseline: main.

| variant | wet tropics NPP (2500+ mm) | LAI there | wet temperate 1000-1500 | land NPP Pg | savanna Mkm2 | burned Mkm2/yr |
|---|---|---|---|---|---|---|
| main | 628 | 3.0 | 788 | 59.6 | 21.6 | 5.67 |
| KN 0.2, all | 744 | 3.75 | 849 | 63.1 | 21.6 | 5.83 |
| KN 0.4, all | 833 | 4.34 | 891 | 65.7 | 21.4 | 5.94 |
| lane 123's C1 (herb rl x2.5) alone | 623 | 3.0 | 782 | 54.6 | 18.7 | 4.25 |
| **C1 + KN 0.4 on non-herbs** | **827** | 4.3 | 886 | **59.9** | 18.0 | 4.25 |
| C1 + KN 0.4 + all efficiencies x1.25 | 1208 | 4.75 | 1187 | 77.7 | 17.4 | 5.24 |

Reading it. KN alone lifts wet tropics 628 -> 833 (field ~1160: 0.54x -> 0.72x; MOD17 1011: 0.62x -> 0.82x) and wet
temperate 788 -> 891 (MOD17 741, Miami 734: from +6% to +20% high). Combined with C1 the land total stays at 59.9 Pg, the same
as main, so the "two errors cancel" total survives while each error shrinks. Raising all efficiencies fixes the tropics but the
temperate and boreal land overshoots (1187 against 741), as lane 123 found; the forest gap is tropical-specific, so a global
efficiency cannot close it.

## What it does not do (honest limits)

- Still ~0.7x of the field median in the wet tropics, and wet temperate forest rises above MOD17 by ~20%. The leftover tropical
  gap has no second mechanism I could name without a fudge; candidates not tested: a sunlit/shaded two-leaf canopy with
  diffuse-light gain (Gu et al. 2003 style; cloud in the tropics is 0.54 against 0.50 temperate, so it would not
  discriminate), and a higher extinction coefficient than k = 0.5. Both need a read first.
- Grass is untouched by this lever: grassland stays 465 against MOD17 292 even with C1 (1.6x). PW-1261's thin herds, and the
  grass error in PW-1332, belong to C1 and its re-anchors.
- Savanna area falls to 18.0 Mkm2 (target band 13-27), mostly C1's doing (18.7 alone).
- One planet, observed climate, no run. KN's effect on a run's weathering (NPP_WEATHER) is not measured; wet tropics +30% would
  raise weathering where it is already high, which is the opposite sign to PW-1332's warming from lowering grass. After D47
  makes weathering read plant cover, none of this moves climate by degrees.

## Suggested next steps for a lane

1. Read Lloyd 2010 / Bonan 2011 for the profile and KN (0.11-0.5 range?) before keeping 0.4.
2. Ship KN with C1 as one change (they cancel in the total), re-anchor NPP_WEATHER or wait for D47, then veg_check, scorecard
   and the seed judge.
3. Only then look at a second tropical mechanism if the 0.7x matters.
