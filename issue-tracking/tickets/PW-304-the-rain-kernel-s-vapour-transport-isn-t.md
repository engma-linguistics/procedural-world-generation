---
id: PW-304
title: The rain kernel's vapour transport isn't mass-conservative (fresh-water residue ~1 cm/yr on L6 planets, up to 0.6 m/yr on banded test planets)
type: task
status: todo
parent: PW-245
milestone: v2
subsystem: climate
effort: s
impact: low
found_by: climate-ocean
blocked_by: []
relates: [PW-266, PW-211]
refs: [planet/climate.py, planet/ocean.py]
created: 2026-10-15
updated: 2026-10-21
---

## Description
With PW-266 the rain kernel takes up exactly what the sea and the land's water balance evaporate, so rain − evaporation over the sea plus the rivers should come to ~0. It doesn't quite, because the kernel's own transport loses or gains vapour:
- `inflow_weights` divides each cell's inflow by what a uniform wind would bring it (PW-211's seam fix). That is not conservative where the wind converges or diverges.
- The eddy mixing `(1 − d_i)·m_i + d_i·mean(neighbours)` isn't symmetric when `d` or the degree varies from cell to cell.
- Cells are treated as equal masses, but their areas vary by ±9%.
- The rain and the uptake are averaged over the last quarter of the iterations, which may not be steady at level 4 (70 iterations).

Measured as the residue in m/yr over the sea, after PW-266:
- L6 seed 3199 planet: +0.005. L6 seed 11: −0.010 (the kernel alone −0.016). Earth L6: +0.001.
- L5 two-basin planet: +0.005. L4 two-basin planet: +0.028 (+0.014 of it is rain cut off at the 8000 mm/yr clip).
- Banded test planet (land at |lat| < 40, `test_climate_responds_to_dT`), dT = ±5: −0.6 to +0.08. The same planet on main (before PW-266) showed −0.47..+0.65.

`ocean.freshwater` still removes the mean and warns above 2 cm/yr (`FW_RESIDUE`). So the pytest run prints ~160 such warnings from the L4 test planets.

Fix: make the transport conservative (each cell sends its moved vapour out in shares that sum to 1, and the inflow is what its neighbours send), and give the mixing a symmetric edge form. Keep the PW-211 seam fix in some form, then re-check PW-211's rain-streak test. Then lower `FW_RESIDUE` to 1 cm/yr.

## Updates
- 2026-10-21: Owner 2026-10-21: moved to v2.
- 2026-10-16: Merged inbox draft draft-pw304-land-books-residue.md ("PW-304 after PW-015: the transport is conservative; the residue left (L4 -1..-4 cm/yr) is the land books' (storm spread, first-pass PET)", found by pw015-rain).
  For PW-304 (probably `--merge-into PW-304`). PW-015 stage 1's finite-volume transport keeps the vapour's
  mass exactly: the kernel's steady-state residue is -0.01..-0.08% of rain at L6 (main -0.14 / -0.66%),
  -0.05 / -0.12% at L7 (the steady state's drift over the 20 days); pytest's fresh-water warnings fell 188 -> 16.
  What's left in `ocean.freshwater`'s check is the land's books, not the transport: two-basin L4 planet -1.4
  cm/yr, L5 -0.14; the timezoom tests' L4 planets -3..-4 cm/yr; health L6 runs occasionally -2 cm/yr. Causes:
  the storms' spread of frontal rain after the kernel moves ~0.9 cm/yr of rain from sea to land (L4), whose
  evaporation the kernel's land_e never saw; and the kernel's land evaporation uses the first-pass PET, the
  water balance's runoff the final temperatures'. FW_RESIDUE stays at 2 cm/yr until those close.
  - [ ] land evaporation in the kernel and runoff in the water balance from the same rain and PET
  - [ ] then FW_RESIDUE 1 cm/yr
- 2026-10-15: Docs cleanup: the after-audit 1 Gyr health sweep (8 L6 + 3 L7 seeds, main after the audit fixes) logged 402 fresh-water imbalance warnings, residue -2.0..-6.1 cm/yr (all negative; larger than the ~1 cm/yr quoted above for L6 planets). The full log is docs/review/after-audit-2026-10-15/health.log at commit 29ab7d4.
- 2026-10-15: Coordinator: at L4 the freshwater check warns on every climate update (+2..+4.7 cm/yr over its 2 cm/yr threshold), ~450 warnings per pytest run; fixing the leak or scaling the threshold by level would quiet it.
- 2026-10-15: Created from inbox draft draft-climate-ocean-rain-transport-leaks.md (found by climate-ocean).
