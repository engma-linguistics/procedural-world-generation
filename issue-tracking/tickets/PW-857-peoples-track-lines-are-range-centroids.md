---
id: PW-857
title: Peoples track lines are range centroids, so a multi-patch people's line wanders at sea and looks like a migration
type: task
status: done
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner saw a meandering pink line (likely the tabaxi, #ff69b4, 44 patches round the equator) in b69f51. viewer/index.html:1680-1726 draws meta.lineages[].track, the presence-weighted centroid per frame (history.py:1202-1209). Show a largest-patch or per-patch track, snap to land, or label it 'range centre'.

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 24 (de83743).
- 2026-10-25: fun-lane-24: peopleOverlays no longer draws the range-centre tracks (meta.lineages[].track stays in the data); the checkbox is relabelled 'Peoples' origins' (the origin rings stay).
- 2026-10-25: Owner: don't draw the range-centre track at all unless it's useful to us; remove the overlay.
- 2026-10-25: Created.
