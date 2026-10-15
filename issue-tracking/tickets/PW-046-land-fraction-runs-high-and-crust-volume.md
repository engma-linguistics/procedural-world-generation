---
id: PW-046
title: Land fraction runs high and crust volume drifts mid-run
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: mantle
blocked_by: []
relates: []
refs: [planet/tectonics/earth.py, planet/tectonics/crust.py, tools/scorecard.py, "run:0f18a3", "run:fd1cfa"]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Land median is 34–36% (up to ~40% when assembled; Earth 29%; the envelope test allows 22–42%), and continental crust
volume drifts +2–5% mid-run: assembled continents have fewer subducting margins, and the volume
thermostat only partly compensates. The v1 notes had continental area at ~45% vs a 40% target.

## Updates
- 2026-10-15: Status in-progress -> todo. Tect2 (merged): rifted margins laid thicker when area is over target; area 41-42% -> 40-41%. Residual ~1-2 km thinning per Gyr remains.
- 2026-10-15: Status todo -> in-progress. Worktree tect2.
- 2026-10-15: Status in-progress -> todo. Tectfound (merged): island arcs out of the volume thermostat, forearc gap, level-independent erosion, no welds at trenches, integral thermostat term. Crust 48.9/46.3% -> 42.7/42.0%. Residual: ~1-2 km thinning and +2-3 points area per Gyr (merged draft).
- 2026-10-15: Merged inbox draft draft-residual-crust-thinning.md ("Continents still thin ~1-2 km and gain ~2-3 points of area per Gyr", found by tectfound).
  Left over from the foundation round (PW-052/046). Mean continental crust is
  ~36 km over the first 500 Myr and ~34 km over the last 300 Myr of a 1 Gyr
  run, with crust area rising 40 -> 42-43% (L6 seeds 1/21/3199; L7 0f18a3,
  fd1cfa); at 2 Gyr (L6 seeds 1, 21) ~34-36 km and 40-44% (the old code:
  28-29 km, 49-50%). The area thermostat's integral term saturates late
  (THERMO_MAX), because subduction erosion can only act at ocean-continent
  trenches, which get scarce when plates are few.
  Per-step budget at L6, 700 Myr (old code, per step): resolve loses ~664
  continental cells and gains ~630 (plates moving over the grid); coherence
  welds ~141 and shreds ~104 (asymmetric: welds take any ocean cell ringed by
  continent, shreds only thin < 20 km continent), net +37, about the resolve
  loss; new continent from thickened island arcs ~23 (much less now that the
  volume thermostat only steers continental arcs), rifted margins ~21;
  subduction erosion removes ~35. A diagnostic script that books area per
  process is worth keeping as a tool (tools/churn.py style).
  To try: make coherence area-neutral on average (shred thick one-cell spits
  too, with their crust flowing to their continental neighbours, as welds do
  the other way), or let the area thermostat also steer the rifted-margin
  pool; check island arcs (one cell wide at L6) aren't shredded.
- 2026-10-15: Status todo -> in-progress. Foundation round, worktree tectfound.
- 2026-10-14: Migrated. Merged: 'Land runs high' (mantle), 'Continental area overshoots to about 45%' (v1 Also noted and Crust section).
