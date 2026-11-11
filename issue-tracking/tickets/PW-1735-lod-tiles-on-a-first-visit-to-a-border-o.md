---
id: PW-1735
title: "LOD tiles: on a first visit to a border or corner, the cells' level 1 are built one after another, so half the screen stays globe hexagons for minutes"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: m
impact: med
found_by: lane306
blocked_by: []
relates: [PW-1690, PW-1699]
refs: [planet/tiles.py, "planet/zoom/lod_build.py::build_level1", docs/review/zoom/lod-judge-306.md, docs/review/zoom/lod-judge-306/border_08_1km_tilted.png, docs/review/zoom/lod-judge-306/corner_10_250m_south_cells_waiting.png]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** Lane 306 dived onto the line between two big squares with nothing built (own server, 4 jobs x 2
threads). The first square's level 1 was drawn 334 s after the stop; the second's only after it (one level-1 build per
world at a time, the later one matched to the earlier), so through the 1 km and 250 m levels half the screen was flat
globe hexagons beside sharp mountains (`border_08`). At a corner of four squares the cold ones wait in turn as well
(`corner_10`). With 4-6 min a level 1 on a shared machine, a corner can take ~20 min to fill in.

Options to weigh (not decided): build level 1 with all the threads the server has while it is the only build; start the
level-2 tiles of the first cell meanwhile (they don't wait for the neighbour's level 1 unless they touch the line); show
the neighbour's level 1 unmatched as a stand-in until the matched one is in; or keep the order and show the parent
cells' colours smoothly instead of hexagons.

**Done when.** On a cold dba204 border dive (`tools/viewer_lod_dive.py --wait`) both cells show level-1 detail within
the time of one level-1 build plus a minute, and the line still meets at the floor (`line_seam` against `resampled`).

## Updates
- 2026-11-11: Created from inbox draft draft-lod-cold-border-waits-for-level1-in-turn.md (found by lane306).
