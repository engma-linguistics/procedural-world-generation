---
title: Measure zoom build peaks that the RAM guard only estimates (mid resolutions, 500 km zooms, 1,200 px fine zooms)
type: task
status: todo
parent: PW-1299
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: lane283
blocked_by: []
relates: [PW-1674, PW-1337]
refs: ["planet/api.py::zoom_peak_gb", "planet/api.py::ZOOM_PEAK_ANCHORS", docs/review/land-zoom/cost.md, docs/review/land-zoom/seams-round2.md, tools/]
---

## Description
`api.zoom_peak_gb` (PW-1674) interpolates the peak memory of a zoom from three measured 4,000 km section builds
(4 km/px 6-8 GB, 2 km/px 23.1 GB, 1 km/px 85.9 GB alone; `ZOOM_PEAK_ANCHORS`), by pixel count, log-log. Nothing between or
beside those points has been measured: a 3 km or 1.5 km section, the viewer's 500 px zooms of 250-2,000 km (the
estimate is a floor of 1.5 GB, 2 GB at 1,000 km / 2 km), and fine zooms (up to 1,200 px, the estimate gives ~10.8 GB,
probably high). The guard is on the safe side where it is wrong, but a high estimate refuses fine zooms on a busy machine for
no reason. Measure with `/usr/bin/time -v` (as cost.md did) on: a 4,000 km section at 3 km/px, a 1,000 km zoom at 2 km/px,
a 500 px zoom, a 1,200 px fine zoom of a 4 km section, and a 1,200 px fine of a 2 km section; replace the anchors with the
measured table and cite it in the docstring.
- [ ] each of the five peaks measured and listed in `docs/review/land-zoom/cost.md`
- [ ] `ZOOM_PEAK_ANCHORS` (or a separate fine-zoom constant) updated; tests still pass
