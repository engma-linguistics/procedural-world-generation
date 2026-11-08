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

## Pass 2: judge (scout 210b, 2026-11-08)

**In plain words.** The full test on 36 planets passes. With the rainforest change no planet ends frozen over, boils,
loses its ocean or crashes its CO2, the same as main. 34 of 36 planets pass the softer checks against main's 32 (a
difference chance easily makes). The planets end a little warmer: the late climate's median is 1.4 C above today's
Earth against main's 0.8 C, all still inside the -6..+5 C bar, and the spread between planets is a little narrower.
Hot desert grows by about 1 point of land (median 6.8% of land on main, 8.6% with the change). That comes from the
warmth, not from the plants directly: in every planet the desert grows by about as much as main's own planets do per
degree of warming. The rainforest itself (trees on the wet equatorial lowland) does not change. On Earth's real
climate nothing visible moves (Koppen agreement 37%/71% on both). Verdict: merge-ready.

Baselines: "main" is e6cb463c, whose physics is identical to current main e6343d92 (`git diff e6cb463c e6343d92 --
planet tools` touches only planet/lineages and planet/server.py); "cand" is 419d5055 (this branch's physics). "Today's
Earth" is the climate model's dT = 0. Both arms ran from frozen copies (`git archive`), v1-finish-16's `paired.sh`, 2
rolls (0.0005, 0.001) x 18 draws, L6, 1 Gyr, 1 thread per run (as pass 1 and lane 185). Pass 1's 8 draws per arm (roll
0.0005, l6fix + l6c_0) were reused: same commits (the frozen code directories compare identical with `diff -r`), same
script, same thread count; main's 8th draw (l6c_0 958504) was finished by pass 1's still-running job and copied in.
The other 28 per arm were run here. Outputs: `scout2b/` (judge.txt, stats.txt, hard_bar_*.txt, yardstick.txt,
mech.txt); scripts `scout2b_stats.py` (scout 194's scout5_stats.py with the arms renamed and late cover read-outs
added) and `scout2b_mech.py`. Runs in the worktree's `exports/s210b/` (gitignored).

### The bar

| check | main | cand | verdict |
|---|---|---|---|
| hard: frozen over at the end (PW-1425) | 0/36 | **0/36** | pass |
| hard: boiled / hellhouse | 0/36 | **0/36** | pass |
| hard: ocean loss | 0/36 | **0/36** | pass |
| hard: CO2 crash (below the plants' compensation point) | 0/36 | **0/36** | pass |
| soft pass (bar + finish moment) | 32/36 | **34/36** (both 30, main only 2, cand only 4; McNemar p 0.688) | not worse |
| late dT (600-1000 Myr) range, against today's Earth (bar -6..+5) | -2.31..+4.07 | **-0.98..+4.26** | pass |
| late dT sd between draws (D47 bar about 1.3-1.7) | 1.67 | **1.43** | pass |
| learnt yardstick y, L6 (`tools/yardstick.py`; YARDSTICK 1.377) | 1.352 (se 0.028) | **1.352** (se 0.032) | no re-fit |
| reported: frozen at some moment after 300 Myr | 0 | 1 | |
| reported: CO2 under 100 ppm / end pCO2 outside 180-600 | 3 / 14 | 3 / 14 | |
| reported: glacial maximum / icehouse | 18 / 36 | 13 / 36 | |

### Paired measures (cand - main over the 36 draws; median, bootstrap 95% CI, draws up/down)

| measure | main median | cand median | median diff | 95% CI | up / down | sign p |
|---|---|---|---|---|---|---|
| late dT, C | +0.77 | +1.42 | +0.77 | [-0.26, +1.87] | 22 / 14 | 0.243 |
| (late dT, mean diff) | | | +0.82 | [+0.03, +1.55] | | |
| end T, C | -0.33 | -0.62 | +0.23 | [-2.07, +2.70] | 18 / 18 | 1.000 |
| late CO2, e-folds | +0.54 | +0.63 | +0.10 | **[+0.02, +0.22]** | 24 / 12 | 0.065 |
| hot desert (BWh), % of land | 6.83 | 8.61 | +0.95 | **[+0.03, +2.33]** | 24 / 12 | 0.065 |
| arid (B), % of land | 21.7 | 22.6 | +1.25 | [-0.25, +2.37] | 23 / 13 | 0.132 |
| land rain, mm/yr | 1140 | 1134 | +6 | [-37, +47] | 18 / 18 | 1.000 |
| trees, % of land | 39.8 | 38.6 | -0.05 | [-1.28, +2.16] | 18 / 18 | 1.000 |
| **wet equatorial lowland trees, %** | 66.8 | 66.2 | -0.35 | [-1.57, +0.85] | 17 / 19 | 0.868 |
| savanna trees, % | 55.1 | 53.6 | -1.36 | [-2.83, +0.34] | 13 / 23 | 0.132 |
| steppe trees, % | 12.6 | 11.5 | -0.60 | **[-1.40, -0.26]** | 10 / 26 | 0.011 |
| sink / source reference (ln) | 6.611 / 7.988 | 6.616 / 7.993 | -0.01 | [-0.03, +0.05] | 16 / 20 | 0.618 |

Pass 1's +2.0 points of hot desert on 7 draws comes down to +0.95 on 36 (CI just off zero, sign p 0.065).

### Why hot desert grows (scout2b_mech.py)
- **It follows the warmth.** Across the 36 pairs the desert change tracks the late-dT change (r +0.71, +0.84 points per
  C); at no warming the fit leaves +0.23 points. Main's own planets show the same relation between draws (+0.71 points
  per C, r +0.66). A warmer planet has more of its dry land over the BWh/BWk line and a higher aridity threshold;
  that is the Koppen rule working, not a plant artefact. Plausible, not a red flag.
- **The warmth comes from CO2** (late dT against late CO2 change r +0.98; CO2 forcing term +0.45 C [+0.07, +0.93]),
  and methane follows the warmth as its code says (`earth.ghg_conc` reads dT and runoff, not plants).
- **No weathering pathway was found.** None of the weathering's factors moves beyond chance (plant factor w_plant
  -0.0001 [-0.012, +0.012], bare 0.004 [-0.000, +0.009], temperature 0.04 [-0.01, +0.08], supply, area, the
  references): D47 makes the weathering read rooted cover, and the change leaves cover where it was. So the +0.10
  e-fold of late CO2 is either a small diffuse effect or chaos at the edge of the interval (the median late-dT
  interval spans zero; the mean's just clears it). It is a modest warm shift within the bar, not a mechanism to chase
  before merging. Draws colder than today's Earth over the late window: main 15, cand 5; warmer than +3 C: 3 and 7.
- **Steppe trees** fall 0.6 points (of ~12.6) with a fit intercept of -0.6 at no warming: a direct, small plant effect.
  The sourced KN 0.15 makes deep leaves dearer than lane 181's 0.4 did for every tree type, so marginal dry-land
  stands carry a little less canopy. Pass 1's Earth screen saw the same in the temperate boxes (NPP back toward MOD17).

### Scorecard and Earth check (on this branch, b5c85a97)
- `tools/earth_check.py` (L6, worktree copy of the data/earth caches), cand against main (e6cb463c's frozen copy):
  Koppen exact 37% / main group 71% on both; BWh 11.6% of land both (Kottek 14.8); land rain and the river mouths
  move by under 1%; Amazon basin rain 3351 -> 3362 mm. Nothing climatic moves on Earth's real geography.
- `tools/scorecard.py` (2 seeds, 1 Gyr L6): Earth group agreement 71.4%, exact 37.3%, log-rain corr 0.718 (last line
  with an Earth part, 93ba6fb0: 71.4 / 37.4 / 0.718). Seeds: seed 1 land NPP 558 g C/m2/yr, trees 41.4%, ice 0.5%;
  seed 2 land NPP 214, trees 26.7%, ice 11.3% (main's last line, a5de7a62, same physics as main: seed 1 552 / 45.0% /
  3.3%; seed 2 422 / 39.6% / 1.0%). Single draws: seed 2 ends in a colder, icier state, which the 36-draw judge shows
  is chaos (no shift to cold, frozen over 0/36).
- Tests: `tests/test_vegetation.py` and `tests/test_golden.py` pass (16) on the merged branch (golden as pass 1 updated it).

### Verdict
Merge-ready: hard bar 0/36, soft 34 against 32 (not worse), late dT inside the bar with a narrower spread, the yardstick
unmoved, the rainforest's trees unmoved. The hot-desert rise is real-looking but small (+1 point of land) and is the
Koppen response to a +0.8 C warmer late climate, not a plant effect.
