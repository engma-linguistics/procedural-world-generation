---
id: PW-1318
title: Thin continental margins drag and insulate like full continent, so keeping them leaves the young planet fewer plates
type: task
status: todo
parent: null
milestone: null
subsystem: tectonics
effort: m
impact: med
found_by: lane-119
blocked_by: []
relates: [PW-1317, PW-1295, PW-1314, PW-1316]
refs: ["planet/tectonics/mantle.py::update", "planet/tectonics/mantle.py::traction", "planet/tectonics/motion.py::forces", "planet/tectonics/events.py::maybe_rift", "planet/tectonics/events.py::sutures", "planet/tectonics/events.py::absorb_slivers", "planet/tectonics/crust.py::coherence", "docs/review/tectonics/margin/pw1295-note.md#5-round-3-lane-119-pw-1317-do-the-kept-thin-margins-jam-trenches-no", docs/review/tectonics/margin/jamdiag.py, docs/review/tectonics/margin/envdraw.py, tests/test_envelopes.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the plate model treats every continental cell alike. A 15-20 km thinned margin cell gets the
continental keel's extra drag (2.5x an ocean cell's, `motion.forces` and `mantle.traction`) and warms the mantle under
it like a continent (`mantle.update`'s insulation, `insulation x w_cont x lid`). Real thinned margins have neither a
thick lithospheric keel nor a continent's insulating lid. This matters when the margin is kept as continent: with
PW-1295's 15 km shred bound (reverted on main), the young planet has about 2.5 fewer plates (-17%) over 100-300 Myr on
8 of 8 seeds, so ~9% less plate boundary, ridges and arcs ~8% weaker, the spin-up CO2 source down. That is what made
the frozen CO2 reference fragile on test_envelopes seed 2 (PW-1316). Not the thin margins jamming trenches (PW-1317:
that's ~1 edge in 900).

Evidence (pw1295-note.md section 5, jamdiag.py, L5 test_envelopes world, seeds 1-8, 100-300 Myr medians against the
20 km bound): with the 15 km bound, plates -2.5 (8/8 lower), boundary -178 edges/scale^2 (7/8), slab flux -441 (8/8).
Screen with the 15 km bound but the force balance and the mantle's insulation reading only crust >= 20 km as continent
(`JAM_THICK_DYN=1`): plates -0.8 (5/8), boundary -38 (5/8), slab flux -216 (6/8). Each term alone takes only part
of it (keel only: plates -1.9, 6/8; insulation only: -0.3, 5/8 but boundary still -132). Scratch runs deleted; rerun
with `jamdiag.py SEED 15 300 OUT.json` (and `JAM_THICK_DYN=keel|mantle|1`) on a checkout with d143c2bc.

Why fewer plates follows is not shown (fewer rifts plus more sutures and absorbed slivers, in about equal parts).

What to try (only worth it if the 15 km bound, or any change that keeps more thin margin, comes back):
- [ ] weigh the keel and the insulation by how continental a cell's crust is, e.g. a fraction rising from 0 at the
  20 km birth bound (`isostasy.BECOMES_CONT_KM`) to 1 at ~30 km, instead of `w_cont`; same in `mantle.traction`
- [ ] screen on the 20 envelope seeds (envdraw.py, both bounds): band count, spin-up source (100-300 Myr) and plate
  count against main; then the L6 paired judge
- Caution: this changes every run's plate dynamics (main's thin margins too, ~1.8% of the surface at L5), so judge it
  on its own against main first, not only with the 15 km bound.

## Updates
- 2026-11-02: Created from inbox draft draft-thin-margins-weigh-as-continent-in-plate-dynamics.md (found by lane-119).
