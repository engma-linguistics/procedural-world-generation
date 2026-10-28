---
title: Zoom deltas don't know their load's grain size (cohesive mud vs sand sets elongate vs lobate)
type: task
status: todo
parent: PW-244
milestone: null
subsystem: zoom
effort: m
impact: low
found_by: physics-lane-21
blocked_by: []
relates: [PW-847]
refs: [planet/zoom.py, planet/coast.py, "zoom 91bf86 of world 2a7385", docs/review/zoom/pw847/]
---

## Description
Lane 21's PW-847 fix gives a zoom delta its fingers only where the river dominates (Galloway weights) and
runs out into water several channel depths deep (`zoom.BUOYANT_DEPTHS`, after Wright 1977's friction- vs
buoyancy-dominated outflow). Fingers are now short (0.12 R past the lobe front), at most four, and the lobe is
held as land.

The other control on delta shape is the load's calibre: cohesive, fine-grained loads build elongate deltas with
few stable channels and a rough shoreline; coarse, non-cohesive loads build a round fan with many channels and a
smooth front (Edmonds & Slingerland 2010, Nature Geoscience 3:105-109; Caldwell & Edmonds 2014, JGR Earth
Surface 119:961-982). The world has no grain-size field for a river's load (`coast.river_sediment` gives BQART
tonnes only), so the zoom can't tell a muddy lowland river from a sandy or gravelly mountain one.

What to try: a sand fraction of the load from the basin (relief and steepness, glacial share, perhaps the
weathering climate), checked against published bedload and suspended-sand shares. Then scale `FINGER_LEN` and the
lobe's rim scallops by it. Cite each source; any threshold that has none is judgement and should say so.
- [ ] a load-calibre estimate per delta, with its source
- [ ] the finger and lobe shapes scaled by it, with before/after zooms
