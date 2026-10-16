---
id: PW-046
title: Land fraction runs high and crust volume drifts mid-run
type: task
status: done
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: mantle
blocked_by: []
relates: []
refs: [planet/tectonics/earth.py, planet/tectonics/crust.py, tools/scorecard.py, "run:0f18a3", "run:fd1cfa", docs/review/health/2026-10-15/report.md, tools/health.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
Land median is 34–36% (up to ~40% when assembled; Earth 29%; the envelope test allows 22–42%), and continental crust
volume drifts +2–5% mid-run: assembled continents have fewer subducting margins, and the volume
thermostat only partly compensates. The v1 notes had continental area at ~45% vs a 40% target.

## Updates
- 2026-10-16: Status in-progress -> done. Done (ba5d976): setup starts continents at continental_thickness (were ~37 km vs 35), stacked crust spreads beyond its own plate before MAX_KM deletes it, cleanup_ghosts stacks hidden crust instead of deleting it. Scorecard seeds 1/2, 1 Gyr volume x0.905/0.873 -> x0.977/0.981; L6 health 0.895 -> 0.963. Coordinator: residual 2-4% (thermostat lag behind real sinks) accepted; closed.
- 2026-10-16: Tectonics night lane (2026-10-16, docs/review/audit/tectonics-night.md): three causes fixed. (1) setup laid the continents at ~37 km against the thermostat's 35 km target (start 6% over), so every run shed 6% and the integral term wound up (thermo[0] -0.09 at 300 Myr, negative until ~750 Myr), holding arcs back while volume fell below target; setup now shifts the start to continental_thickness. (2) collision stacking could only spread into its own plate, so front cells hit MAX_KM and the cap deleted the excess (seed 2: -7.6k of -19.4k km-cells over 1 Gyr); belts now straddle the suture (crust.inner_edges). (3) cleanup_ghosts deleted continental crust hidden under a continent; now stacked (~0.5%/Gyr). Volume end/start: health 8 L6 seeds 500 Myr 0.867-0.916 -> 0.939-0.988 (mean 0.895 -> 0.963); scorecard 1 Gyr seeds 1/2 x0.905/x0.873 -> x0.977/x0.981. Remaining ~2-4% below target is the PI thermostat's lag against real sinks (subduction erosion steered by area -42k, sediment onto ocean floor -27k vs arcs +41k km-cells per Gyr, seed 2); resolve+collision net -6..-8k per Gyr is nearest-cell multiplicity (duplicated world cells each get the physics, one write survives), not a leak. Judgement: accept the lag (no stronger thermostat) and close?
- 2026-10-16: Status todo -> in-progress. Tectonics run-lane agent started.
- 2026-10-15: Merged inbox draft draft-health-pw046-volume.md ("PW-046 update: continental crust volume falls 3-8% over 1 Gyr on all 11 sweep runs; land and crust area now on target", found by health-sweep).
  Update for PW-046. PW-246 health sweep (2026-10-15, main 6926583, 8 L6 + 3 L7 seeds, 1 Gyr): the
  land and area part of this ticket looks settled, the volume part has turned into a slow loss.
  - land: seed medians 30.8-31.5% at L6, 32.2-32.3% at L7 (Earth 29%); maxima 37.7-38.7% when assembled.
  - continental crust area: medians 39.4-40.2% (L6), 38.8-39.0% (L7); ranges 35-44%.
  - mean continental thickness: medians 33.9-34.9 km (L6), 34.9-35.9 km (L7); target 35 (PW-238).
  - continental crust volume (sum of thickness over continental cells), end / start: L6 0.918 (seed 11),
    0.925 (77, 3199), 0.934-0.936 (42, 505, 1), 0.955 (2), 0.974 (21); L7 0.933 (3199), 0.950 (21),
    0.958 (11). Every run loses 3-8%, none gains (the ticket's mid-run +2-5% drift is gone).
  Whether a slow loss is wanted is a judgement call (Earth's continental volume is thought roughly
  steady or slowly growing over the last Gyr); the volume thermostat could aim at the starting volume.
  If that's accepted, PW-046 can close.
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
