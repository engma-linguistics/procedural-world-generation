---
id: PW-314
title: "Earth soil check data: SoilGrids WRB overview reader, GLiM parent rock and an LGM ice mask for the Earth world"
type: task
status: done
parent: PW-185
milestone: null
subsystem: infra
effort: m
impact: med
found_by: soilprop
blocked_by: []
relates: [PW-185, PW-132, PW-033, PW-037]
refs: [docs/proposals/soils.md, tools/earth_data.py, tools/earth_world.py, tools/veg_check.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Step 4 of the soils proposal (docs/proposals/soils.md section 7) needs three Earth inputs that `tools/earth_data.py` doesn't have yet:
- **SoilGrids 2.0 WRB most probable group** (ISRIC, CC BY 4.0): https://files.isric.org/soilgrids/latest/data/wrb/MostProbable.vrt and its overviews MostProbable.vrt.ovr (32 MB BigTIFF, deflate-compressed 128 px tiles, top level 43200 x 16800, 30 groups; legend MostProbable.qml). Read one coarse overview level (~4-8 km) with HTTP range requests and a small zlib + numpy BigTIFF reader (the project has no GDAL), cache it, and take the area mode per grid cell. Alternative HWSD v2.0 (FAO/IIASA: HWSD2_RASTER.zip 22 MB, HWSD2_DB.zip 9 MB Access .mdb; CC BY-NC-SA 3.0 IGO) only if SoilGrids proves unusable.
- **Parent rock:** the Earth world has no rock record (PW-132) and only a terrain-based rock guess (`earth_rock`). GLiM at 0.5 deg (Hartmann & Moosdorf 2012, PANGAEA doi:10.1594/PANGAEA.788537, 38 kB, CC BY 3.0) mapped onto surface.ROCKS ids as the soils' parent rock (not the world's rock layer).
- **Glaciation:** an observed Last Glacial Maximum ice mask for `glaciated_myr` ~0.02 Myr (source and licence to find; fallback: the Earth time zoom's glacial maximum, with PW-033's errors). Without it, Canada and Scandinavia count as ancient surfaces.

Done when `tools/soil_check.py` can load all three on the Earth grid at L6 in a few seconds after the first download.

## Updates
- 2026-10-15: Status in-progress -> done. Done (ef4ab22): SoilGrids WRB (overview level 1, pure TIFF reader), GLiM 0.5 deg, LGM ice (Zenodo 14506525, 46.8 Mkm2); tools/soil_check.py 0.3 s cached. GLiM->ROCKS mapping note merged into PW-185 (coordinator: A now, B parent-material classes if the soil rules need it).
- 2026-10-15: Status todo -> in-progress. Agent started (loaders + tools/soil_check.py).
- 2026-10-15: Created from inbox draft draft-earth-soil-data.md (found by soilprop).
