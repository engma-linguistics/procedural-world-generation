---
id: PW-318
title: Check where the LGM ice mask comes from, and test the HDF5 reader
type: task
status: done
parent: null
subsystem: infra
effort: xs
impact: low
found_by: soildata
blocked_by: []
relates: [PW-314, PW-185]
refs: [tools/earth_data.py, tools/h5_reader.py, tools/soil_check.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-314 uses the Zenodo "Global Kilometer-Resolution Dataset of Boundary Conditions for the LGM" (Shao et al., doi:10.5281/zenodo.14506525, CC BY 4.0), variable `ice_cover_boolean`, averaged to 0.25 deg. Its total ice area is 46.8 Mkm2 (Laurentide+Cordilleran 16.6, Fennoscandia+Barents-Kara 6.5, Greenland+Innuitian 5.0, Antarctica 17.7), inside the published ranges. Two loose ends:
- The record's `Dataset_Description.pdf` (34 MB, not downloaded) says which ice-sheet reconstruction the mask is built from. Read its ice section and name the reconstruction in the `earth_data.py` comment, so the "observed" mask is not an unnamed source.
- `tools/h5_reader.py` (minimal HDF5/netCDF-4 reader, chunked v3 + B-tree v1 + deflate) has no unit test; `tests/test_tiff_reader.py` covers only the TIFF reader. Add one on a small netCDF-4 file if a writer is ever available offline (none is in the dependencies), or a hand-built byte string.
- [ ] reconstruction named in `earth_data.py`
- [ ] h5 reader test

## Updates
- 2026-10-15: Status in-progress -> done. Done (d76a9c9): mask is the 1 deg PMIP3 LGM composite (ANU, ICE-6G v1.02, GLAC-1; Abe-Ouchi et al. 2015) resampled to 30 arcsec; recorded in earth_data.py. tests/test_h5_reader.py added.
- 2026-10-15: Status todo -> in-progress. Agent started.
- 2026-10-15: Created from inbox draft draft-lgm-mask-provenance.md (found by soildata).
