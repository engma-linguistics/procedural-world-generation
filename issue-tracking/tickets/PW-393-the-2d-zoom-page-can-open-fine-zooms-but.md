---
id: PW-393
title: The 2D zoom page can open fine zooms but can't ask for one
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: med
found_by: pw129-fine-zoom
blocked_by: []
relates: [PW-129, PW-072]
refs: [viewer/zoom.html, planet/api.py, planet/zoom_fine.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Fine zooms (planet/zoom_fine.py, PW-129) are ordinary zoom folders, so
viewer/zoom.html?id=<fine id> opens them unchanged. The server takes
`POST /api/zoom {zoom: <parent id>, lat, lon[, size_km, res_km]}`. Without a
size, it defaults from the parent's resolution: 50 km at 100 m in a regional
zoom, 25 km at 50 m in a fine zoom. Requests more than 20x finer than the
parent, or that don't fit inside it, get a 400 with the reason.
zooms/index.json lists `parent_zoom` on a fine zoom and `children` on its
parent.

Missing in the 2D page:
- a "fine zoom here" pick: 50 km / 25 km / 25 km at 1000 px, with picks too
  close to the parent's edge greyed out;
- the children's rectangles drawn on the parent (`parent_zoom.rect_px` in the
  child's zoom.json gives its place in parent pixels);
- a link from a child back to its parent.

The 3D inset is the separate 3D-tile work.

## Updates
- 2026-10-16: Status todo -> done. Shipped (f3fc8cd, cb3c8a6, 1093058); follow-ups PW-391/392/399-405.
- 2026-10-16: Created from inbox draft draft-fine-zoom-viewer-pick.md (found by pw129-fine-zoom).
