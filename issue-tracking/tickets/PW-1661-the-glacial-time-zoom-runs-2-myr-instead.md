---
id: PW-1661
title: The glacial time zoom runs 2 Myr instead of 1 Myr for v1.0
type: task
status: in-progress
parent: null
milestone: v1.0
subsystem: timezoom
effort: m
impact: high
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-11-10
updated: 2026-11-10
---

## Description
Daniel (2026-11-10): v1.0 runs are 2 Myr instead of 1 Myr. In plain words: the glacial time zoom covers about 1 Myr of ice ages in 500-year steps today (planet/timezoom/__init__.py, README, docs/overview.md), and the peoples' deep history runs over the time zoom's frames, so a 2 Myr zoom gives the peoples twice the deep time. If never done: v1.0 worlds have half the deep history Daniel asked for.
- [ ] default span 2 Myr (CLI, make jobs, viewer start screen), docs updated
- [ ] cost measured at L7 (time zoom ~30 min per Myr; peoples history on the longer frames); the split pipeline (L7 deep history, L8 settled window) still fits the machine
- [ ] peoples presets' deep dates still sensible on 2 Myr (dnd, seven_meals, humans)

## Updates
- 2026-11-10: Status todo -> in-progress. Lane 280 merged (80f46bf8/5519d730): 2 Myr default everywhere, costs in docs/review/timezoom/two-myr.md. Left: the L8 split measurement on the refined 2 Myr world (chain running in /data/personal/scratch/lane280).
- 2026-11-10: Created.
