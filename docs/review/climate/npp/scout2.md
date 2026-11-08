# Scout 210: sourcing KN_RESP and the rainforest's low photosynthesis (PW-1331, pass 1 of 3)

**In plain words.** Lane 181 made a shaded leaf cost less upkeep than a sunlit one, with a depth constant KN_RESP = 0.4
that nobody had checked. I read the field measurements. In Amazon rainforest the leaves' enzyme (and so their upkeep) falls
with depth about 0.15 per layer of leaf, not 0.4: 0.4 was too generous. Putting the measured 0.15 in on its own takes
rainforest growth back down (827 to 711 g C/m2/yr). The real shortfall is somewhere else: the model's rainforest turns
sunlight into sugar too poorly. Flux towers in the Amazon measure 1.1 to 1.9 g of carbon per MJ of light the canopy
absorbs; the model's rainforest used 0.88, below even the towers' worst (dry-season) month. Setting the rainforest
tree's efficiency to the towers' low end (1.14) and the depth constant to the measured 0.15 brings Earth's rainforest to
1016 g C/m2/yr (satellite estimate 1011, field plots about 1160), also brings the wet temperate forests (which 0.4 had
pushed too high) back toward the satellite, and leaves savanna area, fire and the biome map where they were. Both numbers
are now read from measurements instead of tuned. It changes the plants on every planet's rainforest, so it needs the
36-planet judge before merging; I ran a smaller screen (below).

Baselines: "main" is e6cb463c (KN_RESP 0.4, the herbs' root upkeep C1 merged). Earth screens are the Earth L6 terrain
(world 506694) on observed climate, soils on, `docs/review/vegetation/npp-check/npp_check.py` (the same function
tools/veg_check.py runs). Yardsticks: MOD17A3 and the Miami model as lane 123 read them; field ~1160 is lane 123's
17-plot median from Malhi et al. 2011.

## 1. What KN_RESP is

`planet/vegetation.py::_year`: a stand's yearly leaf maintenance respiration is `rl x leaf x Q10`, where `leaf` was the
LAI L and, with KN > 0, is the canopy integral (1 - exp(-KN L)) / KN. This is the integral of a respiration rate that
falls as exp(-KN z) with cumulative leaf area z from the top: the profile of leaf enzyme capacity (Vcmax / Amax), with
dark respiration a fixed share of capacity. KN is per unit of LAI (not normalised by total LAI), applied to trees,
shrubs and ground cover; herbs keep the linear form. It acts on respiration only; photosynthesis stays the big-leaf
eps x fAPAR x PAR with light extinction k = 0.5. So in the model KN only sets how cheap the deep leaves are, and
through that the optimum LAI.

## 2. What the literature gives (read this session)

| source (read) | what it says | KN per unit LAI |
|---|---|---|
| Lloyd et al. 2010, Biogeosciences 7:1833 (full text) | Amazon forest, 204 trees/57 sites. Tapajos: "kP ~0.15" observed, with L = 5.1 +- 0.5 (Aragao et al. 2005); their optimisation gives kP 0.123 and L 4.5. Light extinction for tropical forest kI = 0.7 (Wirth et al. 2001); "in no case is the predicted kP even close to that of the light extinction coefficient". Dark respiration scales with capacity: Rd(z) = 0.08 Amax(z). | **~0.12-0.15** |
| Lloyd et al. 2010, Fig. 10 | 18 literature profiles of broadleaf forests: loge(kV) = 0.00963 Vmax(0) - 2.43 (kV per unit L) | 0.13 at Vmax(0) 40, 0.16 at 60, 0.22 at 100, 0.28 at 120 umol/m2/s |
| Lloyd et al. 2010, Sect. 6.2 | de Pury & Farquhar 1997's sun/shade model used "a kV of ca. 0.3" | 0.3 (a model value) |
| Lloyd et al. 2010, Table B1 | modelled optimal kP over capacities and LAI: 0.00-0.57 | range |
| Clark et al. 2011, GMD 4:701 (JULES, full text) | Vcmax25,i = n_e n0 exp(-kn i/n), "kn a nitrogen profile coefficient estimated to be 0.78", from Mercado et al. 2007's Amazon profile (Carswell et al. 2000). Normalised by relative depth i/n, so per unit LAI it is 0.78 / L. Also: uniform N "produce[s] very large respiration fluxes from leaves in the shaded understorey"; option 5 inhibits leaf respiration 30% in light. | 0.78 / 5 = **0.16** |
| CLM 6.0 technical note (escomp.github.io, read by a fetch agent) | k_n,ext "the extinction coefficient for N through the canopy (0.3)", in a two-stream form; Rd25 = 0.015 Vcmax25 scales with Vcmax | 0.3 (a model value, not Amazon-specific) |
| Not read | Bonan et al. 2011, Mercado et al. 2007/2009, de Pury & Farquhar 1997 originals, Niinemets 2007 (paywalled or not found) | - |

**Verdict.** 0.4 is not supported for tropical evergreen forest: the Amazon measurements and the model fitted to them
give 0.12-0.16 per unit LAI, the cross-forest fit 0.13-0.28, and the land models' own values 0.15 (JULES) and 0.3 (CLM,
de Pury & Farquhar). Only high-capacity canopies (top-leaf Vmax > ~130) reach 0.3-0.5. **KN_RESP = 0.15**, the Tapajos
observation, which JULES's Amazon-derived value matches.

## 3. The GPP diagnosis

Wet-tropics TrBE stand (`exports/scout210/probe.py`, T > 22 C, P > 2000 mm, 679 cells; model PAR from CRU sunshine via
Angstrom-Prescott, 2992 MJ PAR/m2/yr):

| | main (KN 0.4) | KN 0.15 + TrBE eps 1.43 | measured |
|---|---|---|---|
| LAI | 5.04 | 4.56 | 5.1 +- 0.5 (Tapajos, via Lloyd 2010) |
| fAPAR (k 0.5) | 0.89 | 0.87 | |
| absorbed PAR, MJ/m2/yr | 2661 | 2607 | |
| GPP, g C/m2/yr | 2196 | 2815 | 3144 (Tapajos tower, Hutyra et al. 2007, as Lloyd 2010 gives it: 262 mol C/m2/yr); ~3000 (Malhi et al. 2011, read by scout 173) |
| GPP / absorbed PAR, g C/MJ | 0.83 | 1.08 | 1.1 (dry season) to 1.9 (wet season) at K67 (Yan et al. 2017) |
| NPP / GPP | 0.42 | 0.45 | ~0.30 (Malhi 2011); forests 0.46 +- 0.12 (Collalti & Prentice 2019, as the code cites it) |

- **The light is not the problem.** Main's canopy already absorbs ~89% of the light at LAI 5 (KN 0.4 did that). With the
  tower GPP 3144 the model's absorbed light implies a canopy LUE of 3144 / 2661 = 1.18 g C/MJ, inside the measured
  1.1-1.9. So the model's PAR under observed cloud is consistent with the towers; it is not low.
- **The efficiency is.** TrBE's eps x EPS_SCALE = 1.10 x 0.8 = 0.88 g C/MJ absorbed is below the lowest month measured
  at K67 (1.1, Yan et al. 2017, Fig. 4 text: "a lower LUE (e.g., down to 1.1 g C MJ-1 m-2 at K67) in dry seasons").
  The towers' LUE rises with the diffuse share of the light (Df 0.55 dry to 0.9 wet at K67; Yan's DTEC model gives
  shaded leaves 4.35 against sunlit 1.11 g C/MJ). The model has no diffuse-light gain, so I take the dry-season (least
  diffuse) floor: TrBE eps 1.43 (x 0.8 = 1.14). EPS_SCALE stays: the temperate and cold boxes do not need it changed
  (lane 123: all efficiencies x1.25 overshoots them).
- **NPP/GPP comes out high** (0.45 against Malhi's ~0.30 for tropical forest) on both main and the candidate: the
  rainforest reaches its NPP with ~10% too little GPP and too little upkeep. Still inside the all-forest spread
  (0.46 +- 0.12). Not chased here (it is the wood and root upkeep, rw, not KN); noted as a follow-up.

## 4. Earth screens (NPP, g C/m2/yr; areas Mkm2)

| | main | KN 0.15 only | KN 0.3 only | KN 0.15 + TrBE&TrBR eps x1.3 | KN 0.15 + TrBE x1.2 | **KN 0.15 + TrBE x1.3 (cand)** | KN 0.4 + TrBE x1.3 | MOD17 | Miami |
|---|---|---|---|---|---|---|---|---|---|
| land NPP, Pg C/yr | 60.0 | 57.2 | 59.0 | 64.4 | 60.2 | **61.9** | 64.7 | ~56 | |
| savanna (band 13-27) | 20.0 | 20.6 | 20.1 | 15.7 | 20.3 | **20.1** | 19.5 | | |
| forest | 45.0 | 44.1 | 44.7 | 49.0 | 44.4 | **44.6** | 45.4 | | |
| burned, Mkm2/yr | 5.36 | 5.37 | 5.36 | 5.05 | 5.37 | **5.37** | 5.37 | | |
| potveg agreement, % | 62.4 | 62.2 | 62.4 | 62.9 | 62.3 | **62.4** | 62.5 | | |
| T 18-32, P 2500+ (wet tropics; field ~1160) | 827 | 711 | 788 | 1116 | 909 | **1016** | 1130 | 1011 | 1099 |
| T 18-32, P 1500-2500 | 769 | 688 | 741 | 999 | 827 | **905** | 987 | 920 | 961 |
| T 18-32, P 750-1000 (savanna) | 682 | 680 | 681 | 685 | 680 | **681** | 683 | 476 | 593 |
| T 10-18, P 1000-1500 (wet temperate) | 878 | 823 | 859 | 828 | 824 | **825** | 880 | 741 | 734 |
| T 10-18, P 1500-2500 | 894 | 823 | 871 | 834 | 827 | **829** | 900 | 982 | 836 |
| T 0-10, P 500-750 | 476 | 456 | 469 | 456 | 456 | **456** | 476 | 469 | 392 |
| T 0-10, P 750-1000 | 572 | 541 | 562 | 541 | 541 | **541** | 572 | 564 | 466 |
| forest/woodland potveg group | 565 | | | | | **598** | | 634 | 576 |
| vegetation carbon, Pg | 573 | | | | | **600** | | | |

Reading it:
- Wet tropics 827 -> 1016: MOD17 1011, Miami 1099, field ~1160 (0.71x -> 0.88x of the field median). The 1500-2500 mm
  tropics 769 -> 905 (MOD17 920). Inside the Earth plausibility range; I stop here (no closing of the last 12%).
- Wet temperate 878 -> 825 (MOD17 741, Miami 734: +18% -> +11%) and the 0-10 C boxes 476/572 -> 456/541 (MOD17
  469/564): the sourced KN takes back the temperate overshoot lane 181 introduced.
- Savanna, fire, forest area and the biome map do not move: only the evergreen rainforest tree changes. Raising the
  raingreen tree too (TrBR, as lane 123 screened) shrinks savanna to 15.7 and has no tower LUE behind it; not done.
- Land NPP 60.0 -> 61.9 Pg C/yr (MOD17 ~56): +3%, all in the tropics, where the model was low.

## 5. Coupled-climate screen (8 L6 draws, not the judge)
The change moves every planet's rainforest, so it moves the run. The full 36-draw judge (72 runs, ~4-5 h at this
scout's 8 cores) did not fit, so this is a small screen: v1-finish-16's `paired.sh`, tags l6fix + l6c_0 (8 draws), roll
0.0005, 1 Gyr, THREADS 1, frozen code (main = e6cb463c, cand = 419d5055), outputs `exports/scout210/judge/`. Main's 8th
draw (l6c_0 958504) was still running at the write-up, so the paired numbers are over 7 draws.

| check | main | cand |
|---|---|---|
| hard: frozen over at the end / boiled / ocean loss / CO2 crash (`tools/hard_bar.py`) | 0/7 | **0/8** |
| soft pass (`tools/judge.py paired`) | 5/7 | 7/7 (both 5, cand only 2, main only 0; McNemar p 0.5) |
| learnt yardstick y, L6 (`tools/yardstick.py`; YARDSTICK 1.377) | 1.435 (se 0.059) | 1.430 (se 0.075) |

Paired cand - main over the 7 (median, bootstrap 95% CI): late dT +0.90 C [-0.64, +3.42], end T +0.60 [-1.72, +5.23],
late CO2 +0.18 [-0.07, +0.47], trees +2.5 pt [-1.3, +6.0], land rain +108 mm [-16, +132], arid +1.7 pt [-0.9, +3.7],
**hot desert +2.0 pt [+0.7, +2.7]** (6 of 7 up, sign p 0.125). The only interval off zero is hot desert; on 7 draws
with the sign test at 0.125 it is not a finding, but it is the measure to watch on the full judge. The yardstick does not
move (1.430 against main's 1.435 on the same draws), so no re-fit is needed for this change.

Not run: the 36-draw judge, `tools/earth_check.py` (the change touches no climate code; lane 181 found the Koppen
check unchanged for KN), `tools/scorecard.py`.

## 6. Open
- The full 36-draw paired judge (lane 181's way) before merging; plus `tools/yardstick.py` on the candidate arm (plant
  cover changes move the learnt yardstick) and `tools/earth_check.py`, `tools/scorecard.py`.
- Diffuse-light gain (Yan et al. 2017's two-leaf form) is the mechanism behind the wet-season LUE; not modelled.
- Tropical NPP/GPP ~0.45 against ~0.30.

Files: `exports/scout210/` (gitignored): npp_check JSONs per variant, `tab.py`, `probe.py`, `run.sh`, judge runs.
Sources read: Lloyd et al. 2010 (bg-7-1833-2010.pdf), Clark et al. 2011 (gmd-4-701-2011.pdf), Yan et al. 2017
(JGR Biogeosci 122:3014-3030, White Rose eprint 124617), CLM 6.0 photosynthesis technical note (fetched page).
