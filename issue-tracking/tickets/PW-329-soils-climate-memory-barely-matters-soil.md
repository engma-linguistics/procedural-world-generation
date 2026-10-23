---
id: PW-329
title: "Soils' climate memory barely matters: soil ages (h/E) are under ~3 Myr"
type: task
status: done
parent: PW-184
milestone: v2
subsystem: surface
effort: s
impact: low
found_by: soils
blocked_by: []
relates: [PW-185]
refs: [planet/soils.py, planet/timeline.py]
created: 2026-10-16
updated: 2026-10-23
---

## Description
Decision 3B (average the run's keyframe climate over each soil's age, so relic laterites survive a climate change) is built (`soils.climate_memory`, read along the plates' motion, linear between keyframes), but on the showcase world (run a1d3b9 at 380 Myr) it moves the weathering stage W by 0.01 on average (p5-p95 +-0.03) and no type visibly. The soil's age is the residence time of a <= 3 m soil (h/E, at most ~3 Myr with E >= 0.001 mm/yr), while keyframes are 4 Myr apart and climates change over tens of Myr. Earth's relic laterites are deep weathering profiles (tens of metres of saprolite, tens of Myr old), which the model doesn't represent.
Option: a separate weathering-profile age (saprolite depth / E, uncapped by the 3 m soil) for W on old flat surfaces, so relic deep weathering shows; needs a look at how far Ferralsols then spread. Lime and salt deliberately follow the present climate (they wash out within ~1e4-1e5 yr).

## Updates
- 2026-10-23: Status todo -> done. Merged (12e8922): saprolite depth D_SAP*ln(R/E) and material age (D+h)/E for W and climate memory; Ferralsols Amazon 64 -> 71%, Congo 48 -> 63%.
- 2026-10-23: soilveg lane 2: weathering-profile age. Saprolite depth D = D_SAP ln(R / E), front rate R = R_SAP x leaching water x warmth (`soils.R_SAP` 0.02 mm/yr per m/yr, `D_SAP` 10 m; capped by the time since glaciation or lava); W and the climate memory now count (D + h) / E (`age_w`, capped as before by glaciation, lava, AGE_MAX), the soil's own age (h/E) still drives lime, salt and peat. Shields in the wet tropics: ~30-40 m of saprolite, ages ~3e7 yr. Earth (soil_check, observed): group shares unchanged; Ferralsols 9.9 -> 15.2% of land (Acrisols 12.3 -> 7.0%; SoilGrids 10.5 / 9.9), Ferralsol placement Amazon 64 -> 71%, Congo 48 -> 63%; model climate: tropical red group unchanged (29.8%). Ferralsol/Acrisol split: inbox draft-soil-ferralsol-acrisol-split.md (needs-decision).
- 2026-10-23: Milestone null/later -> v2 (PW-597 triage, coordinator, 2026-10-23): soils stay under PW-184 in v2.
- 2026-10-16: Created from inbox draft draft-soil-climate-memory-weak.md (found by soils).
