---
id: PW-871
title: finish.orbit_dt (orbit_resp seasons) passes bed + ice as elevation and the ice again, so the climate sees bed + 2 x ice
type: task
status: todo
parent: null
milestone: null
subsystem: timezoom
effort: xs
impact: low
found_by: coupling-audit
blocked_by: []
relates: [PW-459, PW-555]
refs: [planet/finish.py, planet/timezoom/fields.py, docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Coupling audit finding C14 (severity low for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** planet/finish.py orbit_dt: climate.compute(grid, st["elevation"] + st["ice"], dT, tilt, ice) where st["elevation"] is the bed (frame_state).

**Other side:** planet/climate.py compute: surf = elev + ice; the time zoom calls it with the ice surface as elev and no ice (timezoom/fields.py).

**Why they disagree:** Dormant: only on orbit_resp == "seasons" (default "run"). If switched on, the finished world's per-cell orbit response is computed on ice twice as thick.

**Measured:** Code read only.

**What to try:** Pass st["elevation"] (the bed) with the ice, as world.finish does.

## Updates
- 2026-10-25: Created from inbox draft draft-finish-seasons-orbit-response-adds-ice-twice.md (found by coupling-audit).
