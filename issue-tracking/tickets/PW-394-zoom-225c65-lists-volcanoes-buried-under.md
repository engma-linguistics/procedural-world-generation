---
id: PW-394
title: Zoom 225c65 lists volcanoes buried under a higher plateau
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: s
impact: low
found_by: pw129-fine-zoom
blocked_by: []
relates: []
refs: [planet/zoom_volcanoes.py, "zoom 225c65"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Zoom 225c65 (1 km/px, centred -17.0, 119.4) lists several active
stratovolcanoes with top_m 3476 m: at -16.83, 119.956, at -16.757, 118.636,
and others. The terrain there stands ~6000-8700 m (fine zoom mean 6351 m), so
each cone (drawn as max(cone, terrain)) is invisible: the volcano's summit
lies 2.5 km below the ground. Either the run's volcano heights don't follow
the uplift of the plateau they sit on, or the zoom shouldn't list a volcano
whose top_m is below the ground it stands on.

Found while choosing a volcano for a PW-129 fine-zoom showcase. zoom_fine
skips such a volcano: its cone never drops below the summit, so no core
radius is found and it doesn't fit.
- [ ] a listed volcano's summit is at or above the zoom's ground there

## Updates
- 2026-10-16: Created from inbox draft draft-zoom-volcanoes-buried-under-plateau.md (found by pw129-fine-zoom).
