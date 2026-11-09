# PW-1518 screens (scout 232, pass 1 of 3)

**In plain words.** I gave the rainforest tree a gain in light-use efficiency under diffuse, cloudy light, taken from
the Amazon tower where its efficiency was measured, and raised its leaves' upkeep to the rate measured in the Amazon
canopy. Its photosynthesis, growth, the share of growth in photosynthesis and its leaves' breathing all land inside the
measured ranges on Earth's observed climate, and wet-tropics growth stays where it was (a hair higher). Other biomes are
untouched. One number is still short: the forest keeps 4.3 leaf layers, against 4.6 today and 4.7-5.1 measured.

A surprise on the way: the model's own sky over the Amazon is not very diffuse. Its diffuse share runs 0.52-0.61 by
month (mean 0.56), where the K67 tower measured 0.55 in the dry season and up to 0.9 in the wet. The model's light at
the ground (Angstrom-Prescott 0.25 + 0.5 x sunshine) never gets dark enough for Df 0.9, and its two half-year clouds
flatten the seasons. So the gain the model can credit is small (+0 to +12% by month, +8.7% of the stand's GPP in the
year). It happens to be the size the leaf upkeep needed.

**Baselines.** "Main" is 8dd14a77 (this lane's merge base). All screens are `docs/review/climate/diffuse/probe.py` on
Earth's observed climate (world 506694, L6, soils on, as scout 217's `scout3_probe.py`), TrBE stand = the 674 cells
where TrBE is viable with T > 22 C and P > 2000 mm. Measured numbers name their site. Earth is a plausibility check.

## Diffuse fraction the model sees (main, `out/main.txt`, PAR-weighted)

| box | model Df | measured |
|---|---|---|
| TrBE stand | 0.56 (months 0.52-0.61) | K67 0.55 dry to 0.9 wet (Yan et al. 2017, Fig. 4) |
| wet tropics T18-32 P2500+ | 0.57 | |
| seasonal tropics T18-32 P1500-2500 | 0.54 | |
| temperate T5-15 P600+ | 0.52 | |
| boreal T-5..5 | 0.53 | |

## Candidate A screens (TrBE stand, g C/m2/yr; `out/*.txt`)

Gain: eps x (1 + 2.08 (Df - Df0)) in months with Df over Df0, today's eps below. 2.08 = Yan's K67 span
(1.9/1.1 - 1) / (0.9 - 0.55).

| | main | rl x1.5 alone | **A: TrBE gain, Df0 0.55, rl x1.5 (pass 1)** | A on all trees | A with Df0 0.52 (sensitivity) | measured |
|---|---|---|---|---|---|---|
| LAI | 4.58 | 4.11 | **4.28** | 4.28 | 4.35 | 4.7 (Manaus), 5.1 +- 0.5 (Tapajos) |
| GPP | 2827 | 2772 | **3012** | 3012 | 3130 | ~3000 (Manaus), 3144 (K67 tower) |
| NPP (stand) | 1259 | 1109 | **1270** | 1270 | 1349 | 900-1440 (Chambers 2004, Malhi 2009) |
| NPP/GPP | 0.445 | 0.400 | **0.421** | 0.421 | 0.431 | 0.32 / 0.34 / 0.49 (Malhi 2009) |
| leaf maintenance | 432 | 590 | **611** | 611 | 621 | |
| leaves incl. 34% of growth resp. | ~575 | ~716 | **~755** | ~755 | ~774 | 710-980 (Chambers 2004) |
| wood + roots incl. 66% of growth | ~993 | ~947 | **~987** | ~987 | ~1007 | 970 (Chambers 2004) |
| wet tropics box NPP (MOD17 1011, field ~1160) | 1012 | 910 | **1035** | 1052 | 1096 | |
| seasonal tropics box NPP (MOD17 920) | 905 | 834 | **913** | 932 | 951 | |
| temperate box NPP | 629 | 629 | **629** | 673 | 629 | |
| boreal box NPP | 346 | 346 | **346** | 358 | 346 | |
| land NPP, Pg C/yr (MOD17 ~56) | 61.9 | 60.4 | **62.0** | 63.5 | 62.9 | |
| forest, Mkm2 | 44.6 | 44.4 | **44.6** | 46.4 | 44.7 | |

Reading it:
- **Pass 1 meets the ticket's respiration and productivity bar**: leaf upkeep ~755 (in 710-980), stand NPP 1270 (in
  900-1440), NPP/GPP 0.421 (in 0.32-0.49), GPP 3012 at the towers' ~3000-3144, wet-tropics box 1035 against main's
  1012 (MOD17 1011, field ~1160). Wood and roots stay at Chambers' 970.
- **The LAI does not reach the measured 4.7-5.1**: 4.28 against main's 4.58. A big-leaf gain pays every leaf alike, so
  it only partly undoes the dearer leaves. Candidate B (two-leaf: the gain goes to the shaded deep leaves) is the
  mechanism that would raise it; not built in this pass (inbox draft).
- **All trees** (the same anchor for every tree) lifts temperate NPP 7% and land NPP to 63.5 Pg C/yr, further above
  MOD17's ~56. The temperate and boreal trees' eps are fitted through EPS_SCALE on Earth's land NPP under their own
  skies, so giving them a gain means refitting that; it is a decision, not part of this pass (inbox draft).
- Df0 0.52 (anchoring at the model's own dry month instead of the tower's measured 0.55) overshoots GPP and is a fit to
  the model, not a measurement. Not taken.

## Status: the code is a patch, not yet in planet/

The pass-1 code is `pass1.patch` in this folder (`git apply docs/review/climate/diffuse/pass1.patch`):
`climate.diffuse_fraction` (Yan's eq. 13) and `months()["df"]`; `vegetation.DIFFUSE = {"TrBE": (2.08, 0.55)}` read by
`_year` through two new `_KP` columns (21, 22); TrBE `rl=11.1` (x1.5). `probe.py` needs the patch applied (it reads
`s["df"]` and those columns). The screens above were run with it applied (the "A: TrBE" column is exactly the patch's
defaults). It is not committed under planet/ because the not-slow suite, the golden check, a probe re-run on the
committed defaults, `npp_check.py` against main and the scorecard could not run: the machine's load stayed at 50-93
from another session's ~32-core job from 23:44 to past 00:30, over the brief's limit of 30 for starting batches.

Next lane, in order: apply the patch; `NUMBA_NUM_THREADS=4 uv run pytest -q -n 2 -m "not slow"` (goldens will move
if any golden world has TrBE: `tests/test_golden.py --update-golden` on purpose); `probe.py` with no flags (should
match the "A: TrBE" column); `npp_check.py` on main and patched; `tools/scorecard.py`; then the 8-draw L6 screen and
the judge.

## Not done in this pass

- The 8-draw L6 coupled screen and the 36-draw judge (the ticket's last two steps). The change touches only TrBE's
  potential productivity; the coupled effects (forest cover, albedo, weathering) go through the cover, which moved by
  under 0.1 Mkm2 on Earth.

## Pass 2 (scout 239): candidate B, Yan's two-leaf canopy, in planet/

**In plain words.** Instead of paying every leaf the same diffuse-light bonus, the rainforest tree now splits its canopy
into sunlit and shaded leaves as Yan et al. 2017 do at the same Amazon tower; the shaded leaves get more efficient as
the sky gets more diffuse. That pays the deep leaves, so the forest keeps 4.85 leaf layers (measured 4.7-5.1, main
4.58), while its growth, breathing and photosynthesis stay in the measured ranges. On the coupled 8-draw screen nothing
moved measurably, but two of eight draws finished too warm against none on main: probably chaos, not yet shown.

**Code** (`planet/vegetation.py`, `planet/climate.py`; pass 1's big-leaf gain is gone): `climate.months` gives `df`
(Yan eq. 13 of the model's clearness) and `mu` (cos of the month's noon zenith, `noon_cos_zenith`).
`vegetation._two_leaf` is Yan's eq. 5-11 verbatim (eps_sun 1.11, eps_shade 4.35 x (0.25 + 0.75 Df^1.8), sunlit LAI
2 cos(theta)(1 - exp(-0.5 Omega L / cos(theta))), shaded diffuse under the canopy and the multiple-scattering term C;
read from the published PDF, White Rose eprint 124617, p. 3016, and Table 1). For TrBE (`DIFFUSE = {"TrBE": (0.8, 0.55)}`,
clumping 0.8 = Yan's Table 1 for evergreen broadleaf, after Zhou et al. 2016) the month's GPP is today's
eps x FPAR(LAI_REF) x PAR x Yan(L, max(Df, 0.55), mu) / Yan(LAI_REF, 0.55, mu): at LAI_REF 4.6 under Df 0.55 it is
exactly today's eps (the dry-season K67 value), and a month clearer than 0.55 is taken at 0.55 (today's eps is the
floor, as in pass 1). TrBE rl x1.5 as pass 1. No new fitted constant: LAI_REF is main's TrBE LAI (4.58).

Yan's shape, normalised at L 4.6 / Df 0.55 (scratch calc): canopy GPP x1.775 at Df 0.9 (K67's measured LUE span 1.1 to
1.9 is x1.73); the marginal leaf at L 4.3 earns 16% more than the big leaf's at Df 0.55, 28% more at 0.6.

### Earth's observed climate (`probe.py`, world 506694 L6, TrBE stand of 674 cells; `out/B_two_leaf.txt`)

| | main (out/main.txt) | pass 1 A (out/A_pass2.txt, re-run) | **pass 2 B: two-leaf** | measured |
|---|---|---|---|---|
| LAI | 4.58 | 4.28 | **4.85** | 4.7 (Manaus), 5.1 +- 0.5 (Tapajos) |
| GPP | 2827 | 3012 | **3038** | ~3000 (Manaus), 3144 (K67) |
| NPP (stand) | 1259 | 1270 | **1253** | 900-1440 |
| NPP/GPP | 0.445 | 0.421 | **0.412** | 0.32-0.49 |
| leaves incl. 34% of growth resp. | ~575 | ~755 | **~804** (662 + 0.34 x 418) | 710-980 (Chambers 2004) |
| wood + roots incl. 66% of growth | ~993 | ~987 | **~982** | 970 (Chambers 2004) |
| wet tropics box NPP | 1012 | 1035 | **1020** | MOD17 1011, field ~1160 |
| seasonal tropics box NPP | 905 | 913 | **895** | MOD17 920 |
| temperate / boreal box NPP | 629 / 346 | 629 / 346 | **629 / 346** | |
| land NPP, Pg C/yr | 61.9 | 62.0 | **61.7** | MOD17 ~56 |
| forest, Mkm2 | 44.6 | 44.6 | **44.5** | |

The seasonal-tropics box is 10 g C/m2/yr (1%) further from MOD17 than main: its TrBE runs at lower LAI under Df < 0.55,
where Yan's shape sits a little under the big leaf (x0.97 at L 2). Land NPP moves 0.2 toward MOD17.

### 8-draw L6 paired screen (v1-finish-16 paired.sh, ONLY l6fix + l6c_0, roll 0.0005; main b89bc1f2 vs 742d524b)

`tools/judge.py paired`: no continuous measure moved (every 95% interval spans 0): end T +0.35 C [-3.9, +3.0], late dT
-0.44 [-3.0, +2.0], late CO2 -0.02, trees % -2.8 [-6.5, +5.4], land rain -73 mm [-115, +37], arid % -0.4, hot desert
-0.6. Pass count main 8/8, two-leaf 6/8 (both 6, main only 2, two-leaf only 0; McNemar p 0.50). The two fails are warm
finishes, seed 733847 (end T +7.2 against main's +2.1) and seed 819014 (+7.4 against main's +6.9, which passed on its
finish moment); no frozen-over, no hellhouse in either arm. Lane 24's null change gave 7-8 discordant draws of 36, so 2
of 8 one way is inside chaos, but per the re-rolled-draws rule it is not shown: a second roll (0.001) on both arms, or
the judge, decides it.

### npp_check, earth_check, scorecard (main b89bc1f2 snapshot vs 742d524b, same Earth data)

- `npp_check.py` (world 506694): land NPP 61.90 -> 61.69 Pg C/yr (MOD17 ~56), biome agreement 62.4 -> 62.4%, forest
  44.6 -> 44.5 Mkm2, savanna 20.1 -> 20.2, desert 27.3 -> 27.3, vegetation carbon 600 -> 597.
- `tools/earth_check.py` L6: unchanged to the printed precision except Manaus T 25.8 -> 25.9 C and P 3667 -> 3669 mm,
  and the 0..10 / -10..0 band rain by 1 mm; Kottek agreement exact 37%, group 71% in both.
- `tools/scorecard.py` (seeds 1, 2, 1 Gyr L6): Earth part identical. The two seeds diverge from the first 100 Myr track
  point (plates, masses, peaks), so the per-seed finals are chaos, not signal: seed 1 trees 41.4 -> 46.5%, NPP 558 ->
  609, ice 0.5 -> 2.3%; seed 2 (main ends cold, ice 11.3%) trees 26.7 -> 44.8%, NPP 214 -> 671, ice 11.3 -> 0.6%.

### Verdict after pass 2

The Earth bar of the ticket is met in full, LAI included. Suite: 1890 passed, 1 failed (the golden sim, on purpose:
main's goldens pass on main; regenerated). The coupled screen is the open question: 6/8 against 8/8 with no measure
moved. Pass 3: the second roll (0.001) of the same 8 draws on both arms (or the 36-draw judge), then merge or park.

## Pass 3 (scout 243): three rolls and the verdict

**In plain words.** Pass 2's screen left one worry: two of eight test planets finished too warm with the new rainforest
canopy, against none on main. I re-ran the same eight planets twice more with the starting climate nudged a hair
(rolls 0.001 and 0.0015), on both the old code and the new. The warm finishes do not repeat as a pattern. The planet
that failed warm twice passes the third time, and the new code's other failures include two that finished too cold.
Over all 24 pairs the new code's end temperature is 0.2 C warmer than main's on the same draws, with an interval from
-1.7 to +1.8 C, so it does not move the climate. No planet froze over or boiled in either arm. The new code still
passes a few fewer planets (19 of 24 against main's 23), which is inside what chance gives but leans the same way in
every roll. The 36-draw judge on main after the merge should check that.

**Setup.** `docs/review/base-climate/v1-finish-16/paired.sh`, ONLY `l6fix|l6c_0` (8 draws, L6, 1 Gyr), MAXSIM 4 x 2
threads, on scout 239's frozen copies: main = b89bc1f2, two-leaf = 742d524b. Roll 0.0005 is scout 239's; rolls 0.001
and 0.0015 are new. Judged with `uv run python tools/judge.py paired ROOT main twoleaf --table`; full output in
`out/judge_pass3.txt`.

| roll | main passes | two-leaf passes | two-leaf fails (end T; main on the same draw) |
|---|---|---|---|
| 0.0005 | 8/8 | 6/8 | 733847 +7.2 (main +2.1), 819014 +7.4 (main +6.9) |
| 0.001 | 7/8 (583167 fails at +9.1) | 6/8 | 733847 +8.4 (main -0.8), 957317 -4.2 (main +4.5) |
| 0.0015 | 8/8 | 7/8 | 957317 -6.1 (main -4.4) |
| pooled | 23/24 | 19/24 | both 18, main only 5, two-leaf only 1; McNemar p 0.22 |

Paired B - A over the 24 draws (median, 95% interval): end T +0.20 C [-1.71, +1.80]; late dT +0.15 [-1.28, +1.34]; late
CO2 +0.02 [-0.20, +0.15]; trees % +0.25 [-3.3, +2.6]; land rain -19 mm [-73, +46]; arid % -0.35 [-1.13, +2.99]. Nothing
moved. Hard tier (frozen over at the end, hellhouse): 0 in both arms, 24/24 each. Soft tier: two-leaf 79%, above the
~60-70% bar.

Seed 733847 in detail (dT / ln CO2 every 100 Myr): both arms wander by +-4 C between 300 and 1000 Myr. Two-leaf's warm
finishes come by different paths in the two rolls (r0.0005 cools at 700-800 Myr, then warms to +8.0; r0.001 is warm at
600-700 Myr, cools at 800-900, then reaches +9.1 at 1000). Two-leaf's late CO2 on 819014 r0.0005 is lower than main's
(0.66 vs 1.14) while its end T is higher. Nothing points to a CO2 or weathering shift.

### Verdict after pass 3

Chaos: no systematic warm shift in end T or CO2, and the fails split warm and cold. The two-leaf canopy is ready to
merge with the Earth bar met in full (pass 2). The pass count leans to main in all three rolls (5 vs 1 discordant, p
0.22; lane 24's null change gave 7 vs 8 of 36). That is the ticket's open step: the 36-draw judge on main after the
merge.
