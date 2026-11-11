---
id: PW-1699
title: "LOD globe step 3: a cell's level 1 built on demand is matched to its built neighbours"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-1690, PW-1689, PW-1355]
refs: [docs/review/zoom/lod-plan-v2.md, planet/zoom/match.py, planet/zoom/lod_build.py]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** Each 4,000 km square's first detail level (4 km/px) is made on its own, so two neighbouring squares
can disagree by tens of metres on plains and hundreds in mountains where they meet. This makes a square built later fit
the ones already built, exactly at the shared edge, so scrolling across a square's border shows no step.

Plan step 3 (`lod-plan-v2.md` §2.3, §5): level 1 of a cell is built matched (`match.py`) to whichever neighbours are
already built, inside `lod_build.tile`, so the tile service (PW-1690) gets it without changes.
- [ ] two neighbours built in either order meet at the cell edge within a few metres at the line, rivers carried
- [ ] their level-2 tiles at the line agree the same way
- [ ] time and peak for a matched level 1 measured against unmatched

## Updates
- 2026-11-11: Created from inbox draft draft-lod-level1-matched.md (found by coordinator).
