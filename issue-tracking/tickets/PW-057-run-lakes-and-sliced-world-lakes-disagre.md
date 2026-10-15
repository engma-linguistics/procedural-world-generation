---
id: PW-057
title: Run lakes and sliced-world lakes disagree
type: task
status: done
parent: null
subsystem: hydrology
effort: m
impact: low
found_by: lakes
blocked_by: []
relates: []
refs: [planet/world.py, planet/timeline.py, "run 8dc2f2", "world 1c98e7", planet/hydrology.py, "run ee65aa", "run 01b0f7"]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Closed lakes on flat basins disagree a lot between a run frame and the world sliced at the same time
(t=180 in demo run 8dc2f2: 1 shared wet cell of 88 vs 18), because the world adds ±180 m texture, its own
erosion and a fresh climate. Open lakes agree roughly; the world's are smaller and about half as deep.

## Updates
- 2026-10-15: Status in-progress -> done. Merged (hydro2).
- 2026-10-15: Status todo -> in-progress. Worktree hydro2.
- 2026-10-15: Coordinator decision (north star): option B. Relief-scaled world texture (plains flat, mountains rough) and one-sided creep in hydrology.erode (lowers ground only, as the run's hillslope), then re-measure lake agreement. C rejected as a mask rather than a process.
- 2026-10-15: Merged inbox draft draft-world-lakes-vs-run-lakes.md ("PW-057 options: the world's texture and its 12 erosion passes, not the climate, move the lakes away from the run's", found by hydro).
  Measured for PW-057 (hydro branch): lakes computed with the *same* climate on the run's keyframe
  elevation vs on what world finishing makes of it (timeline._world texture, then hydrology.erode, 12
  passes at strength 0.3). Jaccard overlap of lake cells with the keyframe's (run ee65aa @ 632 / 01b0f7 @ 976, L6):
  - texture only: 0.21 / 0.30 (texture makes new hollows: 4 -> 19, 21 -> 57 lake cells, many closed)
  - texture + erosion (today): 0.25 / 0.05; erosion alone on the keyframe: 0.50 / 0.10 (21 -> 2 lake cells:
    the 12 passes cut every outlet and the symmetric creep fills the hollows)
  - texture scaled with local relief (x clip(relief / 150 m, 0.15, 1): plains flat, mountains rough) +
    erosion whose creep only lowers ground (as the run's hillslope): 0.25 / 0.32
  Existing worlds agree with their keyframes on almost no lake cell (c73271, 8e71fd, 7c5adf: Jaccard 0-0.02).
  Options:
  - A. Keep: a world is its own finish; the run's lakes are a coarse preview.
  - B. Relief-scaled texture + one-sided creep in hydrology.erode (above): about a third of the lake cells
    agree; flat lowlands lose their +-180 m bumps (changes how every world's plains look).
  - C. Keep the run's lake basins: no texture and no world erosion on the keyframe's lake cells and their
    rims, so the world's lakes are the run's (re-solved with the world's climate) plus whatever the texture
    adds elsewhere. Most consistent, but a mask rather than a process.
  Lean: B (plains really are flatter than mountains; the creep should not fill hollows), then re-measure.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Viewer / Earth world.
