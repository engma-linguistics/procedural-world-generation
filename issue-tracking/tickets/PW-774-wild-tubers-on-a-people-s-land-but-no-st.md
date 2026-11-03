---
id: PW-774
title: "Wild tubers on a people's land but no staple: independent cultivation is 0.03/kyr per landmass (anja, run dcdfd4)"
type: task
status: todo
parent: PW-691
milestone: later
subsystem: food
effort: s
impact: low
found_by: fun16
blocked_by: []
relates: [PW-721, PW-762]
refs: [planet/lineages/animals.py, planet/lineages/crop_defs.py]
created: 2026-10-24
updated: 2026-10-26
---

## Description
Checked, no bug. Run dcdfd4: the farming orcs (anja, southern lat -35 to -65, 2173 cells at L7) have the wild potato-like tuber on
1351 of them (62%) but the crop is known on none of them. The potato was first cultivated once (10.0 kyr, the northern continent
at 18N 43E) and reached the 60 Mkm2 continent by planked boat at 5.6 kyr; the front (animals.Stock._front) moves only over
peopled land, so it never reaches anja's separate southern land. The other route is an independent re-taming
(`Stock._tame(first=False)`): per landmass with enough wild range and tamers, chance `1 - exp(-again * dt * n_landmasses)`
with `again = 0.03` per kyr (crop_defs._crop), blocked once the crop is known anywhere on that landmass (`has_use`) and
for landmasses that already had one. Over the ~10 kyr of farming that is about a 25% chance per landmass: so a people
sitting on wild tubers usually waits for the crop to arrive.

Options: A leave (diffusion-and-isolation is the intended story, and anja have wheat/maize at 1.0); B scale `again` by the
tamers' farm/forage share and the wild area on the landmass (a big wild range with farmers on it is a likelier cradle);
C raise `again` to 0.06. Lean A (the wheat/maize rows already carry anja; isolated crops give regional flavour); B if the
owner wants staples wherever the wild plant is.

## Updates
- 2026-10-26: Parent PW-721 (done) -> PW-691. (PW-900 backlog reorg).
- 2026-10-24: Status needs-decision -> todo. Coordinator: option A (leave) for now; option B (rate scaled by tamers and wild area) is the later refinement.
- 2026-10-24: Created from inbox draft draft-crop-independent-taming-rate.md (found by fun16).
