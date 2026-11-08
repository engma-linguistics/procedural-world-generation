---
id: PW-1468
title: A single 10.6 km cell at 260 Myr on an L6 judge draw, not on continent crust at the cap
type: task
status: todo
parent: PW-244
milestone: later
subsystem: tectonics
effort: s
impact: low
found_by: scout-190-pw1446b
blocked_by: []
relates: [PW-1446, PW-172, PW-285]
refs: [docs/review/tectonics/mountains/scout3.md, docs/review/tectonics/mountains/scout3_hyps.py, "tools/ice_diag.py::hyps_sample", "planet/tectonics/isostasy.py::elevation", "planet/tectonics/isostasy.py::max_km", "paired draw r0.0005 l6c_p seed 619496 (L6, 1 Gyr, climate_offset 0.0015, star_brightening 1.0)"]
created: 2026-11-04
updated: 2026-11-04
---

## Description
In plain words: one frame of one test planet has a single cell 10.6 km high. If this is never looked at, a world sliced at a moment like that shows a peak higher than Everest's whole mountain (8.85 km), which looks visibly broken.

Seen by scout 190 (PW-1446 (b), scout3.md §3) in the `hyps` record that `tools/ice_diag.py` now writes every 10 Myr. On the cap branch (`isostasy.max_km`), draw r0.0005 `l6c_p` seed 619496 has a highest bed cell of 10,576 m at t = 260 Myr. The continent's thickest crust at that moment is 71.7 km, so the cell is not continent at the cap. It is probably a hotspot pile at sea or newly made land on one (the PW-172 / PW-285 family). It is the only sample above 7.6 km in 36 draws x 100 samples. Main's arm of that draw was run before `hyps` existed, so whether main does the same is unknown. The cap change touches only continent, so this is likely on main too.

What I'd try: rerun that draw to 260 Myr on main (`tools/ice_diag.py --seed 619496 --myr 260 --level 6 --set star_brightening=1.0 climate_offset=0.0015`, ~10 min at 1 thread) and print the top cell's crust, rock, cover, swell and `cont`.
- [ ] the cell's height split into its terms, and whether main has it

## Updates
- 2026-11-04: Created from inbox draft draft-l6-spike-10km-not-continent.md (found by scout-190-pw1446b).
