---
id: PW-204
title: "Earth vegetation data: MODIS NPP, tree cover and GFED burned area need an Earthdata login or GB downloads"
type: task
status: todo
parent: null
subsystem: infra
effort: s
impact: low
found_by: veg
blocked_by: []
relates: [PW-195, PW-187]
refs: [tools/earth_data.py, tools/veg_check.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-195 asked for coarse NPP (MODIS MOD17), tree cover (MODIS VCF / Hansen), burned area (GFED4s) and potential vegetation. Only potential vegetation was practical: Ramankutty & Foley (1999), a 0.5 MB ASCII grid from SAGE (now in earth_data.earth_potveg, used by tools/veg_check.py). The others:
- MOD17 annual NPP: free at files.ntsg.umt.edu, but only as 30-arcsec global GeoTIFFs (~1 GB a year) or 12 monthly 0.05 deg GeoTIFFs; NASA NEO's 1-degree CSVs are gone (moved to science.nasa.gov).
- MODIS VCF tree cover and GFED4s: Earthdata login (LP DAAC / ORNL DAAC) and HDF files.
veg_check uses published numbers instead (global NPP ~56 Pg C/yr, GFED ~4-5 Mkm2/yr, biome areas) and approximate MOD17 zonal means good to ~20%; no tree-cover correlation is computed.
Options: (A) the owner provides an Earthdata token and we fetch VCF and GFED once (HDF needs a reader: h5py as a dev dependency); (B) stay with published numbers (current); (C) fetch the 12 monthly 0.05 deg MOD17 GeoTIFFs (~hundreds of MB) and write a minimal TIFF reader. Lean: B now, A if an account exists.

## Updates
- 2026-10-15: Status needs-decision -> todo. Coordinator decision (north star): keep the published global numbers; no Earthdata account exists. Revisit only if vegetation tuning stalls on missing spatial data.
- 2026-10-15: Created from inbox draft draft-veg-earth-datasets-login.md (found by veg).
