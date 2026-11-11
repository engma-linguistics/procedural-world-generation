---
id: PW-1680
title: With Andean shortening and collapse on, land above 4 km rises late in a run (1 Gyr) where the 600 Myr screen saw it fall; check before 1-2 Gyr showcases
type: task
status: done
parent: null
milestone: v1.0
subsystem: tectonics
effort: m
impact: med
found_by: lane 275b
blocked_by: []
relates: [PW-1497, PW-1446]
refs: [docs/scorecard.jsonl, docs/review/tectonics/mountains/scout9.md, docs/review/tectonics/mountains/scout7_measure.py, "planet/tectonics/crust.py::andean_contraction", "planet/tectonics/crust.py::flow_and_orogeny", tools/scorecard.py, tools/judge.py]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: the new mountain physics (PW-1497, on by default since lane 275b) was screened over 600 Myr, where it
cut high ground a little. Over a full 1 Gyr scorecard run it seems to leave more very high ground late in the run
than today's code does. If never checked, 1-2 Gyr showcase planets may have about twice main's land above 4 km
(a visibly over-mountainous world) and nobody will know it came from this change.

Numbers (scorecard, L6 seeds 1 and 2, 1 Gyr; baseline: main a626c541 run the same day, line before c219720a's in
docs/scorecard.jsonl): land above 4 km at 1 Gyr 2.35% and 4.86% (main 1.35% and 1.86%; Earth at L6 ~1.5%); mean over
the 100-Myr snapshots from 200 Myr 1.9% and 1.4% (main 1.3% and 0.8%); seed 2 climbs 0.43 -> 1.97 -> 2.49 -> 4.86 over
700-1000 Myr. Single runs per seed: one seed's trajectory is chaos-dominated (coordination.md, forked screens), so
this may be chance. The paired judge (18 draws) also shows glacial maxima 10 vs 3 of 18 and late dT -0.8 C median
(CI -1.3..+0.5), consistent with more weathering from more high ground. Dry land 17.4/14.0% vs 24.7/24.4%.

- [ ] Re-run `scout7_measure.py` (Andes share, land >3 km, >4 km) on L6 seeds 1, 2, 6001 to 1 Gyr, main against
      the defaults, and say whether the 900-1000 Myr window breaks scout8.md's bar (>3 km mean <= 3.0%, no seed > 3.5%)
- [ ] If it does: find which belts are high late (live Andean margins, or collision plateaus that collapse cannot touch)

## Updates
- 2026-11-10: Status todo -> done. Lane 286 merged: docs/review/tectonics/andes-late.md. Late high ground at 1 Gyr is mountain-building pulses landing on the scorecard's single 1000-Myr reading, not a trend. Over 600-1000 Myr (3 seeds, L6, main 7dae542a): >3 km 2.69% on vs 3.17% off (Earth 2.4%); collapse leaves 96-99% of late >4 km in active belts. Cooling not systematic across seeds. L7 seed 2: >4 km falls to 1.29% (600-1000 Myr), ending at 0.09%; >3 km 4.3% vs Earth 2.5%, cause open (L7 crust thicker). No default change.
- 2026-11-10: Created from inbox draft draft-andes-late-high-ground-1gyr.md (found by lane 275b).
