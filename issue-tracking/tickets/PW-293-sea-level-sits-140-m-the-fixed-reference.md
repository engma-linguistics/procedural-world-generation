---
id: PW-293
title: "Sea level sits ~+140 m: the fixed reference (starting ocean, 60 Myr) is older than the model's steady ocean (~50 Myr)"
type: task
status: in-progress
parent: PW-245
subsystem: tectonics
effort: s
impact: med
found_by: audit-fix-tectonics
blocked_by: []
relates: [PW-288, PW-051, PW-053]
refs: [planet/tectonics/earth.py, planet/tectonics/setup.py, docs/review/health-tectonics/report.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
After PW-288 (fixed reference, x0.69, slab drag), health --quick (8 L6
seeds, 500 Myr, frames after 50 Myr): mean ocean age median 50 Myr (p5-p95
36-69; was 38), plate speed 4.5 cm/yr (was 6.2), and sea level median
+141 m (p5-p95 -75..+221; was +34). The basin term is now often in the
soft part of its +-250 m tanh (total sea level max 234 m), so the limiter
does bind softly for much of most runs. Land share did not drop (median
32.8%, was 31.6%).

Why it sits high: setup starts the ocean as a steady-state one with mean
age 60 Myr (PW-053), but the model's own steady ocean, with today's
plates, is ~50 Myr, i.e. shallower by ~200-250 m of floor. So "sea level 0"
is the depth of an ocean the model doesn't keep.

Options:
- (A) Accept: a young-ocean planet has a high sea (that is the physics);
  widen SEA_TECT_MAX to ~400 m as PW-288's lean suggested, so the limiter
  stops shaping it.
- (B) Start setup's ocean at the model's steady state (mean age ~50 Myr),
  so 0 is the model's mean and excursions are breakups/assemblies.
- (C) Revisit the depth law (GDH1 flattening, PW-288's option C): the
  half-space law to 6400 m makes sea level ~30% more sensitive to age.
Lean A+B: B is a re-centring of the start, A lets the term speak.

## Updates
- 2026-10-15: Status todo -> in-progress. Agent started with PW-309.
- 2026-10-15: Status needs-decision -> todo. Owner 2026-10-15: A+B. The start is a convenient initial state, not a claim about early Earth; it only has to settle into realistic behaviour by ~50-100 Myr. B makes sea level 0 the model's own steady ocean, A raises SEA_TECT_MAX to ~400 m so the limiter stops shaping it. Queued after PW-308 (both touch global_temperature's sea-level block).
- 2026-10-15: Created from inbox draft draft-tect-sea-ref-older-than-steady-state.md (found by audit-fix-tectonics).
