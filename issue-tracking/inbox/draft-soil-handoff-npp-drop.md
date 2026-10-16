---
title: "Soils hand-off lowers Earth land NPP 9% (62.7 -> 57.0 Pg C/yr): keep, or renormalise harder?"
type: task
status: needs-decision
parent: PW-184
subsystem: surface
effort: s
impact: med
found_by: soils
blocked_by: []
relates: [PW-185, PW-212]
refs: [planet/soils.py, planet/vegetation.py, tools/veg_check.py, docs/proposals/soils.md]
---

## Description
With the soils' buckets and fertility factor (PW-185 step 3), Earth's land NPP on the observed climate falls from 62.7 to 57.0 Pg C/yr (model climate 46.9 -> 43.3), and potential-vegetation agreement from 62.4 to 60.1% (42.4 -> 40.3) (`tools/veg_check.py`, L6 Earth world). The proposal's check was "NPP unchanged within +-5%".

The buckets are renormalised as planned (Earth land means 50 / 137.5 mm, as the old fixed ones), and the fertility factor (0.85 + 0.25 x fertility) / F_NORM with F_NORM its Earth land mean (0.967). NPP still falls because the soils redistribute water and fertility: thin and sandy soils hold less where water limits growth, and old leached tropical soils (fertility ~0.2) lose ~7% light-use efficiency, which maintenance respiration amplifies to ~15-25% of NPP in the tropics (Amazon ~830 -> ~650 g C/m2/yr; MOD17 ~800-1000). Without the fertility factor NPP is 59.8; with fixed buckets and the factor 59.8 too.

Options:
- (A) Keep it: 57 Pg C/yr is nearer Earth's observed ~56 (Field et al. 1998) and the factor stays in decision 6A's 0.85-1.1 (here 0.88-1.14 after F_NORM). Vegetation agreement drops 2.3 points.
- (B) Renormalise the fertility factor on NPP, as the proposal's text says (F_NORM ~0.93 restores ~62): the factor then spans ~0.91-1.18, beyond decision 6A's "mild" range.
- (C) Make the factor act on NPP rather than LUE (multiply the stand's NPP), so 0.85-1.1 stays 0.85-1.1 in NPP and the respiration doesn't amplify it; small change in vegetation.py.
Lean: C if the owner wants 6A's range to mean what it says, else A.
