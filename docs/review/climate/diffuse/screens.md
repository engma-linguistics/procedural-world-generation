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
