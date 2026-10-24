---
id: PW-741
title: "After PW-725, L7 runs still spend ~15-25 points more of 300-1000 Myr in an icehouse than the same seeds at L6 (new showcase: 4 of 4 seeds icier at L7, 1-2 of 4 pass vs 3 of 4)"
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: v1-finish-4
blocked_by: []
relates: [PW-725, PW-736, PW-460, PW-202]
refs: [planet/tectonics/earth.py, docs/review/base-climate/v1-finish-4/, docs/review/base-climate/v1-finish-3/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-725 put the run's margin band in km and took the L7 showcase from 0/4 to 5/8 passing draws (median 33%), with the
per-seed L7-L6 gaps mixed (-17..+44 points on one draw, -6..+20 on the other). The v1 showcase made on that code
(four new random seeds, `planet make --level 7`, docs/review/base-climate/v1-finish-4/) against the same four seeds
at L6 (tools/ice_diag.py, same code), icehouse share of 300-1000 Myr (passrate.py):

| seed | L7 (showcase run) | L6 |
|---|---|---|
| 957317 | 64% ICEBOX (deep 30.1%) | 48% F |
| 619496 | 42% (just over the bar) | 23% ok |
| 583167 | 22% ok | 0% ok |
| 639472 | 60% ICEBOX (deep 30.1%) | 32% ok |
| pass / median | 1/4 (2/4 counting 42%), 51% | 3/4, 28% |

Every seed is 16-28 points icier at L7. One draw per seed per level, and a single draw moves by about +-17 points,
so one seed proves nothing; but 4 of 4 one way, together with v1-finish-3's mean of about +7 over its 8 pairs,
points to a remaining level effect of ~10-15 points. Pooled over the 12 L7 draws on PW-725's code: 6/12 pass
(7/12 counting 42%), median ~41%, against L6's 33% median over 32 draws and the ~70% pass bar.

Candidates, in the order PW-725 left them: the margins' last cell (the band is whole rings of cells, so 120 km
rounds to 2 rings of ~60 km at L7 but only approximately; the sub-cell ramp PW-460 retires it), and the finer
relief (L7's higher, sharper peaks start and hold caps that L6's smoothed relief doesn't: v1-finish-3's L7 vs L7s).
eqcurve.py (v1-finish-3) on one of these runs, e.g. 27929a or 656f66 at a cold moment, would split the two.

- [ ] eqcurve.py L7 / L7s / L6 on 656f66 and 27929a at a moment where L7 ices and L6 doesn't
- [ ] if it's the relief, decide (owner) whether L7's own peaks icing more is acceptable physics or a bias to
  remove; if it's the band, PW-460
- [ ] re-judge the L7 pass rate on a few more draws after any fix (seed-pass-rate rule: several re-rolled draws)

## Updates
- 2026-10-24: Created from inbox draft draft-l7-runs-still-icier-same-seeds.md (found by v1-finish-4).
