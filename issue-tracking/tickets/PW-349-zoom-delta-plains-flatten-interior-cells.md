---
id: PW-349
title: "Zoom: delta plains flatten interior cells up to 800 m high, ~25 m low cell means on river-mouth zooms"
type: task
status: done
parent: null
milestone: null
subsystem: zoom
effort: s
impact: low
found_by: zoom-batch3
blocked_by: []
relates: [PW-298, PW-061]
refs: [planet/zoom.py, docs/review/zoom-polish/pw298.md, "world:592f2a(4.97,-114.51)", "world:592f2a(1.96,-70.44)"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
After PW-298 the landscape pass keeps its target's cell means (inland bias -6..+2 m on 6 of the 8
showcase zooms of 592f2a), but two zooms stay ~25 m low inland: 4.97,-114.51 (1000 km @ 2 km, the largest
river: -25 / 54 m bias / RMS) and 1.96,-70.44 (500 km @ 1 km: -27 / 87 m). Stage by stage on 1.96,-70.44:
after the detail's 12 mean passes -2 / 28 m; after the delta plains are blended in (`if deltas:` right
after the mean passes, h = (1 - wD) h + wD (zD + det)) -23 / 73 m; the landscape pass then keeps that.
The delta plain's weight wD reaches cells whose ground is up to 800 m (hf = 1 - smoothstep(250, 800,
e_land)) over a radius R of up to ~300 km, interior cells included, and flattens them to a few metres
(zD) with no mean correction (wC damps the detail's correction there by design).

To try: keep the plain's cells' means by putting the lost volume back on the land just beyond the plain
(keep_means with f outside the plain), or limit the plain to the coarse cells that are lowland in the
world (a delta plain on 250-800 m coarse ground is the zoom inventing a lowland the world doesn't have).
Check the deltas' look (test_zoom_water's delta tests) and the inland bias on the two zooms.
- [ ] inland cell-mean bias within +-10 m on 4.97,-114.51 and 1.96,-70.44

## Updates
- 2026-10-16: Status in-progress -> done. Done: delta plain only on low coarse ground (full to 30 m, none above 250 m), the removed volume restored on the cell's land beyond. Inland bias -25..-27 -> ~0 m on the delta zooms.
- 2026-10-16: Status todo -> in-progress. Zoom batch 4 agent started.
- 2026-10-16: Created from inbox draft draft-zoom-delta-plain-cell-means.md (found by zoom-batch3).
