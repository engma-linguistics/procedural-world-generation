---
id: PW-1299
title: "Whole-planet land zoom at 4000 km sections: practice seams on chosen neighbours, then sweep every land region"
type: epic
status: todo
parent: null
milestone: v2
subsystem: zoom
effort: xl
impact: high
found_by: owner
blocked_by: []
relates: [PW-1198, PW-541]
refs: ["planet/zoom/regional.py::zoom", docs/review/gpu/profile.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** Daniel 11-02: cover all of a world's land with the regional zoom at its largest (4000 km sections, up to 4096 px across, ~1 km/px), seamless, rivers continuous, viewed through PW-1198's level-of-detail globe. Steps, in order: (1) pick meaningful side-by-side practice sections and measure the seams; (2) seams agree; (3) rivers and lakes continuous across sections; (4) memory, timing and storage per section; (5) last: the planet-wide sweep (PW-1296). Each step is judged in the viewer on the practice sections before the next.

## Updates
- 2026-11-02: Created.
