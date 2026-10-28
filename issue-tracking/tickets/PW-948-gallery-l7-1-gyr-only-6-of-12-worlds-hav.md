---
id: PW-948
title: "Gallery L7 1 Gyr: only 6 of 12 worlds have a good finish moment (2 of 4 stock seeds fail temperature)"
type: task
status: in-progress
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
- 2026-10-28: Status todo -> in-progress. Lane 20: no L7-specific cause found. 5 of 6 fails are too WARM (+3.7..+6.5 C), only 54da15 cold. Ice-albedo matches L6; same seeds re-rolled at L7 swing by up to 7 C. Main-only pooled: L6 18/24, L7 12/20 so far (p~0.3). 8 more L7 sims finishing in scratchpad l20.
- 2026-10-28: Created from inbox draft draft-gallery-l7-finish-rate.md (found by coordinator).
