---
id: PW-067
title: "Zoom: big rivers less deeply incised; canyons shallower since falls"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: falls
blocked_by: []
relates: [PW-079]
refs: [planet/zoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Since `falls`, big zoom rivers keep at least their valley floor, so they are less deeply incised and
canyons are shallower than before. Check a canyon zoom and restore incision where the coarse world has a
gorge.

## Updates
- 2026-10-14: Status todo -> done. zoomsmalls: canyons are deeper again, from no longer letting creep fill stream beds (the valley floors were not the cause: dropping them off falls reaches changed canyon depth < 1%). Median river-to-rim depth on 4 canyon highlights (500 km @ 1 km) vs main: 04e7a7 1386 -> 1392 m (glaciated), 779b14 912 -> 1097, 382d62 1280 -> 1358, ae28af 866 -> 1183; big-river valley depth median over 20 zooms 66 -> 85 m.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Highlights (falls).
