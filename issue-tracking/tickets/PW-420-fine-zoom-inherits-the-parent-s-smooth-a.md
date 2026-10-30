---
id: PW-420
title: Fine zoom inherits the parent's smooth arc-rock hills with no fine detail (a0097b)
type: task
status: todo
parent: PW-649
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: pw395-volcano-form
blocked_by: []
relates: [PW-395]
refs: [planet/zoom/fine.py, "zoom a0097b"]
created: 2026-10-16
updated: 2026-10-23
---

## Description
Split from PW-395 (which now draws volcano edifices). Round lagoon a0097b
(parent 3ac681, 1 km/px) the arc-rock hills come out as smooth ~1 km blobs
40-400 m high: no volcano is involved (the volcano there is an atoll, top_m
< 0, left as the parent drew it), so this is the detail noise and landscape
pass on small inherited hills. The detail amplitude is 0.35 x the parent's
local relief x ruggedness: check whether low relief_p or rug there keeps it
near its 1 m floor, and whether the hills are held (fixed) or clamped.
- [ ] hills of 40-400 m in a fine zoom show sub-parent-pixel relief (ridges, valleys) like other land

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-16: Created from inbox draft draft-fine-zoom-smooth-inherited-hills.md (found by pw395-volcano-form).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
