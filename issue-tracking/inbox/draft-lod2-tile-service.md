---
title: "LOD globe step 2: the server builds the tiles in view on demand (replace-queue, centre first, cancel on pan, RAM guard, disk cap)"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: viewer
effort: l
impact: high
found_by: lane289
blocked_by: []
relates: [PW-1198, PW-1674]
refs: [docs/review/zoom/lod-plan-v2.md, planet/zoom/lod.py, planet/server.py, "planet/api.py::zoom_estimate", "planet/api.py::zoom_peak_gb", "planet/api.py::zoom_is_heavy"]
---

## Description
**In plain words.** Nothing is pre-built (Daniel 11-10): the globe asks for the tiles on screen and the server makes them.
Without a queue that follows the view, a pan or a zoom-out leaves minutes of builds for places no longer looked at, several
builds can pile into the shared machine's memory, and the cache grows without bound. Plan: `docs/review/zoom/lod-plan-v2.md`
section 3 (step 2). Starts once the step-1 draft (`draft-lod2-seam-true-tiles`) has committed its tile build entry point;
the addressing (`lod.py`) is already there.
- `POST /api/tiles/want {world, gen, tiles}`: replaces the world's queue (dropping what is no longer wanted; a running build
  finishes and is kept); missing ancestors and the parent tiles a build reads go first; order: coarser level, then distance
  from the screen centre.
- `GET /api/tiles/status`, and tile files at `/api/tiles/<world>/<cell>/<level>/<tx>/<ty>/<file>` (`view.bin`: float16
  elevation and water; `satellite.png`; any layer by name).
- Level 1 is the existing section build (one heavy at a time, `zoom_estimate`); levels 2-4 up to three at once within free RAM
  (fine-pass anchors for `zoom_peak_gb`: ~3.5 GB per 500 px tile, measured) and the core cap.
- A disk index per world and a cap (default 60 GB) dropping least-recently-viewed tiles of levels 2-4; level 1 kept.
- [ ] a scripted client panning across a cell gets the centre tiles first; panning away drops the rest; a second visit serves
      each tile from disk in under 100 ms; tests on a scratch data root (never port 8765)
