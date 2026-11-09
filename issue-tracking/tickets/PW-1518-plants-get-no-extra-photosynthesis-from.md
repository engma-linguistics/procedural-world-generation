---
id: PW-1518
title: Plants get no extra photosynthesis from diffuse (cloudy-sky) light; the rainforest's leaf upkeep waits on it
type: task
status: done
parent: null
milestone: later
subsystem: surface
effort: m
impact: low
found_by: scout217
blocked_by: []
relates: [PW-1517, PW-1331]
refs: ["planet/vegetation.py::_year", "planet/vegetation.py::_TUNE (TrBE eps 1.43)", "planet/vegetation.py::KN_RESP", "planet/climate.py::shade_from_hours", docs/review/climate/npp/scout3.md, docs/review/climate/npp/scout3_probe.py, docs/review/climate/npp/scout3/, docs/review/climate/npp/scout2.md, docs/review/vegetation/npp-check/npp_check.py, "Yan et al. 2017 JGR Biogeosci 122:3014 doi:10.1002/2017JG004008 (White Rose eprint 124617)", "Chambers et al. 2004 Ecol Appl 14:S72 (Table 2)", "Atkin et al. 2015 New Phytol 206:614", "Malhi et al. 2009 GCB 15:1255", "world 506694 (Earth L6)"]
created: 2026-11-08
updated: 2026-11-09
---

## Description
**In plain words.** Under cloud, sunlight comes from the whole sky and reaches the shaded inner leaves of a forest.
Amazon towers fix 1.1 g of carbon per MJ of absorbed light in the sunny dry season, and up to 1.9 under the wet
season's cloud (Yan et al. 2017, K67 Tapajos). The model's plants get the same efficiency whatever the sky. Because of
that, scout 210 had to take the dry-season floor for the rainforest tree (TrBE eps 1.43, i.e. 1.14 g C/MJ). Scout 217
found that the rainforest's leaves breathe too little: about 575 g C/m2/yr against 710-980 measured at Manaus
(Chambers et al. 2004), and a top-leaf rate x1.6 under Chambers' in-situ rate. The measured fix (TrBE rl x1.5) cannot
go in alone. The model would keep fewer leaf layers (LAI 4.58 -> 4.11, measured 4.7-5.1) and wet-tropics NPP would fall
10% (1012 -> 910 g C/m2/yr, satellite 1011). The missing photosynthesis (+6%, a canopy efficiency of 1.23 g C/MJ, i.e.
Df ~0.61 on K67's span) is what a diffuse-light gain supplies.

What misleads if never done: the rainforest's respiration stays about 20-40% under the measured leaf upkeep, and any
carbon read-out that splits GPP into respiration and growth is off. Cloudy and sunny climates also grow the same per
unit of light, so a cloudier world's forests are under-credited. The impact is low: the rainforest's NPP and NPP/GPP
(0.445, measured 0.32-0.49) are inside the measured ranges today.

- [x] derive a monthly diffuse fraction Df from the model's cloud (the shade the PAR already uses), as Yan et al. did
  from the sky clearness index
- [x] a two-leaf or Df-linear efficiency for trees (Yan: sunlit 1.11, shaded 4.35 x (0.25 + 0.75 Df^1.8) g C/MJ), with
  the clear-sky floor kept at today's eps; check whether the optimal LAI rises toward the measured 4.7-5.1
- [x] then TrBE rl x1.5 (Chambers' in-situ canopy leaf rate 0.54 umol/m2/s against the model's 0.33 at 25 C)
- [x] Earth screens with scout3_probe.py and npp_check.py: wet-tropics NPP near 1011-1160, LAI, NPP/GPP; temperate
  boxes against MOD17 if the gain applies to all trees (EPS_SCALE is fitted there)
- [x] then an 8-draw L6 screen (3 rolls, scout 243)
- [x] then the 36-draw judge (on main after the merge; watch the pass count, see the 2026-11-09 pass 3 update)

## Updates
- 2026-11-09: Status todo -> done. Runner 252 36-draw judge (a61b5454): hard 36/36 both; soft 30/36 vs main 34/36 (p 0.29); continuous measures unmoved. Lean watched in the new ticket.
- 2026-11-09: Runner 252: 36-draw L6 judge, two-leaf (99db109f) vs main before the merge (00cfe6d3), same draws, rolls 0.0005 0.001. Hard tier 0/0 (36/36 each). Soft pass 30/36 (83%) vs 34/36 (94%); discordant main-only 6, two-leaf-only 2, McNemar p 0.29. End T +0.38 C [-1.57, +1.70], late CO2 +0.009 [-0.12, +0.13], nothing moved. Above the bar; PW-1518 stays merged. Glacial maximum 18 vs 13 of 36 (reported only). docs/review/climate/diffuse/screens.md#36-draw-judge-runner-252-2026-11-09.
- 2026-11-09: Scout 243 pass 3 of 3: rolls 0.001 and 0.0015 of the same 8 L6 draws (l6fix + l6c_0) on both arms. Pass counts main 8/8, 7/8, 8/8 (23/24), two-leaf 6/8, 6/8, 7/8 (19/24); McNemar 5 vs 1 discordant, p 0.22. Hard tier 100% in both arms (no frozen, no hellhouse). On the 24 pairs, end T +0.20 C [-1.71, +1.80] and late CO2 +0.02 [-0.20, +0.15], so no measure moved. Two-leaf's fails go both ways: warm on 733847 (r0.0005, r0.001; it passes at r0.0015 +2.9) and 819014 (r0.0005), cold on 957317 (r0.001 -4.2, r0.0015 -6.1). Verdict: chaos, not a warm shift; merged squashed. The pass count leans to main in all three rolls, so the 36-draw judge stays open. docs/review/climate/diffuse/screens.md#pass-3-scout-243-three-rolls-and-the-verdict.
- 2026-11-09: Scout 239 pass 2 of 3: Yan et al. 2017's two-leaf canopy for TrBE (vegetation._two_leaf, climate.months df/mu) + TrBE rl x1.5. Earth (world 506694): LAI 4.85 (4.7-5.1), GPP 3038, NPP 1253, leaf respiration ~804 (710-980); other biomes unchanged. 8-draw L6 screen r0.0005: no measure moved, passes main 8/8 vs 6/8. docs/review/climate/diffuse/screens.md#pass-2-scout-239-candidate-b-yans-two-leaf-canopy-in-planet
- 2026-11-09: Scout 232 pass 1 of 3: diagnosis docs/review/climate/diffuse/diagnosis.md (Yan 2017, Mercado 2009); candidate A (TrBE light-use gain with diffuse share + leaf respiration x1.5, Chambers 2004) meets GPP/NPP/respiration on Earth's climate, other biomes unchanged; LAI 4.28 vs 4.7-5.1. Kept as docs/review/climate/diffuse/pass1.patch, not applied: suite, goldens, scorecard and L6 screen not run (machine load 40-220 from another session). Next: apply and check.
- 2026-11-08: Created from inbox draft draft-diffuse-light-gain.md (found by scout217).
