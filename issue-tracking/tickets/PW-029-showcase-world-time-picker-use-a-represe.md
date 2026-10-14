---
id: PW-029
title: "Showcase world-time picker: use a representative moment, not the most dispersed"
type: task
status: done
parent: null
subsystem: highlights
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: [planet/__main__.py, planet/highlights.py, docs/coordination.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The overnight post-processing picked each showcase world at the run's "most dispersed" moment, which
biased worlds toward the most fragmented snapshot. Use a neutral or representative time instead (e.g.
land fraction and landmass count near the run's median after 300 Myr). The tool was a temp script, so
make it a proper `planet` option (e.g. `planet slice <run> --at representative`, or in `planet
highlights`) or a documented rule in `docs/coordination.md`.

## Updates
- 2026-10-14: Status in-progress -> done. Added highlights.representative_time(frames): after 300 Myr (last two thirds for shorter runs) the keyframe whose land %, largest landmass % and log landmass count are jointly nearest their medians, in IQR units (from run.json frame stats, no layers loaded). 'planet slice <run> --at auto' and 'planet highlights <run> --at auto' use it and print the pick. On the 20 runs here it lands within ~1 point of every median (e.g. 19385e -> 396 Myr, 796a25 -> 692, fe7144 -> 580). Documented in README, coordination.md showcase recipes and the highlights docstring; tests in test_highlights. The existing showcase worlds were not re-sliced.
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Created from the owner discussion 2026-10-14.
