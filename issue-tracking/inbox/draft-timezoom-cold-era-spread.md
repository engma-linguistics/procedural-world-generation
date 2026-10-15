---
title: "Time zoom: cold-era generated worlds still drop ~250 m, because the run's ice has no ablation zone"
type: task
status: needs-decision
parent: null
subsystem: timezoom
effort: m
impact: high
found_by: finish
blocked_by: []
relates: [PW-031, PW-190, PW-102, PW-189]
refs: [planet/timezoom.py, planet/tectonics/earth.py, "world 8e71fd", "run ee65aa", "world bcc894"]
---

## Description
After the PW-031 nudge (sea level from the water the ice holds; a run's start counted as the
cycle average, so half the CO2 / ice-albedo caps), the time zoom of world bcc894 (run e0e21e
@ 688 Myr, dT -3.3) peaks at -132 m (was -171) and an Earth-like moment (e0e21e @ 592, dT -0.7)
at -95 m. But world 8e71fd (run ee65aa @ 632 Myr, dT -5.8, LGM-cold, sea already -274 m) still
reaches -258 m (was -272), and almost all of it is not the feedbacks: with CO2 and ice albedo
off, and even with the orbit off, it still falls -210 m in 60-80 kyr.

Diagnosis: the main run's ice (PW-102 rule: where summers stay below 1 C and snow beats melt,
no flow) is all accumulation zone. Every starting ice cell gains (median +0.17 m/yr; the
start_anchor is zero there), ~10,800 Gt/yr of snow against ~1,700 Gt/yr of melt. The flowing
sheets must spread until melt and calving balance them: 6.3% -> ~14% of the surface (all land
poleward of ~55 deg, which the run had partly bare with summers of 2-4 C). Starting warmer over
the ice (+3 or +6 C over the start sheets) only slows it.

Options:
- A. Accept: a cold-era moment's ice-age maximum really is far bigger than the run's average
  ice; document it (done in overview 2.14) and let finished worlds show it.
- B. Balance the start: a sheet-by-sheet temperature correction (two-sided anchor) found by a
  short spin-up, so the start ice neither grows nor shrinks at the mean orbit; cycles then swing
  around the run's ice. ~1 min extra at L7; changes the meaning of the anchor for Earth too.
- C. Fix the source: make the main run's ice rule flow-consistent (extend it by an ablation
  zone; ties to PW-190's too-thick run ice and PW-189 isostasy). Biggest, but fixes both.
Lean: C as the real fix (with PW-190), A meanwhile; B only if finished cold-era worlds must look
moderate soon.
