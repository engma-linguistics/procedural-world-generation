---
id: PW-522
title: Carved falls (tiers, gorge, basins) are only drawn at the base zoom's pixel scale; fine zooms need the same form at 25-50 m
type: task
status: todo
parent: null
milestone: v1
subsystem: zoom
effort: m
impact: med
found_by: pw517
blocked_by: []
relates: [PW-517, PW-516, PW-399]
refs: [planet/zoom_falls.py, planet/zoom_fine.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
PW-517 added `planet/zoom_falls.py`: in the base zoom (1-4 km/px) a steep run of a river is redrawn as
tiers with ledges, a gorge retreated into the plateau, cone walls (no jutting platform) and a plunge
basin under each tier. At 1 km/px a tier is still one or two pixels, so a horseshoe lip, an
amphitheatre and a ledged face cannot show; they need the fine zoom (zoom_fine, `gorge_path`,
GORGE_WALL_DEG), which keeps the parent's drop and draws the gorge but not the tiers.
- [ ] fine zoom splits each parent fall's drop over the parent's tiers (the base zoom now lists them in `stats.falls[].cascades`)
- [ ] horseshoe lip: lip pixels recessed at the river, flanks held downstream, from the retreat of a notch (Niagara, Kaieteur)
- [ ] amphitheatre round the plunge basin, ledges in the face from strata (Angel, Gocta)

## Updates
- 2026-10-21: Created from inbox draft draft-fall-carving-fine-zoom.md (found by pw517).
