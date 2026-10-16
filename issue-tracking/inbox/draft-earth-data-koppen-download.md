---
title: "Earth data: Koppen download fails on the Ubuntu box, so earth_check and coast_check can't run"
type: task
status: todo
parent: null
subsystem: infra
effort: xs
impact: med
found_by: fix-coast-zoom
blocked_by: []
relates: []
refs: [tools/earth_data.py, tools/coast_check.py, docs/review/baseline-2026-10-15/earth_check.txt]
---

## Description
data/earth/ on this machine holds only raw_etopo_bed/ice.npz. Building L6.npz needs the Kottek Koppen
zip from koeppen-geiger.vu-wien.ac.at, which resets the connection (urllib errno 104, curl exit 35;
other sites download fine). So tools/earth_check.py fails (the coordinator's baseline earth_check.txt is
that traceback) and so does tools/coast_check.py, though coast_check needs only elevation and ice.
The fix agent for coast-zoom ran coast_check through a scratch wrapper that builds the elevation/ice half
of earth_data._build without caching.

Fix: get raw_kottek.npz onto the box (copy it from the Mac, or another mirror of the Kottek 2006 file),
and let coast_check (and anything else needing only terrain) build/cache the terrain without the
observations (e.g. an earth_on_grid(grid, obs=False) path).
