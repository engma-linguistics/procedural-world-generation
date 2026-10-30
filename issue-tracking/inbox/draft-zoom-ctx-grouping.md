---
title: The regional zoom's build context is one flat bag of 227 names; group it so each stage shows what it really needs
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: m
impact: low
found_by: refactor-lane-55
blocked_by: []
relates: []
refs: [planet/zoom/regional.py, planet/zoom/stage_terrain.py, planet/zoom/stage_rivers.py, planet/zoom/stage_landscape.py, planet/zoom/stage_finish.py]
---

## Description
In plain words. The regional zoom's build is now a list of 25 named steps, but they still pass their work to each other through one big shared box (`ZoomCtx`) that holds 227 separate names, so a step can still quietly depend on something a much earlier step left there. It works and gives bit-identical output, but the hidden coupling the code audit complained about is now written down (each step's docstring lists what it reads and writes) rather than removed.

Next step: look at those read/write lists and group the names that travel together into small named records (for example the pixel grid, the coarse cells, the delta set, the lake set, the drainage network, the climate fields), so a step takes only the records it needs. Some steps could then be tested alone. Done when the biggest "Reads:" lists (`crop_halo` 61 names, `stats` 71, `landscape_loop` 60) drop well under 20.
- [ ] grouped records replace the flat slots, with no change to the zoom's outputs (compare layers bit for bit on a few regions)
- [ ] the crop step crops one record instead of a 33-name tuple (audit F13)
