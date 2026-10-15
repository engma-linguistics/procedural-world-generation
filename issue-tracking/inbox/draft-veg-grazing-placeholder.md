---
title: Replace the vegetation's grazing placeholder with fauna (PW-103)
type: task
status: todo
parent: null
subsystem: surface
effort: s
impact: low
found_by: veg
blocked_by: []
relates: [PW-103, PW-187]
refs: [planet/vegetation.py]
---

## Description
Owner decision 8 allowed a cheap grazing placeholder if grasslands closed to forest without it, marked for removal in PW-103. They did on Earth (the Great Plains and the Eurasian steppe became forest at 700-800 mm), so `vegetation.GRAZE` (0.05/yr) adds tree and shrub mortality x (C3 + C4 grass cover)^2, scaled down to zero where the climate is wet all year (P/PET >= 1.5). It makes open grassland self-sustaining (big herds need open grass), a second forest-grassland bistability next to fire. When fauna exist (PW-103), replace it by the herbivores' actual pressure, re-run tools/veg_check.py (prairie and steppe vs potential vegetation).
