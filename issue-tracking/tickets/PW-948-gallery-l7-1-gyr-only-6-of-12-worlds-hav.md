---
id: PW-948
title: "Gallery L7 1 Gyr: only 6 of 12 worlds have a good finish moment (2 of 4 stock seeds fail temperature)"
type: task
status: needs-decision
parent: null
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-866]
refs: [docs/review/gallery/gallery.md, "run a2bd9c", "run f46f51", "run 85f322", "run 69536e", "run 0f316f", "run 54da15"]
created: 2026-10-28
updated: 2026-10-28
---

## Description
The 12-world L7 gallery (docs/review/gallery/gallery.md, 1000 Myr, seeds 201-222) found a habitable finish moment in only 6 of 12, against the L6 rate of about 80% and the earlier L7 7/8. The fails are stock-1 (a2bd9c) and stock-2 (f46f51), 16-plate (85f322), drier (69536e) and both edges (0f316f, 54da15). All fail temperature, and three also fail land ice, so they lean cold. Running them through fmtally needs diag dirs; check whether the gallery runs recorded them.
- [ ] Measure true mean T and land ice at the end for the 6 fails. Icebox or just outside -6..+3 C?
- [ ] Decide whether L7 needs its own pass-rate set (two rolls) before tagging v1.

## Updates
- 2026-10-29: Lane 24: at L6 the warm lean is chaos-sized. A near-null change moved 15 of 36 paired draws and the median end T by +-0.8 C (draft-paired-judge-chaos-floor.md). The one systematic warm push found is the sink reference learnt from a high spin-up erosion supply (PW-980). Weighed against that floor, a 61% L7 rate over 28 draws is not clearly below the ~70% bar.
- 2026-10-28: Status in-progress -> needs-decision. Final main-only L7 1 Gyr: gallery 6/12, re-roll a 8/12, roll b 3/4 = 17/28 (61%), icebox 2/16 in re-rolls, no hellhouse; L6 18/24 (75%). No L7-specific mechanism found; L7 end-T spread wider (sd 4.2 vs 2.85), fails lean warm. Owner: is ~60% at L7 acceptable for v1, or measure with a 3-roll L7 set and look at the warm tail?
- 2026-10-28: Status todo -> in-progress. Lane 20: no L7-specific cause found. 5 of 6 fails are too WARM (+3.7..+6.5 C), only 54da15 cold. Ice-albedo matches L6; same seeds re-rolled at L7 swing by up to 7 C. Main-only pooled: L6 18/24, L7 12/20 so far (p~0.3). 8 more L7 sims finishing in scratchpad l20.
- 2026-10-28: Created from inbox draft draft-gallery-l7-finish-rate.md (found by coordinator).
