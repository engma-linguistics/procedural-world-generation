---
title: "Store each frame's full people presence as bit flags so demes see peoples that rarely lead a cell"
type: task
status: todo
parent: PW-981
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun46-demes
blocked_by: []
relates: [PW-981, PW-689]
refs: [planet/lineages/history/frame.py, planet/lineages/output.py, planet/lineages/demes.py, "run b69f51"]
---

## Description
In plain words: a stored peoples run remembers, for each cell and frame, only the people that holds the most ground there
and the top two by heads. A people that lives everywhere as a minority (orcs among humans, tortles on coasts, the deep
folk under everyone) is nearly invisible to the demes pass, so its regional populations are cut from a small fraction of
where it really lives.

Measured on run b69f51 at the present (the only frame with full presence, `presence_present`): of the cells where a whole
people (its groups counted in) has presence >= 12% (history EST), demes sees it (it leads the cell by ground or by heads,
or is second by heads with >= 10%) in 69% overall, but orcs 9% (1,226 of 14,131 cells), tortles 3%, deep folk 3%,
leonin 22%, dragonborn 37%, aarakocra 38%, dwarves 43% (66 of 155); humans 100%, halflings 98%, cervid folk 96%.

Cheap fix (not done: history files belong to the lane changing the history engine): in the frame store, add one layer
`peoples_present` of uint64 bit flags, bit k = whole people k has presence >= EST in the cell (the same shape and cost
as `crop_known`: 8 bytes a cell a frame, ~315 MB raw at L7 over 240 frames, mostly zeros so it gzips well; or only the
frames <= 300 kyr that demes cuts, ~170 MB). Up to 64 whole peoples fit (b69f51 has ~38). demes.occupied then reads the
bit instead of lead/second.
- [ ] `peoples_present` stored per frame (history/frame.py, output.PEOPLE_LAYERS)
- [ ] demes.occupied uses it when present; the caveat table above re-measured (target: every people >= 90% seen)
