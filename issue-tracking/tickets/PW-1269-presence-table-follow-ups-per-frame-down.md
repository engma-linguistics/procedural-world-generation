---
id: PW-1269
title: "Presence table follow-ups: per-frame download for the picker, a minority's learned country, the brief's people range"
type: task
status: done
parent: PW-670
milestone: null
subsystem: timezoom
effort: m
impact: low
found_by: lane109
blocked_by: []
relates: [PW-1259, PW-1155, PW-981, PW-670]
refs: [viewer/globe/colours.js, planet/lineages/demes.py, planet/lineages/brief.py, planet/lineages/history/frame.py]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: the overlapping demes work, but three loose ends remain.

1. **Download size in the viewer.** The "whose demes" picker fetches the whole presence table and demes_all at once: about
   25 MB at L6 and 155 MB at L7 (measured: a dnd run of 169 frames, 22 M entries; the table 111 MB plus demes_all 44 MB, 12%
   of the 1.3 GB run; a 240-frame Seven Meals run would be about 1.5x that). Fetch one frame's slice instead (HTTP Range on
   presence_cells.bin and demes_all.bin from the offsets, or a small /api endpoint). On disk, the uint32 cell ids at L7 could
   be stored as uint16 deltas within each line's run (cells ascend) to cut the table by about a third.
2. **A minority's learned country.** `peoples_learned` is the leading people's learning only. Lane 109 made the demes read
   it only where the people leads (before, a dragon living over humans' learned farmland split off "adapted" demes from the
   humans' learning: 34 of the gold dragons' 53 demes). So a people that never leads a cell can never split off an adapted
   deme. Store the learned acceptance per entry of the presence table (one more uint8 an entry) if that matters.
3. **The brief's people range.** `planet brief --people X` takes the cells where X leads or comes second. With the presence
   table it could take every cell where X lives (dragons and giants would get their real range).

## Updates
- 2026-11-01: Status todo -> done. Lane 111: picker fetches one frame (/api/presence, ~0.74 MB raw / 0.22 MB gzip per frame change at L7 vs 124 MB); brief --people reads every cell from the presence table. Item 2 measured only (needs-decision ticket); cell-id shrink deferred to the next re-cut.
- 2026-11-01: Created from inbox draft draft-presence-table-follow-ups.md (found by lane109).
