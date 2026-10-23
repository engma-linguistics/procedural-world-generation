---
title: "The mantle's harmonic basis is built by an SVD whose columns are arbitrary within a degree, and it is cached per checkout: a checkout whose cache was built differently runs other worlds from the same code"
type: task
status: todo
parent: null
milestone: v1
subsystem: tectonics
effort: s
impact: high
found_by: thermostat-1024
blocked_by: []
relates: [PW-680, PW-643]
refs: [planet/tectonics/mantle.py, docs/review/base-climate/thermostat-1024/]
---

## Description
`mantle.basis(grid)` builds the degree 1-8 basis by orthonormalising monomials and taking `np.linalg.svd(B)`'s
first 2d+1 columns per degree. Within a degree the SVD's columns are not unique (any sign, and any rotation where
singular values are close), and LAPACK/BLAS may return a different one by thread count or load. `smooth()` is a
projection, so it does not care. `init()` does: `mantle_eddies` are random coefficients on these columns, so the
eddy field, and from it the whole run, depends on which basis the process got.

The basis is cached in `planet/tectonics/__pycache__/mantle_basis_<n>_<hash>.npy`, per checkout. Lane
thermostat-1024 found three different caches on this machine (md5 of the L4 file: `800f36...` in the main checkout
and most trees; `8791fe...` in this lane's fresh worktree, built while two processes started at once, and in
`pw514/merge_code`; for L5, `7bca5b...` in the pw460/pw462 trees against `10b0cf...` elsewhere). The arrays differ
by up to 0.15 (whole columns). With `8791fe...`, sim4 (L4 seed 1, 300 Myr) is another world: 25.0% land and 11
plates against 30.7% and 6, and `test_bed_settles_under_the_ice` on PW-636's tree passes (27.1 m against 84.7 m)
where the canonical cache fails (47.1 m against 46.2 m).

So two lanes running the same commit can measure different worlds without knowing it, and the in-process
determinism check (`health.py`) can't see it, because both of its runs read the same cache.

Fix (sound, small): make the basis canonical, either
- real spherical harmonics from the Legendre recurrence (degrees 1-8, numpy only), which is unique by definition; or
- keep the SVD but fix each degree's columns: e.g. rotate them onto the projections of a fixed ordered set of
  harmonics, or at least fix the signs. A sign fix alone doesn't cover rotations.

It changes every run (the eddies' field), so the goldens and every stored baseline move: it belongs to the serial
physics lane, merged on its own. Until then a lane can copy the main checkout's `mantle_basis_*.npy` into its tree
(this lane did).
- [ ] canonical basis; goldens regenerated; health and Earth re-baselined
