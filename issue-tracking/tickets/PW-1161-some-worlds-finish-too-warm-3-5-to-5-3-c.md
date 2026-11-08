---
id: PW-1161
title: Some worlds finish too warm (+3.5 to +5.3 C) now that the finish-window CO2 crash is fixed
type: task
status: done
parent: null
milestone: later
subsystem: climate
effort: m
impact: high
found_by: lane71
blocked_by: []
relates: [PW-865, PW-1091]
refs: [planet/tectonics/earth.py, docs/review/base-climate/v1-finish-16/pjudge.py]
created: 2026-10-30
updated: 2026-11-05
---

## Description
In plain words. Lane 67 found that every run's CO2 crashed for one step at the start of its final stretch, which
made each world's "present" come out colder than it should. That bug is fixed (main 3cc79068). With the fix, some
worlds' present comes out too warm instead: 3.5 to 5.3 C above pre-industrial, against the allowed -6 to +3 C. The
crash had been hiding them.

Evidence (lane 67's paired judge, 18 L6 draws, roll 0.0005, X arm = today's main physics; scratch
l67/judge, tallied by lane 71's warmend.py). End T against pre-industrial:
- 53669 l6c_0: +4.6; CO2 index at the end +0.58 e-folds. A big late ice episode came first (22% of land iced at
  848 Myr, T -7.9 C), then +6.8 C, so it may be a rebound after the ice let go.
- 583167 l6c_p: +4.3; CO2 index +1.09. Also frozen over (44% at 648 Myr), so it's an ice-linked case too.
- 53669 l6c_m: +4.5; CO2 index +0.28. Late ice <= 4%, so not ice-linked.
- 733847 l6c_p: +5.0; CO2 index +0.71. Late ice <= 12%, not ice-linked.
- 957317 l6fix: +3.5; CO2 index +0.49. Late ice <= 10%, not ice-linked.
So 2 of the 5 follow an ice collapse and 3 don't. The three with no ice link sit 0.3-0.7 e-folds above the CO2
balance at the end, with a warm drift. The warmth looks like the carbon cycle's end state, not the ice.

What to look at: the end-anchored balance (PW-865 option C keeps PCO2_BALANCE 500 ppm at dT +1.5) against the
finish window's weathering. Is the late-window CO2 index sitting above 0 because the sink's reference was learnt
during an icier, less weatherable stretch? Also look at the drift's share of the end T. The PW-1142 lane will
show whether its ice fix changes the two ice-linked cases.
Lane 71's screen (7 draws, 3 of them controls that finished in range on main) makes it worse with the ice
fixes: with the warm-phase kitchen sink, two controls finish at +6.0 and +3.6 C; with the seasonal lapse alone,
three finish at +4.1, +5.8 and +11.0 C. Less ice means a weaker albedo term at the end, so it may be the same
carbon-balance warmth with less ice to hide it.
- [ ] A written split of each warm finish's end T into CO2 term, albedo term and drift
- [ ] A cause (or "chaos, accept") sent to the coordinator before any change

## Updates
- 2026-11-05: Status -> done (chaos, accept). Scout 203 (docs/review/climate/warm_finishes/scout1.md): on today's code 36 fresh L6 draws: 0 hard, soft 32/36, warm-side fails 2/36, end T median +0.11 C; twins (same seed, tiny change) correlate -0.07. Reopen if a 36-draw judge shows warm fails >10% or median >+1.5 C. L7 not re-checked.
- 2026-11-03: Milestones 11-03: v2 -> later: physics side track, ranked 6; gates no tag (re-check after D47)
- 2026-10-30: Lane 80 split (docs/review/base-climate/finish-drift-l80/README.md; coordinator: climate done for v1,
  so moved to v2). The warmth is physical red variance of a sound loop. End T has median +0.1 C and sd 3.7 C over
  the 18-draw K judge. F = ln source - ln erosion supply (last 10 Myr, against the references) explains R2 0.52 at
  11.3 C per e-fold. Adding the ice-albedo term gives R2 0.93 (albedo/CH4 amplify ~1.4x). Source variance is slow
  (autocorrelation 0.71 at 10 Myr, 0.1 at 50), so it is not jitter. Warm draws: 639472 l6c_p +7.3, 958504 l6c_p +6.0
  and 639472 l6fix +3.9 have the source near reference (+0.02..+0.05) and erosion supply down 0.23-0.33 e-folds
  (erosion rate -0.27..-0.45); 583167 l6fix +3.6 has the source high (+0.19). No finish-window bias: the window
  minus the 20 Myr before gives ln src +0.025 +- 0.03 and T -0.04 C. Two systematic drifts cancel in the median
  (draft-sink-supply-reference-learnt-bare.md, with PW-1158). Band question for the owner: draft-warm-finish-band-edge.md.
- 2026-10-30: Created from inbox draft draft-too-warm-finishes-after-co2-fix.md (found by lane71).
