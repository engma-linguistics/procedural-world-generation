---
id: PW-1673
title: "Level-of-detail flow in the viewer: click the globe, fly down into a 4,000 km section, double-click down the rungs to 25 m, fly back out"
type: story
status: done
parent: PW-1198
milestone: v1.0
subsystem: viewer
effort: l
impact: high
found_by: lane282
blocked_by: []
relates: [PW-1198, PW-1299, PW-1341, PW-1360, PW-129, PW-393]
refs: [docs/review/zoom/lod-plan.md, "viewer/globe/tabs.js::showTab", "viewer/globe/tabs.js::buildZoomOutlines", "viewer/globe/zoom.js::startZoom", viewer/globe/scene.js, "viewer/zoom.html::fetchZoom", viewer/zoom3d.js, viewer/zoom3d_place.js, viewer/navigator.js, planet/zoom/tiling.py, "world dba204", tools/viewer_perf.py]
created: 2026-11-10
updated: 2026-11-11
---

## Description
**In plain words.** Owner 11-10, required for v1.0: from the globe, zoom into a ~4,000 km section, then down to the
finest zooms we make. Today the globe offers only 250-2,000 km zooms at 500 px, a zoom opens in a separate tab with no
camera continuity, and going down a level means finding the "Fine zoom here" button. If this is never done, the v1.0
requirement is not met. Plan: `docs/review/zoom/lod-plan.md` (steps 3, 4 and 5).

Depends on the lane-282 drafts for sections in the API (section builds by cell, sections listing) and for the rung
chain (rung sizes); start step A once the API draft is merged.

**A. Globe to section and back (~1.5 lane-days).** The globe draws the world's tiling cells (built / not built, from the
sections listing); a click flies the camera down to the cell holding that spot, builds the section if needed (progress
on screen), and hands over to the section's 3D view at a matching camera (`zoom.html` already takes `view=3d&cam=`),
cross-fading rather than cutting (colours differ between globe palettes and the satellite view). Zooming out past the
section's farthest distance flies back to the globe.
- [ ] globe -> section -> globe on a showcase world with no page reload and no visible camera jump (screen recording)

**B. Down the rungs (~1-1.5 lane-days; after A and the rung-chain draft).** In a section, double-click flies to the spot
and opens the rung covering it (section 2 km -> ~500 km at 0.5 km -> ~30 km at 25 m), building it if needed, drawn
inset as nested fine tiles are today; a breadcrumb (Globe > section > 500 km > 30 km) climbs out; children's 2D
outlines drawn turned in a turned section (PW-1341's viewer half).
- [ ] three clicks from the globe reach a 25 m tile; the breadcrumb or zooming out climbs back to the globe

**C. Memory (~1 day, parallel with A).** `zoom.html::fetchZoom` decodes all ~71 layers up front (~0.63 GB for a 2 km
section, ~2.5 GB at 1 km: estimates from the zooms' layer specs). Load the drawn layers first and the rest on demand;
free a rung's buffers when leaving it.
- [ ] globe + 2 km section + both rungs under ~1.5 GB renderer memory (target; confirm on first measurement)

## Updates
- 2026-11-11: Status todo -> done. merged (lanes 304/306)
- 2026-11-10: Coordinator rulings on lod-plan-v2 questions (11-10 night): Q1 level 1 = 4 km/px (under 2 min on demand; follows the owner's everything-on-demand ruling, and level 2 at 1 km arrives seconds after; D78's 2 km lean was under the old section plan). Q2 = match new big squares to built neighbours for 1.0, river-water fix after the tag. Q3 (the cut) only if late; asked then. Steps 1 (PW-1689) and 4 (PW-1688) start now in parallel.
- 2026-11-10: Status needs-decision -> todo. Owner 11-10 (D78/D79 + chat): Google Earth, not sections. Scroll-zoom the globe continuously; below some height, detail tiles replace cells for what's on screen and sharpen further as you go down. No fixed-section clicks, no double-click rungs. Everything on demand: nothing pre-built; an area shows the blurry globe until its tile builds, then sharpens and is kept. Re-plan: lane 289.
- 2026-11-10: Lane 289: owner 11-10 ruling (Google-Earth scroll zoom, everything on demand) supersedes this ticket's click/double-click flow. New plan: docs/review/zoom/lod-plan-v2.md (tile pyramid per tiling cell: 4 km section, then 500 px tiles at 1 km / 250 m / 25 m on one lattice per level; on-demand queue; globe draws tiles). Measured: 4 km section 100 s / 5.7 GB; 500 px fine tiles 13-17 s / ~3.5 GB. planet/zoom/lod.py (tile addressing) added. Steps as inbox drafts draft-lod2-*; questions Q1-Q3 in the plan.
- 2026-11-10: Status todo -> needs-decision. Desk D78 (section sharpness, lean 2 km/px) and D79 (fixed sections vs centred, lean fixed). PW-1674/1675 proceed meanwhile: the API takes res_km as a parameter.
- 2026-11-10: Created from inbox draft draft-lod-1-viewer-globe-to-finest.md (found by lane282).
