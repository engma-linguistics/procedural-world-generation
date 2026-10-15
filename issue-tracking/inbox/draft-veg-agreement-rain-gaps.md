---
title: "Vegetation agreement on the model's Earth climate stuck at ~44%: the gap is regional rain (Sahel, India, E Europe and W Siberia, Congo)"
type: task
status: todo
parent: PW-013
subsystem: climate
effort: l
impact: med
found_by: vegclim
blocked_by: []
relates: [PW-210, PW-026, PW-015, PW-203]
refs: [tools/veg_check.py, tools/earth_check.py, "world ea00e3"]
---

## Description
Follow-up to PW-210 from the vegclim branch. After the streak fix (PW-211), the vegetation feedbacks (PW-203) and the AET/PET-based summer cooling, potential-vegetation agreement on the model's Earth climate is 43.7% (was 43.9%; target 50; on the observed climate 62.4%). One part did move: NE Canada's treeline (veg_check sector -60) went from 60.9 to 53.4 deg, onto the observed one (53.4), and sector -90 from 67.2 to 60.1 (57.4), because wet cool summers now evaporate near their potential and stay cooler.

The rest is regional rain, not anything the vegetation or a small nudge can fix (Earth world ea00e3, earth_check regions, model vs GPCC mm/yr):
- European Russia 480 vs 590 with winters 5 C too cold (Tc -14.8 vs -9.9), W Siberia 267 vs 503: steppe and grassland reach far north where forest should be (largest confusion: potential forest -> model grassland ~6 Mkm2). Same root as PW-026 (maritime air doesn't reach far enough inland).
- Sahel 1672 vs 593 (savanna and forest where it should be steppe), India 612 vs 1109 and SE China 846 vs 1462 (too dry: grass and savanna where forest), Congo 1185 vs 1652 (savanna south of the forest): the monsoon and the rain belt's reach (PW-013, PW-015).
- Tried as nudges and dropped (no effect on any of these regions or on Koppen): storm eddy mixing `eddy` 1.0 -> 1.5, winter air-mass reach `air_km_w` 900 -> 1300 km.
Use veg_check's model-climate agreement as a score for the PW-013 rain work; expect most of the remaining 6 points from the Sahel/India monsoon structure and the interior winter moisture.
