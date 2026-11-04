---
id: PW-1343
title: "Matched land zoom: held ground under the neighbour's ice may be bare and below the sea until final()"
type: task
status: todo
parent: PW-1299
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: lane128
blocked_by: []
relates: [PW-1301]
refs: ["planet/zoom/match.py::hold", "planet/zoom/match.py::final", "planet/zoom/match.py::sources", "planet/zoom/stage_finish.py::vegetation_layers", "planet/zoom/stage_finish.py::ice_bed", "planet/vegetation.py::classify", "planet/geo.py::is_land", docs/review/land-zoom/seams-round2.md, "zoom fe600a", "zoom 59336f", "world dba204"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
**In plain words.** When a land-zoom section is built to match a neighbour that is already built, it copies the
neighbour's ground on the strip the neighbour owns. Under the neighbour's ice sheet that ground is the rock bed, which
can lie far below sea level (to -6,800 m under the ice range's sheet in zoom fe600a). The new section only puts the
neighbour's ice back on top at its very last step; if its own ice doesn't happen to cover that strip in the steps
before, the vegetation step sees bare ground below the sea and the build crashes (`is_land: N cells is no sphere grid`).

Lane 128 hit this crash with lake beds (fixed: lakes are held at their surface, bare held ground floored at +0.5 m in
`match.hold`), but kept the ice bed as it is, since a floor there would lift the neighbour's bed. Not seen on the five
4 km practice pairs (the new section's own glacier covered the neighbour's ice each time).

Options: (A) give held ground the neighbour's glacier and ice thickness at `hold()` (set `ctx.glacier`/`ctx.ice_th`
from `m_ice` there, before the landscape pass), so every stage sees ice over a sunk bed; (B) hold the ice *surface*
(bed + ice) through the landscape and climate stages, and put the bed back in `final()`. Lean A.
- [ ] a matched build whose neighbour has a marine ice sheet on the held strip, and this section's own glacier
  does not cover it, finishes (a synthetic test: neighbour with ice over a bed below 0, this section warm)

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: zoom polish; zooms are good enough to read
- 2026-11-02: Created from inbox draft draft-land-zoom-held-ice-bed-before-final.md (found by lane128).
