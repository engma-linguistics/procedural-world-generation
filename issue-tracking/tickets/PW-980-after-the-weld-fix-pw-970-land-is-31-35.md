---
id: PW-980
title: After the weld fix (PW-970) land is 31 -> 35% of the surface and finish moments run ~0.9 C warmer
type: task
status: todo
parent: null
milestone: v1
subsystem: tectonics
effort: m
impact: med
found_by: lane23
blocked_by: []
relates: [PW-970, PW-950, PW-293, PW-865]
refs: [planet/tectonics/crust.py, docs/review/tectonics/crust/crust.md]
created: 2026-10-28
updated: 2026-10-30
---

## Description
Lane 23's coherence fix (a607c614) takes thin welded margin crust out. In the paired L6 1 Gyr set (36 draws
each, 600-1000 Myr means, median over draws), continental crust goes 32.6 -> 34.2 km and continental area
41.8 -> 41.3%. But land goes 31.3 -> 34.8% (Earth 29). Drowned continent falls from ~10.5% to ~6.5% of the
surface (Earth ~12). Its median depth is -1519 -> -819 m, so less continent lies under the sea.

The pass rate went 31/36 -> 28/36 (both pass 25, main only 6, branch only 3). All 6 lost draws were too warm
at the finish moment (+4.8 to +11.1 C). The median end temperature is +0.85 against -0.05 C.

Not looked into: why more land runs warmer here, and whether the sea level's own steady ocean (PW-293,
SEA_TECT_MAX ~400 m) should now sit higher with less ocean basin taken by drowned margins. Candidates: the
weathering balance's land/area terms (PW-865's end-anchored GEOCARB frame), the land albedo/ice terms, and
sea level.
- [ ] find what warms the branch's finish moments (one warm draw, e.g. seed 639472 r0.001 l6fix: +11.1 C
  against main's -3.6 C, traced through ice_diag's CO2 source/sink and albedo terms)
- [ ] land back within ~29-33% at L6 without thinning the crust again

## Updates
- 2026-10-30: Lane 28b: warm-finish half looks obsolete (median end T -0.25/+1.44/-0.20 C on 3a58e00d/F/coasts, no warm shift); land-share half open (34.6-34.9% at L6 vs 29-33% target).
- 2026-10-29: Merged lane 24 10-29: the warm shift is erosion against the frozen sink reference (spin-up erodes ~20% more than late), mostly inside the judge's chaos band (PW-994). Water conservation for the continents' sea merged (null at L6). Open: why the spin-up erodes more after the weld fix; land back toward 29-33%.
- 2026-10-29: Lane 24 (docs/review/base-climate/warm-drift/README.md). The diagnosis is the carbon cycle through the erosion supply, against the sink reference frozen at REF_FREEZE. It is not land area, land albedo, land heat or PW-880. Paired over 18 draws (pre-weld 3f43093d against main, roll 0.001), main's 250-300 Myr erosion supply is ln +0.22 higher, so its sink reference is +0.11. Its late supply is -0.08 and its late source -0.09 raw, which gives late CO2 +0.22 e-folds and dT +0.8 C (median of the paired differences). Land does not weather in the model except through erosion, and the new land is low. The climate's own land effect is the other way: -0.25 C true mean for +3.5 points at fixed dT. The weld fix's land rise is systematic (+4 points, and +1.5 of it at 300-400 Myr). The pass loss is not: a near-null change flips 15 of 36 draws, +-3 passes and +-0.8 C median end T (draft-paired-judge-chaos-floor.md). Water conservation for the continents' sea (earth.continent_water) is added. It is a correct mechanism but measures null at L6 (+-20 m, land 34.80 -> 34.84%), so it doesn't bring land back. Still open: why main's spin-up erodes ~20% more than its late run (pre-weld: flat), and land back to 29-33% (shelves, PW-950 v2). Option for the area question: draft-weathering-land-area-term.md.
- 2026-10-28: Created from inbox draft draft-thicker-continents-more-land-warmer.md (found by lane23).
