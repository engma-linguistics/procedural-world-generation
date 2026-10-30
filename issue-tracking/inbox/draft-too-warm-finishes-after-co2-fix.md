---
title: "Some worlds finish too warm (+3.5 to +5.3 C) now that the finish-window CO2 crash is fixed"
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: lane71
blocked_by: []
relates: [PW-865, PW-1091]
refs: [planet/tectonics/earth.py, docs/review/base-climate/v1-finish-16/pjudge.py]
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
