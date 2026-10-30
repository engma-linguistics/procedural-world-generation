---
id: PW-750
title: After PW-741 both levels spend ~45% of 300-1000 Myr in an icehouse (pass ~30-38% of seed-draws against the ~70% bar); L6's ~33% was the crust thermostat's CO2
type: task
status: done
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: v1-finish-5
blocked_by: []
relates: [PW-741, PW-368, PW-558, PW-564, PW-611]
refs: [planet/tectonics/earth.py, docs/review/base-climate/v1-finish-5/]
created: 2026-10-24
updated: 2026-10-29
---

## Description
PW-741 found why L7 runs were icier than L6: the CO2 source counted the arcs' crust growth including the volume
thermostat's gain, which climbs to ~2.5-4 over 300-1000 Myr at L6 but stays ~1.1-1.8 at L7, so L6's outgassing rose
~20% above its frozen reference and kept L6 ~1 C warmer. With the arcs outgassing at their nominal rate the two
levels agree (v1-finish-5): icehouse median ~44% at L6 (17 draws on 8 seeds) and ~45% at L7 (8 draws on 4 seeds),
pass rate ~30% and 38%. The planet is now as icy at L6 as it always was at L7.

So the remaining gap to the owner's bar is the model's mean climate, the same at both levels. The ice response by dT
pooled over the runs: icehouse ~85% of the time at dT -1..0, ~50% at 0..2, ~15% at 3..4; mean dT over 300-1000 is
~+1.1 (L6) / +2.0 (L7) with fix. The source falls slightly below its reference after REF_FREEZE on most seeds (the
reference is the 200-300 Myr balance, a breakup-time high), so CO2 drifts down.

Options (owner's call; not a resolution question any more):
- A. Accept ~45% icehouse as v1 (Earth spent roughly a quarter to a third of the Phanerozoic in icehouse states; the bar is ~40%).
- B. PW-368's narrower drift (3 -> 2 C), decided on PW-240 and parked: fewer deep dips.
- C. PW-564's brightening star (a physical warming trend after the reference freezes), measured first.
- D. A different reference (the source's long-run mean rather than the 200-300 Myr window): a design change to PW-558/559 B.
No per-level factor needed: the levels agree.

## Updates
- 2026-10-29: Removed docs/review/base-climate/v1-finish-6/ in cleanup; last present at 9861e2df.
- 2026-10-24: Status needs-decision -> done. Measured in v1-finish-6: B and D don't reach the bar; continues on PW-761.
- 2026-10-24: Lane v1-finish-6 (docs/review/base-climate/v1-finish-6/): measured at L6 on the same 18 seed-draws. B (drift 2 C) 9/18 pass, median 46%, more deep ice (17% vs 12%); D (source reference = its causal running mean) 8/18, 46%: the 200-300 Myr reference is only ~4% above the long run, no causal D warms; D+B 7/18; probe +1.5 C 10/18 (36%, early 2% late 54%); C (star +0.9%/100 Myr, measurement) 17/18 but 16 never-ice, dT +7.4. None reaches ~70%; nothing merged, showcase not remade. Gap is the late weatherability trend (PW-708). Decision draft: draft-icehouse-bar-late-trend-after-pw750.md (lean: accept for v1, do not apply B).
- 2026-10-24: Coordinator (geophysics delegated): measure B (drift 3->2 C, already decided on PW-240) first at L6 multi-seed, then D if short; owner signs off v1 on the outcome.
- 2026-10-24: Created from inbox draft draft-icehouse-share-both-levels-after-pw741.md (found by v1-finish-5).
