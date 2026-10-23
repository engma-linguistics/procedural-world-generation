---
id: PW-610
title: "Resources stage 2: site concrete deposits (points, seams, placers) in regional zooms"
type: task
status: todo
parent: PW-155
milestone: v2
subsystem: zoom
effort: l
impact: med
found_by: resources
blocked_by: []
relates: [PW-155]
refs: [planet/resources.py, planet/zoom.py, viewer/zoom.html, docs/proposals/resources.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Stage 1 gives each world cell a likelihood per resource (res_* layers). Stage 2 (design in
docs/proposals/resources.md section 6): in each regional zoom, inherit the likelihoods to pixels, then site
deposits deterministically (Poisson draw per resource, seeded by zoom id) on pixels that fit the model:
porphyry on arc volcano flanks and eroded roots, orogenic gold on fold-belt ridges, Sn-W on granite, placers
on river pixels where the gradient drops and on wave-exposed beaches, coal/salt outcrops where the zoom's
strata dip brings the bed up (cuesta scarps), oil/gas on anticline crests (fold wavelength), kimberlite
fields as clusters. Each deposit: type, grade (lognormal per model), tonnage class, depth. Store as a zoom
table, draw as markers with a legend and hover in zoom.html; add to export features.
- [ ] zoom_resources.py with per-model siting rules; deterministic per zoom
- [ ] zoom.html markers, legend, hover; export features
- [ ] screenshots on a porphyry arc, a coal basin and a placer river

## Updates
- 2026-10-23: Created from inbox draft draft-resources-zoom-siting.md (found by resources).
- 2026-10-23: Built (lane resources2): planet/zoom_resources.py, `planet resources zoom:<id>` (zoom.json
  `resources`: deposits with type, size, tonnage, grade, depth, host; coal outcrop belts; summary), zoom.html
  markers/legend/cards/filter and an about row, export `deposit` features. Siting reads a world likelihood p as
  P(notable deposit in cell), so world districts show up (~90% of district cells at p = 0.5 in the checks).
  Seams: coal measures cut by the zoom's terrain; placers: the zoom's own drainage and gradient (valley_floor
  in fine zooms). Also bauxite by mechanism (uninterrupted weathering runs) and a partial coal-speckle fix in
  resources.py. Write-up and screenshots (arc, coal basin, placer river): docs/review/resources/stage2.md.
  Follow-ups in the inbox (draft-resources-*: snw-granite-spread, coal-speckle-residual,
  zoom-deposits-auto-and-3d, zoom-bed-geometry).
