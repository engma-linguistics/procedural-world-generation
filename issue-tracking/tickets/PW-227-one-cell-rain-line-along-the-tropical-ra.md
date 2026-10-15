---
id: PW-227
title: One-cell rain line along the tropical rain belt's convergence latitude
type: task
status: done
parent: PW-013
subsystem: climate
effort: s
impact: low
found_by: vegclim
blocked_by: []
relates: [PW-019, PW-211]
refs: [planet/climate.py, "world 351f32"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
After the grid-artefact fix (PW-211: the coarse-blur lattice and the icosphere seams are gone from the winds and the rain), one thin artefact is left on flat tropical land: a straight east-west line of extra rain one cell wide at the latitude where the trade winds from both hemispheres meet (world 351f32, lat ~-5.6, lon -120..-60, January; about the belt shift). The rain kernel's upwind transport piles the vapour of both converging airstreams into the one row of cells where the north-south wind changes sign; the eddy mixing (`diffusion`) is weakest there (low storminess).

Physically the convergence does make the rain belt, but over the belt's width (`itcz_w` = 10 deg), not one cell. Try: spread the meridional convergence (e.g. extra mixing across the belt, `diffusion` + something x `itcz`), or take the rain kernel's large-scale rate from the smoothed convergence rather than letting the transport concentrate it. Check that the belt's total rain doesn't change.
- [ ] no one-cell line at the convergence latitude on 351f32 / bcc894 rain maps
- [ ] tools/earth_check.py tropical bands unchanged or better

## Updates
- 2026-10-15: Status todo -> done. Merged (smalls2).
- 2026-10-15: Created from inbox draft draft-rain-itcz-line.md (found by vegclim).
