---
title: Picking a people in the panel does not dim the other peoples (peoplesColor lerps a colour with itself)
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: viewer
effort: xs
impact: low
found_by: perf679
blocked_by: []
relates: [PW-679]
refs: [viewer/index.html, "run 7bc9ed"]
---

## Description
In `peoplesColor` (viewer/index.html) the picked-people branch is `c.copy(NOBODY).lerp(c.set(lines[d].color), 0.15)`. The
argument `c.set(...)` runs after `c.copy(NOBODY)` and overwrites `c`, so `lerp` is `c` with itself and the other peoples
come out in their full colour; the panel says "click one to show only its range", but the others are not toned down.
The `peoples overlay` branch has the same shape (`c.copy(NOBODY).lerp(c.set(...), 0.25)`: meant as a 25% blend of the
leading people over grey where there is no overlay). PW-679 kept the output exactly as it was (it only cached the Color
objects) and left a comment in both places.
Fix: lerp from NOBODY towards a separate Color (`lineColor(lines[d])`), then look at the picked view and the overlay
layer on 7bc9ed to see that the intended dim reads well; it changes those two views' look, so it needs a glance from Daniel.
- [ ] picking a people dims the rest (grey, 15% of their colour)
- [ ] the overlay layer shows the leading people at 25% where nothing overlays
