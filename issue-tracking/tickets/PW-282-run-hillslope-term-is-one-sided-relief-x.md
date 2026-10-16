---
id: PW-282
title: "Run hillslope term is one-sided relief x 1/d^2, not a Laplacian: doubles per grid level"
type: task
status: done
parent: PW-245
subsystem: surface
effort: s
impact: med
found_by: audit-surface-hydro
blocked_by: []
relates: [PW-243]
refs: [planet/surface.py, docs/review/audit/surface-hydro.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`surface.erode` (surface.py:242-246) lowers each cell by `_relief` (mean of the one-sided drops to its lower
neighbours) x (1 - exp(-4 kappa K dt / d^2)) and calls it "the Laplacian ... the same at any resolution". A one-sided
mean drop is first order: about slope x d on a uniform slope, where a Laplacian is 0. So the lowering scales as
slope / d. Measured on one smooth synthetic continent: 0.67 / 1.34 / 2.48 m per step at L5 / L6 / L7. Incision
goes the other way (2.38 / 1.56 / 1.04 m). L7 wears its land mostly by hillslope, L5 mostly by rivers; the
level-5-tuned `hillslope` is 2x too strong at L6 and 4x at L7. This may account for part of PW-243's L6/L7 gap.
Fix (simplest sound): a slope law, dh = kappa' K (relief / d) dt, with kappa' chosen so L6 is unchanged. Fix the
docstring.
- [ ] hillslope lowering on the synthetic continent within ~20% across L5-L7
- [ ] L6 golden updated on purpose; scorecard; PW-243's L6 and L7 inland drainage remeasured

## Updates
- 2026-10-15: Status in-progress -> done. Done in the surface-hydro fix branch (merged 4d3b46f); docs/review/audit/fixes-surface-hydro.md.
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Created from inbox draft draft-audit-surface-hydro-hillslope-level.md (found by audit-surface-hydro).
