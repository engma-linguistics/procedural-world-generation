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
