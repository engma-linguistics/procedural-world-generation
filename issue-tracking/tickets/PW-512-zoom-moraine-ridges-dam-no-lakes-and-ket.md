---
id: PW-512
title: Zoom moraine ridges dam no lakes, and kettles and eskers are barely drawn
type: task
status: todo
parent: null
milestone: v1
subsystem: zoom
effort: s
impact: med
found_by: pw092
blocked_by: []
relates: [PW-092, PW-497]
refs: [planet/zoom_glacial.py, "zoom 21703a", "zoom 66c45e"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
PW-092's glacial class draws moraine belts (Baltic zoom 21703a: 4 belts at the 0.5 / 0.85 margin contours) and marks the moraine zone as `basins()` / `lakes()`, but the stats say `moraine_lakes` = 0 on every showcase zoom: the ridges are 3-6 px wide and 6-80 m high, the sills `cut()` removes them across flow paths wherever q >= the through-flow threshold, and `basin_lakes` needs LF_LAKE_M = 5 m of depth behind them. Kettle ponds: 0-3 per zoom (pits only count below the water table by 3 m). Eskers (sinuous ridges along subglacial channels) are not drawn.
What to try: raise moraine dams across valleys to a height that survives (a continuous ridge across a trunk valley, ridge height >= 15 m there), keep them out of `cut()` where the stream is under BASIN_THROUGH_Q, make kettles deeper on outwash, and draw eskers along the ice-ward flow paths of the outwash source.
- [ ] Baltic zoom: >= 3 moraine-dammed lakes; kettle ponds on the outwash plains

## Updates
- 2026-10-21: Created from inbox draft draft-glacial-zoom-moraine-lakes.md (found by pw092).
- 2026-10-21: Built on branch worktree-agent-a6325323c9d1c4305: moraine dams across streams, lakes() open inside the margin, recessional belts at thickness contours, kettles to the water table, eskers. Baltic 34 moraine-dammed lakes (zoom 9213a8), Ungava 9 (a44e9f), Norway 12-13, Patagonia 8, Alps 3. Needs a merge.
