---
id: PW-1446
title: "L7 relief overshoots Earth: 8-9.5 km cells at the 80 km cap, 2-3x Earth's land above 2 km, and 12 km zoom summits on stacked craton"
type: task
status: todo
parent: PW-244
milestone: later
subsystem: tectonics
effort: m
impact: med
found_by: scout-171-pw846
blocked_by: []
relates: [PW-846, PW-048, PW-172, PW-451, PW-827]
refs: [docs/review/tectonics/mountains/scout1.md, docs/review/tectonics/mountains/scout1_hyps.py, docs/review/tectonics/mountains/scout1_tops.py, docs/review/tectonics/mountains/scout1_highrock.py, "planet/tectonics/crust.py::flow_and_orogeny", "planet/tectonics/crust.py::stack_collisions", "planet/tectonics/isostasy.py::elevation", "planet/tectonics/isostasy.py::MAX_KM", "planet/timeline.py::texture", "run 10fd90", "run fe954c", "run a19366", "run 2b53a0", "world dba204", "zoom 7d6c4d", "zoom f4db12", data/earth/L7.npz, data/earth/raw_hydrosheds_dem_30s.zip]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: on current code the tallest L7 ground stands well above anything Earth has at the same grid size, and the zooms draw summits of 11 to 12 km (Everest is 8.85 km). If this is never fixed, the viewer and zooms keep showing mountains 3 km too tall, and anyone comparing them with Earth will trust a wrong number.

Measured by PW-846 scout 171 (docs/review/tectonics/mountains/scout1.md), comparing per-frame medians over t >= 100 Myr with Earth's L7 cell means (ETOPO1 via tools/earth_data.py):
- Land above 2 / 3 / 4 km: 7 Earth-like L7 runs (codes deecf8af and e55316ad: 2b53a0, b92096, 85f322, a19366, 10fd90, fe954c, c9f38c) have 9.7-18.3 / 3.9-8.6 / 1.6-3.7%. Earth L7 has 5.2 / 2.7 / 1.7% (ice-free land).
- The highest cell is above 7 km in most frames (10fd90 45/61, fe954c 53/60, 2b53a0 48/60), and up to 9.5 km. Earth's highest L7 cell is 5.9 km. Those top cells sit at the 80 km cap (`MAX_KM`) and stand a median 1.0-1.4 km above their own Airy height (7.0 km at 80 km), so sediment lift and swell lift single cells: the PW-048/PW-172 spike family.
- Craton rock covers 54-68% of land above 4 km. `flow_and_orogeny` leaves stacked craton as craton (erodibility 0.3; orogen is 0.6), so a plateau stacked on a craton erodes at half the rate.
- Zooms of world dba204 (run 10fd90): 7d6c4d (1 km/px) has a mean land height of 6249 m and a highest point of 12188 m on craton. f4db12 (4 km/px) reaches 11957 m. The HydroSHEDS 1 km DEM tops out at 8247 m, and Earth's highest 0.5-degree block mean is 5718 m.

What I'd try (L7 judge, 3-4 seeds x 1 Gyr, per-frame hypsometry against Earth L7):
(a) crust stacked onto craton in a collision becomes orogen rock, or the thickening favours the weaker side;
(b) a cell at the cap gets no sediment lift or swell above its Airy height;
(c) check the zoom's sub-cell relief against the HydroSHEDS table in scout1.md section 1.
Risk: less high ground lowers the weathering CO2 sink (PW-451), so the climate moves. Judge that on the two-tier bar, not on these seeds.
- [ ] L7 land above 4 km within about 1-2.5% and the highest cell at or below about 7 km in most frames, over 3+ seeds
- [ ] zoom summits at or below about 9 km

## Updates
- 2026-11-03: Created from inbox draft draft-l7-relief-overshoot-craton.md (found by scout-171-pw846).
