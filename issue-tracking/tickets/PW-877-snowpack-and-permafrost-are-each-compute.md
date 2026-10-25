---
id: PW-877
title: Snowpack and permafrost are each computed by several rules (months vs icemass; three permafrost tests)
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: s
impact: low
found_by: coupling-audit
blocked_by: []
relates: []
refs: [planet/climate.py, planet/icemass.py, planet/soils.py, planet/vegetation.py, planet/hydrology.py, docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Coupling audit finding C13 (severity low for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** planet/climate.py months: snowmelt at the monthly mean with no day-to-day scatter (SNOW_DDF, ramp -2..+2 C), gdd5 with sd 4; comment "as earth.ICE_DDF", which no longer exists; earth.degree_days (sd 5) has no callers.

**Other side:** planet/icemass.py: positive degree-days with sd 5, DDF 3/8, refreeze 60%. Permafrost: soils.py (nival offset on temp), vegetation.flooded (temp < -2), hydrology (>= 6 months below -2 C).

**Why they disagree:** Snow albedo, soils' permafrost, satellite snow and game attributes use months' snow while ice caps start on icemass's; the three permafrost tests disagree at their margins.

**Measured:** Code read only; not measured.

**What to try:** Let months take icemass's PDD melt (one snow rule), share one permafrost class (soils') with vegetation and hydrology, drop the dead helper and stale comment.

## Updates
- 2026-10-25: Created from inbox draft draft-snow-and-permafrost-rules-diverge.md (found by coupling-audit).
