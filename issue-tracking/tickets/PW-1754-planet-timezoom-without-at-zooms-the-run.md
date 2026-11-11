---
id: PW-1754
title: planet timezoom without --at zooms the run's first moment (0 Myr), whose finished world is barren and crashes the peoples
type: task
status: todo
parent: null
milestone: null
subsystem: timezoom
effort: xs
impact: med
found_by: lane305
blocked_by: []
relates: []
refs: [planet/__main__.py, planet/lineages/ladder.py, "run 0760b3 (lane 305 scratch, deleted)"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** `planet timezoom <run>` defaults `--at` to 0.0 Myr: the zoom starts from the run's first keyframe, not its
end. Lane 305 zoomed a fresh L6 run (seed 250979, 1000 Myr) that way; the finished world at the interglacial had NPP 0, 55% hot
desert and 29% ice sheet (the run's own 1000 Myr world: NPP 470, forests and grassland), and `planet lineages` on its refine then
stopped with `KeyError: 'grazing'` in `ladder.Ladder.__init__` (land.goods leaves out a good the plants lack, the ladder
assumes it is there).

**What breaks if never done.** Anyone following the CLI help ("from one moment of a run") without `--at` gets a dead world and a
crash an hour later; the ladder crashes on any world without grazing.

**Do.** Default `--at` to the run's end (as `make` and the viewer do), and let the ladder read a missing good as zero.
- [ ] `planet timezoom <run>` with no --at starts at the run's last keyframe
- [ ] lineages on a world without grazing runs

## Updates
- 2026-11-11: Created from inbox draft draft-timezoom-default-at-zero.md (found by lane305).
