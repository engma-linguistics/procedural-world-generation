---
id: PW-195
title: "Earth vegetation datasets for the vegetation check: potential vegetation, NPP, tree cover, burned area, observed half-year rain"
type: task
status: done
parent: null
subsystem: infra
effort: s
impact: med
found_by: vegprop
blocked_by: []
relates: [PW-187]
refs: [tools/earth_data.py, tools/earth_check.py, "world dc3732", docs/proposals/vegetation.md]
created: 2026-10-14
updated: 2026-10-15
---

## Description
The vegetation proposal (docs/proposals/vegetation.md §7) validates the model on Earth's terrain against: potential natural vegetation (Ramankutty & Foley 1999, 0.5 deg, 15 classes; not today's land cover, which includes crops), MODIS MOD17 annual NPP (land total ~53-56 Pg C/yr), MODIS VCF or Hansen tree cover, GFED4s burned area, and biome areas. `tools/earth_data.py` downloads ~25 MB once and maps datasets onto the grid; it has none of these. It also has observed annual and warmest/coldest-month temperature and annual rain, but no observed half-year (Apr-Sep / Oct-Mar) rain, which the vegetation model needs to run on observed climate (to separate vegetation errors from climate errors).

Do: add coarse (~0.5-1 deg) versions of these to earth_data.py (prefer small preprocessed products, e.g. ISLSCP II collections, to keep the download small), map them to the grid like the others, and add obs_precipitation_jul/jan to the Earth world.
- [ ] datasets downloaded once and cached, total download stays modest (< ~100 MB)
- [ ] mapped onto L6/L7 grids; documented in docs/overview.md §2.17

## Updates
- 2026-10-15: Status in-progress -> done. Merged with PW-187: Ramankutty-Foley potential vegetation in earth_data; satellite products need a login (PW-204).
- 2026-10-14: Status todo -> in-progress. Done inside PW-187 step 3 (worktree veg).
- 2026-10-14: Created from inbox draft draft-earth-vegetation-data.md (found by vegprop).
