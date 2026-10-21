---
title: Zoom moraine ridges dam no lakes, and kettles and eskers are barely drawn
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: med
found_by: pw092
blocked_by: []
relates: [PW-092, PW-497]
refs: [planet/zoom_glacial.py, "zoom 21703a", "zoom 66c45e"]
---

## Description
PW-092's glacial class draws moraine belts (Baltic zoom 21703a: 4 belts at the 0.5 / 0.85 margin contours) and marks the moraine zone as `basins()` / `lakes()`, but the stats say `moraine_lakes` = 0 on every showcase zoom: the ridges are 3-6 px wide and 6-80 m high, the sills `cut()` removes them across flow paths wherever q >= the through-flow threshold, and `basin_lakes` needs LF_LAKE_M = 5 m of depth behind them. Kettle ponds: 0-3 per zoom (pits only count below the water table by 3 m). Eskers (sinuous ridges along subglacial channels) are not drawn.
What to try: raise moraine dams across valleys to a height that survives (a continuous ridge across a trunk valley, ridge height >= 15 m there), keep them out of `cut()` where the stream is under BASIN_THROUGH_Q, make kettles deeper on outwash, and draw eskers along the ice-ward flow paths of the outwash source.
- [ ] Baltic zoom: >= 3 moraine-dammed lakes; kettle ponds on the outwash plains
