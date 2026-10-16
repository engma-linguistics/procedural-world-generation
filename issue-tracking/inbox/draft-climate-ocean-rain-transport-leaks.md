---
title: The rain kernel's vapour transport isn't mass-conservative (fresh-water residue ~1 cm/yr on L6 planets, up to 0.6 m/yr on banded test planets)
type: task
status: todo
parent: PW-245
subsystem: climate
effort: s
impact: low
found_by: climate-ocean
blocked_by: []
relates: [PW-266, PW-211]
refs: [planet/climate.py, planet/ocean.py]
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
