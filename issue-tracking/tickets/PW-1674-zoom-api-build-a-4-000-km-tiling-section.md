---
id: PW-1674
title: "Zoom API: build a 4,000 km tiling section by its cell, list a world's sections, and refuse zoom jobs the free RAM can't hold"
type: task
status: done
parent: PW-1299
milestone: v1.0
subsystem: zoom
effort: m
impact: high
found_by: lane282
blocked_by: []
relates: [PW-1198, PW-1338, PW-1341, PW-1337, PW-1438]
refs: [docs/review/zoom/lod-plan.md, "planet/api.py::parse_zoom_request", "planet/api.py::zoom_job", "planet/api.py::free_ram_gb", "planet/api.py::_fine_zoom_job", "planet/zoom/tiling.py::sections", "planet/zoom/tiling.py::section", "planet/zoom/regional.py::Frame", "planet/zoom/fine.py::zoom", "planet/server.py::serve", docs/review/land-zoom/cost.md, docs/review/land-zoom/tiling.md, "world dba204"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
**In plain words.** The viewer's level-of-detail flow (plan `docs/review/zoom/lod-plan.md`, step 1) opens the fixed
tiling section that holds a clicked spot. The CLI can build a section (`planet zoom WORLD --section px.1.1`, PW-1338)
but `/api/zoom` takes only lat/lon/size/res, there is no listing of a world's sections, and zoom jobs have no RAM check:
with the server's 4 workers (`server.py` JOBS = 4) four 2 km sections want ~92 GB (23.1 GB each, cost.md) and a single
1 km section 86-110 GB, past the shared-machine cap. If never done, the viewer cannot open sections and two clicks can
push the machine into swap or OOM.

- [ ] `POST /api/zoom {world, section, res_km}` builds or reuses the section (Frame with the cell's `up`); ids stay deterministic
- [ ] `GET /api/sections?world=` lists cells: id, centre, `up`, corners, land share, built zoom ids by resolution
- [ ] zoom jobs check MemAvailable against the expected peak (4 km ~8 GB, 2 km ~25 GB, 1 km ~110 GB) plus a margin, as refine does, and run at most one section-sized job at a time; a refusal names the RAM needed
- [ ] fine zooms are built in their parent's orientation (`up` = the parent's), the generation half of PW-1341
- [ ] tests for the request parsing and the guard; `uv run pytest -q` passes

## Updates
- 2026-11-10: Status todo -> done. Lane 283 merged (914bfded): GET /api/sections, POST /api/zoom {world, section, res_km}, RAM guard (api.zoom_peak_gb), one section-sized zoom at a time, fine zooms in the parent's orientation. Follow-ups: PW-167x drafts (guard sums running jobs, measure mid/fine peaks, viewer turned-fine check).
- 2026-11-10: Created from inbox draft draft-lod-2-sections-in-api.md (found by lane282).
