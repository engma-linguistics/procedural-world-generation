---
id: PW-872
title: Glacier bed rule (warm month > -8 C slides, else frozen) was set on the bare-ground frame and now reads the ice surface
type: task
status: todo
parent: null
milestone: v1
subsystem: surface
effort: s
impact: med
found_by: coupling-audit
blocked_by: []
relates: [PW-277]
refs: [planet/tectonics/earth.py, planet/timezoom/params.py, "runs 0ceebf 172922 2b0b65 6b48f5", docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Coupling audit finding C5 (severity low-med for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** planet/tectonics/earth.py erode() (main L690; branch erode): k_mult = glacial_erosion where sim.t_warm > -8, else 0.3; the line predates PW-277 (present at 30d06a8, 2026-10-13).

**Other side:** planet/tectonics/earth.py update_climate (branch L420): sim.t_warm is overwritten with the ice surface's warmest month (climate.ice_surface, PW-277, a26c7eb 2026-10-15: ~8 C colder in winter on big sheets than the old rule). The time zoom decides glacial erosion by sliding speed instead (timezoom/params.py).

**Why they disagree:** A threshold in surface-air units that was set when the temperature on ice was the bare ground's minus a cover term; after PW-277 the same number means a different bed. Two rules (run: air temperature; time zoom: sliding) for one quantity.

**Measured:** Run keyframes (every 10 Myr after 50 Myr): share of iced cells counted wet-based 0.16, 0.24, 0.18 (L6 0ceebf, 172922, 2b0b65), 0.47 (L7 6b48f5); of ice > 1 km 0.10-0.35. Antarctica's bed is ~half thawed (Pattyn 2010), so the share is plausible-ish, but the rule is no longer the one that was tuned.

**What to try:** Re-derive the bed regime from the ice's own state (thickness and surface temperature, e.g. the time zoom's sliding rule or a pressure-melting estimate), or at least re-check the -8 C on the post-PW-277 temperatures against the glacial-erosion calibration.

## Updates
- 2026-10-25: Created from inbox draft draft-glacier-bed-threshold-in-pre-pw277-frame.md (found by coupling-audit).
