---
id: PW-366
title: "Run ice: the sheets' 50 kPa profile is ~20% thinner than Earth's real sheets and the time zoom's flow (the time zoom's start drift)"
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: med
found_by: tzbatch-2026-10-16
blocked_by: []
relates: [PW-241, PW-295, PW-240, PW-190, PW-276]
refs: [planet/tectonics/earth.py, planet/icemass.py, planet/timezoom.py, docs/review/timezoom/batch-2026-10-16.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
The time zoom's drift from a run's moment (PW-241, PW-295) is mostly the run's ice being thinner than
the time zoom's own sheets, then the time zoom's thicker sheets spreading (height-mass-balance feedback).
Measured with the orbit, CO2 and ice albedo off (pure consistency), on L5 seed 11 @ 200 Myr (dT -8, run ice
12.6% of the surface, 110.7 Mkm3): the time zoom falls -72 m in 2 kyr and -282 m in 20 kyr, then stays.
After 20 kyr its old ice is +53 Mkm3 thicker (median +690 m, margin cells 340 -> 1730 m), it covers 427
more land cells (+44 Mkm3, up to 8 cells beyond the run's margin; their interiors gain +0.8 m/yr under
2.8 km of ice, though an edge's 330 m there would lose ~8 m/yr) and grounds on 154 shelf cells (+8 Mkm3).

Two causes, both in the run's sheet profile (`earth.sheet_surface`, `ICE_TAU`):
1. **The yield stress.** `ICE_TAU` = 50 kPa. On Earth's real ice extent and bed the same profile gives
   Antarctica 19.8 Mkm3 at L6 (ETOPO1 25.1; median -415 m), 19.2 at L7; 75 kPa gives 25.4 / 24.9 (bias +12 /
   -27 m), 100 kPa 29.6 / 29.2. Real sheets fit tau ~70-100 kPa (Greenland's 3.2 km dome ~500 km in: ~90;
   Antarctica's 4 km ~1000 km in: ~70). The time zoom's shallow-ice flow (Glen, A 1e-16 x 3) settles thicker
   than 50 kPa too.
2. **Each cell's rise is the profile's value at its inner edge** (d hops + 10 km in), not its mean over the
   cell: a margin cell holds 340 m, the profile's mean over it is ~740 m at L6 (~1.1 km at L5); +11% volume
   at L6 at 50 kPa (21.9 -> 24.5 Mkm3 on Earth), less at L7.

Experiment (scratch monkeypatch of the run's last climate update, not merged): seed 11 @ 200 Myr L5 with
tau 100 kPa: run ice 144 Mkm3, drift (no forcing) -176 m (was -284), default 150 kyr end -111 m (was -200);
100 kPa + cell mean: run ice 171 Mkm3, drift -94 m, default end -42 m. Capping the ablation zone at cells
that lose < 1 m/yr changed nothing (-273 m). The rest is extent (the run tests new cells under an edge's
330 m only; once the time zoom's flow has thickened them they accumulate: the feedback the run's steady
profile leaves out).

Options:
- A. tau 75 kPa (Earth's Antarctic profile) and the cell-mean rise: the time zoom starts much nearer its
  own balance; the run's ice ~+27% in volume at the same extent, so cold eras' sea levels deepen by about
  as much (PW-240's -246..-340 m eras would reach ~-310..-430), and `icemass.EDGE_H` (330 m, from 50 kPa)
  moves to ~400 m (shared with the time zoom and the zoom's glaciers).
- B. A only for the time zoom's start: the time zoom rebuilds the run's sheets at 75 kPa within the run's
  extent (its sea level then starts a little below the run's).
- C. Keep 50 kPa and document the drift as the time zoom refining the run's thin ice.
Lean: A with PW-240 (the cold-era climate drift) handled first or together, since A deepens exactly the
eras PW-240 says are already too deep.

## Updates
- 2026-10-16: Status needs-decision -> todo. Owner 2026-10-16: close enough unless cheap. Coordinator: parked; thicker sheets would deepen cold eras and need another round of ice-age sweeps. PW-295/241 (time zoom start drift) stay blocked on it.
- 2026-10-16: Icehouse lane (PW-364): the deep cold eras come from extent, not thickness, so this pass leaves tau and the edge rise alone. On the L5 envelope world's 344 Myr geography (continents over both poles, polar land ~1.1 km high) the ice rule's fixed point at dT -4 is -578 m over 16% of the surface (mean ~2.5 km, Nye-consistent for sheets ~3x Antarctica's area); without the carried sheet air it is -85 m / 6.7%: the extent is what grows. Thicker sheets (75 kPa, or the cell-mean rise) would add ~+20-30% depth on the same extent and more through the height-mass-balance feedback (extent). Reconciling with the time zoom needs the run's new margins tested under more than an edge's 330 m (this ticket's point 2) and is best done with PW-015's margin snowfall, since both make ice grow. Note: the run's ice is now settled within each climate update (PW-364), so a run's ice is at its fixed point and a thicker profile's effect would show in full at once.
- 2026-10-16: Created from inbox draft draft-run-ice-profile-thin.md (found by tzbatch-2026-10-16).
