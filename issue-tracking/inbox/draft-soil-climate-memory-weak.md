---
title: "Soils' climate memory barely matters: soil ages (h/E) are under ~3 Myr"
type: task
status: todo
parent: PW-184
subsystem: surface
effort: s
impact: low
found_by: soils
blocked_by: []
relates: [PW-185]
refs: [planet/soils.py, planet/timeline.py]
---

## Description
Decision 3B (average the run's keyframe climate over each soil's age, so relic laterites survive a climate change) is built (`soils.climate_memory`, read along the plates' motion, linear between keyframes), but on the showcase world (run a1d3b9 at 380 Myr) it moves the weathering stage W by 0.01 on average (p5-p95 +-0.03) and no type visibly. The soil's age is the residence time of a <= 3 m soil (h/E, at most ~3 Myr with E >= 0.001 mm/yr), while keyframes are 4 Myr apart and climates change over tens of Myr. Earth's relic laterites are deep weathering profiles (tens of metres of saprolite, tens of Myr old), which the model doesn't represent.
Option: a separate weathering-profile age (saprolite depth / E, uncapped by the 3 m soil) for W on old flat surfaces, so relic deep weathering shows; needs a look at how far Ferralsols then spread. Lime and salt deliberately follow the present climate (they wash out within ~1e4-1e5 yr).
