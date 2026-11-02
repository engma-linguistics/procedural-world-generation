---
id: PW-1295
title: With the sea-floor creep, the continents' outer cells flicker between continent and ocean floor at the 20 km bound
type: task
status: in-progress
parent: null
milestone: null
subsystem: tectonics
effort: m
impact: med
found_by: lane-112
blocked_by: []
relates: [PW-1292, PW-950, PW-108]
refs: [planet/tectonics/crust.py::coherence, docs/review/tectonics/margin/pw1292-note.md, docs/review/tectonics/margin/pw1295-note.md, docs/review/tectonics/margin/tracediag.py]
created: 2026-11-01
updated: 2026-11-02
---

## Description
In plain words: with the sea-floor creep on, the model keeps turning the continents' outermost cells into ocean floor
and back again. The churn PW-1292 was opened for (+45 000 born, -40 000 shredded per 400 Myr) is mostly this, not
isolated sediment piles. Turning isolated piles to ocean floor (PW-1292 option A) changed it by 0-14%.

Numbers (L6, seeds 1 and 3, 600-1000 Myr, tracediag.py `births`, docs/review/tectonics/margin/pw1292-note.md): with
`neck_km=200 rise=1 slope_k=1000`, coherence shreds 3300-3800 cells against 1100-1300 on main. Only 660-840 of them
are pile rock. Births of crust that is mostly basement (classed "arc") double, 990-1060 against 410-430, though no
arc process doubles. Requiring 3 continental neighbours for a pile's birth (screen `pile_touch=3`) didn't reduce the
churn and ran 4-5 C colder on both seeds.

Likely cause (not yet proven): the birth bound and the shred bound are the same 20 km (`BECOMES_CONT_KM`). Necking
and the creep stripping the cover leave the margin's outer cells near 20 km. Below it, with at most 2 continental
neighbours, a cell is shredded and keeps its thickness. When sediment or crust flow brings it back to 20 km, it is
born again.

What to try:
- [x] tag the shredded cells in tracediag.py and count how many are born again within 50 Myr (confirms or rules out the flicker)
- [x] if confirmed, screen hysteresis between the bounds (a shred only below ~15 km, or re-birth of a shredded cell only above ~25 km), on seeds 1 and 3 with the creep
- [x] then a paired judge of the creep on top of it (judge 2 in deep-dive.md failed with 2 frozen-over worlds): not run, moved to draft-sea-creep-still-cools-with-the-flicker-cured (the screens show the cooling stays)

## Updates
- 2026-11-02: Status done -> in-progress. 11-02: merge reverted (code only): slow test_envelopes seed 2 (L5, 400 Myr) goes 15.8 -> 28.8 C, pCO2 327 -> 3547 with SHRED_KM 15. Back to lane 115 for re-rolled draws before calling it chaos or signal.
- 2026-11-02: Merged 7dac9049 (SHRED_KM 15). Land -1.25 points, climate unmoved; follow-up PW-1314.
- 2026-11-01: Created from inbox draft draft-margin-cells-flicker-at-the-20-km-bound.md (found by lane-112).
- 2026-11-02: Lane 115. Confirmed (pw1295-note.md): with the creep ~1150 shreds per 400 Myr come within 10 Myr of a
  birth (at 19.3 km) and ~900 births within 10 Myr of a shred, against 140-160 and 60-65 on main. Screened a 15 km
  shred bound (S15), a 25 km re-birth bound (R25) and both: S15 ends the flicker and brings the creep's churn to
  main's level, statelessly. `crust.SHRED_KM = 15` is on. Judge (36 draws, creep off): 0 hard failures, 32/36
  against 33/36, climate unmoved, land -1.25 points (moved; the area thermostat counts the kept thin margin: draft).
  The creep-on judge wasn't run: creep + S15 screens 3 C colder than S15 (draft).
- 2026-11-02: Lane 115, round 2 (after the revert, 4e3185dc): test_envelopes' world re-rolled over 20 seeds at its own
  settings (L5, 400 Myr; docs/review/tectonics/margin/envdraw.py). Out of band: 1/20 with 15 km (seed 2, 28.8 C), 0/20
  with 20 km; median end T the same (-0.25 C paired). Seed 2's hothouse is the frozen CO2 references (REF_FREEZE)
  locking in a spin-up dip of the arcs and ridges. That dip is systematic with 15 km (spin-up source -7%, lower on
  17/20; subduction erosion's area gain higher on 7/7), so the bound makes such trips a little likelier. Diagnosis and
  candidates in pw1295-note.md section 4; first a cheap check of whether kept thin margins jam trenches. No fix made.
