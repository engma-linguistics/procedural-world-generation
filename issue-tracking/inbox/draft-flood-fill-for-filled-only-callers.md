---
title: Use kernels.flood_fill where only priority_flood's filled surface is used (zoom, highlights)
type: task
status: todo
parent: PW-247
subsystem: zoom
effort: xs
impact: low
found_by: pw255-lakes-speed
blocked_by: []
relates: [PW-255]
refs: [planet/kernels.py, planet/zoom.py, planet/highlights.py]
---

## Description
PW-255 added `kernels.flood_fill(elev, outlet, nbr_off, nbr_idx, eps)`: `priority_flood_to(...)[0]`
alone, bit-identical, ~2.5x faster at L6 (1.5 vs 3.7 ms), because the filled surface doesn't depend on
the order tied cells are taken in, so the sea's inner cells needn't be queued. `zoom.coarse_lakes`
(`hydrology.priority_flood(g, elev)[0]`) and `highlights.py` (lines ~612 and ~1219, filled only) could
call it (`kernels.flood_fill(elev, elev <= 0, g.nbr_off, g.nbr_idx, 0.01)`). Milliseconds per call, so
only worth doing when those files are next touched; left to their owners (PW-255 stayed in
hydrology.py / kernels.py).
