---
id: PW-499
title: What PW-092 gets from the glacial imprint, and what it still lacks (ice flow direction)
type: task
status: todo
parent: PW-092
milestone: null
subsystem: zoom
effort: s
impact: med
found_by: pw037
blocked_by: []
relates: [PW-092, PW-037, PW-005]
refs: [planet/finish.py, planet/timeline.py, planet/zoom.py, planet/zoom_landforms.py, docs/proposals/glacial_carving.md]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Notes for the zoom synthesis (PW-092), from PW-037. A finished world now carries, per coarse cell:
`glacial_erosion` (m of bed the ice abraded, up to the frame), `glacial_till` (m dropped: till sheets,
moraine belts at long-lived margins), `ice_max` (m), and `glaciated_myr` = 0 wherever the time zoom's ice
reached (so `zoom_landforms`' shield scour already fires there). Its coarse elevation already holds the
carved basins and till, and the sub-cell texture's bumps are planed by exp(-erosion / 180 m).

Missing for oriented forms (drumlins, flutes, fjords along the flow, U-valleys aligned with outlets):
- the ice flow direction. Not stored. Cheapest: in `finish.glacial_imprint`, the surface gradient of the
  frame with the thickest ice (elevation is stored per frame), or record a sliding-weighted mean flow
  vector in the time zoom (it has the edge fluxes in `sia_flow`).
- `wet_kyr` (kyr the bed was thawed) and `slide_km` exist in the time zoom's state but aren't stored per
  frame: thawed-bed regions get drumlins / scour, frozen-bed regions keep their old landscape (Keewatin).
- Volume to distribute: the cell-mean erosion should be concentrated into troughs/fjords (a 2 km deep,
  5 km wide fjord in a 56 km cell is ~180 m cell-mean), not spread evenly.

Overlap: the zoom's rivers (`zoom_fine.py`, being edited on another branch) will meet more closed basins
and lakes on deglaciated ground in finished worlds; nothing in PW-037 touches that file.

## Updates
- 2026-10-21: Created from inbox draft draft-zoom-inputs-from-glacial-imprint.md (found by pw037).
