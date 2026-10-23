---
id: PW-621
title: "Zoom coast forms still missing: spits by longshore drift, beach ridges, tidal channel networks, cliffs as terrain, drowned reefs"
type: task
status: todo
parent: PW-097
milestone: v2
subsystem: coast
effort: l
impact: med
found_by: coast-detail
blocked_by: []
relates: [PW-097, PW-326, PW-004]
refs: [planet/zoom_coast.py, docs/proposals/coast_detail.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Stage 2 of docs/proposals/coast_detail.md drew shore classes, barrier islands with inlets, colonies and
hazards in zooms. Still not drawn:
- spits and recurved hooks at headlands and inlets, deflected by the longshore drift (the wave direction from
  coast.py's rays relative to the shore normal);
- beach ridges / strandplains on prograding wave coasts (delta flanks, zoom preview);
- dendritic tidal channels on macrotidal flats (noise-based now in the delta code);
- cliffs as terrain: a steep step at the shore where the class is cliffs (now only the class);
- drowned reefs and raised reef terraces from the time zoom's sea-level history (meta sea_level_change_m per
  frame): lowstand reefs now 60-120 m deep (shelf-edge hazards), terraces on uplifting arcs.
Also observed in zoom ccf03a: the shore band also follows estuary channels that the zoom marks as sea, so
beach/rocky classes run up tidal rivers; harmless but noisy.
- [ ] spits at inlets and headlands oriented by drift
- [ ] cliff step in the terrain (opt-in like barrier islands)
- [ ] drowned-reef layer from a time zoom's sea-level curve

## Updates
- 2026-10-23: Created from inbox draft draft-coast-zoom-forms-remaining.md (found by coast-detail).
