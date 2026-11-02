---
id: PW-1297
title: The biggest remaining numpy glue calls np.exp, which numba cannot match bit for bit (needs-decision)
type: task
status: done
parent: null
milestone: v2
subsystem: infra
effort: m
impact: med
found_by: lane-114 (PW-252)
blocked_by: []
relates: [PW-252]
refs: ["planet/climate.py::_erf", "planet/climate.py::months", "planet/climate.py::koppen", "planet/tectonics/isostasy.py::sediment_lift", "planet/tectonics/isostasy.py::elevation", docs/review/speed/pw252.md, tests/test_golden.py]
created: 2026-11-01
updated: 2026-11-02
---

## Description
In plain words: PW-252 ported the numpy glue whose arithmetic numba reproduces exactly (cos, sqrt, min/max,
sums in order). The next-largest glue calls `np.exp`, and numba's exp is not the same function as numpy's
(numpy uses a SIMD exp; numba calls libm): on 4M random arguments 4.6% of results differed in the last bit
(measured in lane 114, `par.py` in the PW-252 note). A kernel using exp therefore changes golden hashes.

What it would buy (L7 per 100 Myr, exclusive Python-side seconds, docs/review/speed/pw252.md): `climate._erf`
4.2 s, the gdd5 tail of `climate.months` (most of its remaining 3.3 s), `isostasy.elevation` /
`sediment_lift` (inside `_world_view`'s caller), `koppen` 2.1 s, `vegetation.site` 2.8 s. About 10-15 s of
241 s at L7 (4-6%).

Decision for Daniel: accept last-bit output changes (every number moves by ~1e-16 relative, goldens
regenerated, the climate is not meaningfully different), or keep the numpy exp and fuse only around it
(pass `np.exp(...)` of an (n,)-vector in; saves less).

## Acceptance
- [ ] Daniel picks: regenerate goldens for ulp-level changes, or stay bit-identical with exp precomputed in numpy.
- [ ] Then port `_erf`+gdd5, `sediment_lift`, `koppen`, `site` accordingly; bound the change (max relative diff) on the golden case.

## Updates
- 2026-11-02: Status needs-decision -> done. Lane 118 merged 80d8b181: L7 python-side 150 -> 105 s per 100 Myr (wall ~15-25% under load); goldens regenerated for 1-ulp exp/pow. Rest in PW-1323.
- 2026-11-01: Coordinator 11-01: accept last-bit (1 ulp) exp differences; regenerate goldens with that stated reason. No backward compat, and 1 ulp is below any physical meaning. Queued with PW-1298 as speed part 2.
- 2026-11-01: Created from inbox draft draft-glue-exp-ports-need-ulp-decision.md (found by lane-114 (PW-252)).
