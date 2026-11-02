---
id: PW-1329
title: The herd fit (McNaughton 1989, across ecosystems) holds ~1.5x fewer grazers than Africa's parks at measured grass production
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane123
blocked_by: []
relates: [PW-1261, PW-1073, PW-1225, PW-966]
refs: ["planet/lineages/prey.py::wild", "planet/lineages/prey.py::above", "planet/gameattrs.py::compute", docs/review/vegetation/npp-check/diagnosis.md, docs/review/vegetation/npp-check/npp_check.py, docs/references/megafauna/mcnaughton1989_herbivore_biomass_productivity_nature.pdf, docs/references/megafauna/coe1976_african_herbivore_biomass_rainfall_oecologia.pdf, "Deshmukh 1984 Afr J Ecol 22:181 (abstract)", "Yang et al. 2020 Land Degrad Dev doi:10.1002/ldr.3715", "world 506694 (Earth L6)"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** Lane 123 found the plants were not too weak for Africa's herds; if anything grass grew too much
(fixed by giving grass roots an upkeep cost, PW-1261's lane). With the grass now near field measurements, the model's
wild herds on Earth's savanna come out at ~0.7x of the real African parks Coe et al. 1976 counted (3.1 against 4.0-4.4 t/km2
at 550-700 mm). The remaining gap is in the herd formula, not the plants: McNaughton et al. 1989's fit runs across all
ecosystems (forests, tundra, grassland; r2 0.58), and McNaughton et al. say themselves that grasslands sit above their
line for consumption (p. 143: "forests fell below the line and grasslands above").

Numbers (Earth L6, observed climate, warm African grassy cells, median herds t/km2, lane 123 `npp_check.py`):
| rain mm | before (grass CUE 0.7) | after (roots respire x2.5) | Coe Table 1 measured |
|---|---|---|---|
| 400-550 | 2.6 | 1.9 | 1.7-2.9 (406-425 mm) |
| 550-700 | 4.1 | 3.1 | 4.0-4.4 (553-650 mm) |
| 700-900 | 5.5 | 4.1 | 4.8-8.4 (784-878 mm) |
McNaughton's fit at Deshmukh 1984's measured peak grass biomass at 626 mm (512 g dry/m2) gives ~2.5 t/km2.

Options:
- **A. Accept** (a factor of ~1.4 inside the fit's own scatter; `meta.dragon_abundance` remains the lever).
- **B. A grassland/savanna offset** on McNaughton's intercept, fitted on Coe's measured herds against Deshmukh's measured
  grass production at the same rain (both on file / read); forests keep the cross-ecosystem line.
- **C. Coe's rain fit** for warm savanna (Africa-only, rain-only; not general).
Lean: B, a one-number offset for open grassy land, sourced on two African datasets.

## Updates
- 2026-11-02: Created from inbox draft draft-herd-fit-grassland-offset.md (found by lane123).
