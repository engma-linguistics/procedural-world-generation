---
id: PW-171
title: Pits in continents (2+ km below their continental neighbours), from old ocean seams and welded inlets
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: tectchurn
blocked_by: []
relates: [PW-108, PW-048]
refs: [planet/tectonics/events.py, planet/tectonics/crust.py, tools/churn.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
`tools/churn.py`'s 'spike' counts cells with >= 4 continental neighbours more
than 2 km off their median: ~2.4% of continental cells at L6 s21 (base), ~1.5%
after PW-108's crust.coherence (which welds one-cell ocean inlets into the
continent but keeps their thickness, so they stay ~4 km deep pits until
sediment fills them). Sources seen while diagnosing PW-108:
- sutures: `events.merge` pulls gone's crust into keep's *unowned* cells only
  and resamples it nearest-of-nearest; keep's own ocean cells along the
  suture stay as a seam of old (100-300 Myr) ocean inside the welded
  continent (L6 s21 300 Myr: a 1-cell line of -4 to -5 km through a craton,
  plate 5), and at big sutures ~2% of gone's world cells change type at
  once (L6 s21 176-218 Myr: 43-100 cells each);
- arcs and margins leave one-cell ocean enclaves; the weld keeps their depth.
Options: (A) at a merge, make keep's frame reproduce the world view (copy gone's
sampled crust over keep's cells under gone's world cells, owned or not);
(B) let a welded inlet take its continental neighbours' thickness, booked as
coherence (adds crust), or fill it with sediment from them (conserves it);
(C) leave it to deposition (slow: a 4 km pit needs ~12 km of sediment).
Lean A and C, check B against the crust budget.

## Updates
- 2026-10-14: Created from inbox draft draft-continental-pits.md (found by tectchurn).
