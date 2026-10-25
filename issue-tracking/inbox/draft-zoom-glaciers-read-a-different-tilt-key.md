---
title: "Zoom glaciers read the tilt from meta.params.tectonics, the zoom's climate and plants from meta.params"
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: xs
impact: low
found_by: coupling-audit
blocked_by: []
relates: []
refs: [planet/zoom.py, planet/zoom_fine_forms.py, docs/review/coupling-audit/]
---

## Description
Coupling audit finding C11 (severity low for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** planet/zoom.py:1900 and zoom_fine_forms.py:76: params.tectonics.tilt (default 23.4).

**Other side:** planet/zoom_vegetation.py:289, zoom.py:3352, 3633, 3657: params.tilt (world.py writes it).

**Why they disagree:** Generated worlds (no tectonics key) and Earth worlds get 23.4 for glacier mass balance whatever their tilt, while plants and satellite use the true tilt.

**Measured:** World 2a7385 has both keys (23.4 each); the mismatch only bites on non-default tilt without a tectonics block. Not measured further.

**What to try:** Read meta.params.tilt everywhere.
