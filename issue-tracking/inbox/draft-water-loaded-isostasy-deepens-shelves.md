---
title: Water-loaded isostasy for drowned continent (PW-1287 A) is built but deepens the drowned margins by ~400 m and shrinks shelves; keep it off?
type: task
status: needs-decision
parent: null
milestone: v1.0
subsystem: tectonics
effort: s
impact: med
found_by: lane 292
blocked_by: []
relates: [PW-1287, PW-950]
refs: [docs/review/tectonics/l7-high-ground.md, "planet/tectonics/isostasy.py::elevation", "planet/tectonics/simulation.py::Simulation.wet", "planet/tectonics/earth.py::erode", "planet/tectonics/earth.py::continent_water", docs/review/tectonics/mountains/l7_high_ground.py, "runs 145d7f ea1b47 (lane292 scratch; deleted)", "runs 213321 2e1bc2 (lane288 scratch, main 5411930b; deleted)", "McKenzie 1978 EPSL 40:25"]
---

## Description
In plain words: under the sea, continental crust should float as if water, not air, sat on it. That is now built
(parameter `water_loaded`, default off, commit 5c55c21a), as the coordinator ruled for PW-1287 (option A). But it
makes drowned continent sit deeper, not shallower: a column with water on it sinks about 1.46 times as deep as one
with air on it (rho_m / (rho_m - rho_w); McKenzie 1978's water-loaded E0 is likewise larger). So it moves the
shelves away from Earth, the opposite of what PW-950 wants. If turned on without knowing this, shelves (already
~1% of the ocean against Earth's ~6%) shrink further.

Numbers (l7-high-ground.md section 6.2, L7 1 Gyr, medians 600-1000 Myr, against main 5411930b's runs 213321 /
2e1bc2): submerged continental median -1140 -> -1500 m (seed 1), -1050 -> -1440 m (seed 2); shelf share of ocean
1.03 -> 0.81%, 1.28 -> 0.96%; land 32.8 -> 33.0%, 34.0 -> 33.7% (no sea-level trouble). Lane 23 found the same at
L6 (PW-950 update 2026-10-28).

Options:
- A. Turn it on anyway: it is the correct isostasy and closes PW-1287's bookkeeping gap (sediment moved off a
  drowned shelf onto the ocean floor is lifted at the same rate on both); shelves get worse until PW-950's own fix
  (tapered necking, sediment wedges, wave-base planation) lands. Needs the paired judge first.
- B. Keep it off until PW-950's margin work lands, then turn both on together and judge them as one.
Lean: B.
- [ ] decision A or B
