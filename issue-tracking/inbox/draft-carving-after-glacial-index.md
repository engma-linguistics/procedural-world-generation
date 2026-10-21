---
title: "Glacial carving (pw037-carving): unblocked for Earth zooms by the glacial index, still blocked on drifting run moments"
type: task
status: todo
parent: PW-037
subsystem: timezoom
effort: m
impact: high
found_by: pw471
blocked_by: []
relates: [PW-418, PW-471, PW-436]
refs: [docs/review/audit/PW-471-handoff.md, docs/review/audit/pw037-handoff.md, planet/timezoom/cycle.py]
---

## Description
PW-418 blocked the carving branch (pw037-carving) on two things: the zoom's ice drifting hundreds of
metres, and SIA speeds ~1 km/yr at the median (old base 4-11 m/yr), against which the carving's
calibration eroded 10-50x too much.

With the glacial index (PW-471) the ice is bounded where the zoom starts in balance:
- Earth L6, 600 kyr: sea level cycles between ~+5 and ~-100 m (glacial maxima -83..-104 m), no drift.
- SIA speeds (D |grad s| / H) under grounded sheets at Earth's first glacial maximum (82 kyr, -86 m):
  median 18 m/yr (northern sheets 23), p90 350, p99 ~1.8 km/yr. That is the old base's range for the
  interiors, with fast outlets.

So carving looks unblocked for Earth-sourced zooms: rebase the branch on the index, recalibrate the
sliding speed (pw037 handoff, step 2) on an Earth zoom, and check the erosion under the Laurentide.
Run moments are still blocked: most still lose or gain 50-200 m of their start's ice at I = 0 (the
needs-decision draft on run-moment drift), and carving calibrated there would carve the drift.
- [ ] rebase pw037-carving on PW-471 (not merged; the branch touches sia_flow and the shelves)
- [ ] recalibrate the sliding speed on an Earth L6 zoom; erosion under the ice of order 10-100 m per Myr
- [ ] decide whether carving waits for the run-moment drift fix or ships Earth/run-in-balance only
