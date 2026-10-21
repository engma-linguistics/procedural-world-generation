---
id: PW-495
title: Glacial debris dropped at marine fronts piles up in one sea cell (no fan spreading)
type: task
status: todo
parent: PW-037
milestone: null
subsystem: timezoom
effort: s
impact: low
found_by: pw037-port
blocked_by: []
relates: [PW-037]
refs: [planet/timezoom/sim.py, docs/review/audit/PW-037-handoff.md]
created: 2026-10-21
updated: 2026-10-21
---

## Description
The time zoom's carving (PW-037) drops the debris carried by ice that the sea takes (shelf melt, break-up,
calving) in the cell where that happens. Fronts that stay in one place for a long time build cell-mean
piles of 0.5-1.2 km:
- Earth L6, 600 kyr: the thickest till is 540-640 m, in sea cells off the Ross and Weddell grounding zones.
- Drifting run moments, 400 kyr: 690-1215 m in sea cells 1-2.4 km deep (seed 5 @ 260: 73.5 N -174.9 E,
  1215 m).
Real trough-mouth fans do reach 1-4 km, but over ~2.6 Myr, and debris flows spread them over 100s of km.
Ice-rafted debris spreads further still.
What to try: spread what the sea takes down the sea floor's steepest descent over a few cells (~200-300 km),
and send a small share far off as ice-rafted debris. Keep the volume conserved.
- [ ] no sea cell gets more than ~300 m of till in 600 kyr on Earth L6; volume still conserved

## Updates
- 2026-10-21: Created from inbox draft draft-glacial-debris-piles-at-marine-fronts.md (found by pw037-port).
