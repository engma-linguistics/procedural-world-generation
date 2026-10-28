---
id: PW-950
title: Shelves stay ~1.5% of the ocean because the submerged continent sits ~1.5 km deep; try water-loaded isostasy
type: task
status: todo
parent: null
milestone: v1
subsystem: tectonics
effort: m
impact: med
found_by: lane19b
blocked_by: []
relates: [PW-818, PW-846]
refs: [planet/surface.py, planet/tectonics/, tools/scorecard.py]
created: 2026-10-28
updated: 2026-10-28
---

## Description
Lane 19 added clinoform progradation to surface._offshore (PW-818: sediment arriving at the shelf brink fills the
slope cell toward shelf level). Measured over seeds 1-6 at L6, 600-1000 Myr mean: shelf (0..-200 m) 1.40% -> 1.46% of the
ocean; median submerged continent -1500 -> -1464 m (Earth at L6: ~5.8% and -184 m). Scorecard seeds 1/2 at 1 Gyr:
shelf 0.7% and 2.0%. Sediment supply is not the limit: drowned continental crust sits ~1.5 km down, far below any
wedge the rivers can build. Likely cause: the submerged continent's isostasy is computed as if unloaded (or air-loaded),
so a flooded margin sinks too far; under water a column floats ~1/(rho_m - rho_w) not 1/(rho_m) higher per km of
crust thinned. Try water-loaded isostasy for sea cells of continental crust (no fudge to the shelf target).
- [ ] median submerged continental cell within -100..-500 m on ~70% of seeds at 1 Gyr
- [ ] shelf share of ocean >= 3% without a pass-rate cost on the paired judge

## Updates
- 2026-10-28: Owner 10-28: if it fails a round or three, record what was tried, why it failed and suggestions, then move it to v2.
- 2026-10-28: Created from inbox draft draft-shelf-water-loaded-isostasy.md (found by lane19b).
