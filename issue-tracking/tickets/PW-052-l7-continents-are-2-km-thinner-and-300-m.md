---
id: PW-052
title: L7 continents are ~2 km thinner and ~300 m lower than at L6
type: task
status: done
parent: null
subsystem: tectonics
effort: m
impact: high
found_by: l7jumps
blocked_by: []
relates: [PW-053]
refs: ["run 1beb32", "run 98adcb", "run fe7144", docs/review/overnight_runs.md, planet/surface.py, planet/tectonics/crust.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Median continental crust is 33 km at L7 vs 35 km at L6, so continents sit ~300 m lower; twice as much land
lies within 100 m of sea level and land is ~2× as sensitive to sea level. L7 also has ~3× as many small
continental specks. Cause not found: check erosion and the thermostat's scaling with resolution
(per-cell rates, diffusion lengths). Level 7 is now the showcase default, so this matters.

Related observation (owner, 2026-10-14): at L6 continents match Earth (largest 20–24% of the surface vs
Earth's 15.5%; 3–4 landmasses over 0.5% vs Earth's 4) and the owner is satisfied; L7 being more
fragmented ties to this issue.

## Updates
- 2026-10-15: Status in-progress -> done. Merged (tectfound): setup.py coast-distance search capped at 50 cells made big L7 interiors start as coast; fixed. L6 vs L7 now match (seed 21: 35.7 vs 35.9 km median; seed 3199: 36.0 vs 37.2).
- 2026-10-15: Status todo -> in-progress. Foundation round, worktree tectfound.
- 2026-10-14: PW-169 (owner, 2026-10-14): the coherence fix (PW-108) thinned continents and lowered land 2-6 points; retune the continental targets as part of this ticket rather than weakening coherence.
- 2026-10-14: Added the owner's continent-size check (L6 matches Earth; L7 more fragmented).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Crust and continents and morning_report biggest problem 4.
