---
id: PW-1299
title: "Whole-planet land zoom at 4000 km sections: practice seams on chosen neighbours, then sweep every land region"
type: epic
status: todo
parent: null
milestone: v1.0
subsystem: zoom
effort: xl
impact: high
found_by: owner
blocked_by: []
relates: [PW-1198, PW-541]
refs: ["planet/zoom/regional.py::zoom", docs/review/gpu/profile.md]
created: 2026-11-02
updated: 2026-11-10
---

## Description
**In plain words.** Daniel 11-02: cover all of a world's land with the regional zoom at its largest (4000 km sections, up to 4096 px across, ~1 km/px), seamless, rivers continuous, viewed through PW-1198's level-of-detail globe. Steps, in order: (1) pick meaningful side-by-side practice sections and measure the seams; (2) seams agree; (3) rivers and lakes continuous across sections; (4) memory, timing and storage per section; (5) last: the planet-wide sweep (PW-1296). Each step is judged in the viewer on the practice sections before the next.

## Updates
- 2026-11-10: Lane 282: the owner's v1.0 flow opens one tiling section at a time (docs/review/zoom/lod-plan.md); it needs sections by cell in the API and a RAM guard, not matched seams. Suggest the sweep pieces (PW-1296, PW-1355) go back to later unless side-by-side sections are wanted for 1.0.
- 2026-11-10: Owner 11-10: required for v1.0 (milestone v1.0): from the globe, zoom into a ~4,000 km section, then down to the finest zooms we have.
- 2026-11-03: Milestones 11-03: v2 -> later: owner 11-03: no whole-planet fine map is fine; the L7->L9 refine of the chosen world is v5
- 2026-11-02: Created.
