---
id: PW-226
title: Ice caps 2.4 km thick on 7 km polar ranges give coldest months of -105 C
type: task
status: done
parent: null
milestone: null
subsystem: tectonics
effort: s
impact: low
found_by: vegclim
blocked_by: []
relates: [PW-190, PW-203]
refs: [planet/tectonics/earth.py, tests/test_invariants.py, planet/climate.py]
created: 2026-10-15
updated: 2026-10-16
---

## Description
After merging main (2026-10-15, with the vegetation feedbacks of PW-203 and main's ice/vegetation fixes), the L4 test run (seed 1, 300 Myr; tests/conftest.py sim4) grows a 2.4 km ice cap on a 7.1 km range at 78 N: the ice surface sits at ~9.5 km and its coldest month is -105 C (annual -80), which broke test_values_sane's -95 C bound (relaxed to -110 on the vegclim branch, with a comment). Not caused by one feedback: a seed sweep (L4, seeds 1-5, 300 Myr) gives coldest months of -33 to -105 with or without the vegetation feedbacks (without them seed 1 happens not to glaciate that range, -50; seed 4 reaches -69 to -82 either way); whether a high polar range glaciates is chaotic.

Real ice surfaces stop near 4 km (Antarctica) because a thick cap on a high range flows away to its sides and has too little snow at that height. Check whether ice_sheets limits ice thickness on high ground (precipitation falling off with height, flow to the margins; PW-190 land ice depth) and restore the -95 bound if it does.

## Updates
- 2026-10-16: Status in-progress -> done. Fixed already by PW-276 (thin caps' coldest months -61..-83 C in the L4 seeds 1-5 sweep; -95 C bound back in test_values_sane). Sea-ice air in deep icehouses is PW-337.
- 2026-10-16: pw313 check on main 6392e18: fixed by PW-276. The -95 C bound is back in test_values_sane. Sweep L4 seeds 1-5 x 300 Myr: coldest land months -69/-80/-83/-61 C (seeds 1, 2, 4, 5) on 340-380 m caps over 5.2-6.8 km beds; thickest ice 4 km in basins. Seed 3's -114 C is sea-ice air in a deep icehouse (draft-sea-ice-air-unbounded), not a cap. Lean: done.
- 2026-10-15: Status todo -> in-progress. Run-lane agent started (polar summers / Antarctica).
- 2026-10-15: Merged inbox draft draft-ice-cold-high-peaks.md ("Coldest months near -95 C on 8+ km polar-ish peaks (bare or margin-thin ice) after PW-276", found by ice-fix).
  After PW-276 (ice surface from the margin's bed) and PW-277 (one ice-surface climate) the run's ice on high
  ground is margin-thin (~350 m), so the remaining extreme surfaces are the peaks themselves. Probe over every
  climate update (L5, 1000 Myr): seed 2 coldest month -93.5 C (1 cell below -90), seed 11 -97.4 C (8 cells); highest
  iced surfaces 9.2 / 8.4 km, i.e. 8-9 km peaks at ~60-65 deg plus a margin's ice (L4 seed 4: -97.5 C on a 7-8 km
  plateau at 66-74 N). test_values_sane's restored -95 C bound holds on the L4 seed-1 test run (-55 C) but would
  not on these.
  It is now the lapse rate on very high ground in a continental polar winter, not the ice. Worth checking:
  - whether 8-9 km peaks at 60+ deg are expected (PW-172 is about > 9.5 km spikes);
  - whether the climate's winter inversion (polar winters are colder at the ground than aloft, so a peak is not
    6.5 C/km colder than a frozen lowland in January) should cap the lapse rate's cooling in winter.
  - [ ] coldest months above ~-90 C on L5/L6 seeds 2 and 11, or a stated physical reason for the colder ones
- 2026-10-15: Created from inbox draft draft-polar-range-ice-cap.md (found by vegclim).
