---
id: PW-612
title: "Mature start: what still moves early (the breakup's erosion dip, sediment that keeps piling up, a little crust volume)"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: surface
effort: m
impact: low
found_by: base-climate-laneB3
blocked_by: []
relates: [PW-558, PW-576, PW-559, PW-549, PW-649]
refs: [planet/tectonics/setup.py, docs/review/base-climate/thermostat.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
The made-up start's low relief (the original subject of this draft) is fixed on branch
worktree-agent-a6839a8fda5489c3d. setup.py now gives the continents the run's own long-run thickness distribution and
sediment cover (thermostat.md, Stage 3). The ice-free land's erosion now starts at ~0.9× its 300-1000 Myr mean (was
0.25× until ~150 Myr). What still moves early or late:
- **A dip to ~0.7× at 50-150 Myr.** The starting belts wear down before the first collisions (~150 Myr) while the
  first breakup's highstand (+170-270 m at ~90 Myr) floods the lowlands. It is within the late runs' range
  (single windows 0.62-0.72), so it's probably the supercontinent's breakup phase, not spin-up. Only 3-6/10 seeds
  are within 20% at 50-150 Myr.
- **Sediment keeps piling up through the whole run**, on both starts: land cover 1.4× and sea-floor cover 1.2× their
  300-1000 Myr means by 1 Gyr. There's no steady state to start from. The sea floor starts with no sediment.
- **Crust volume end/start in the scorecard**: x0.981 and x0.949 (seeds 1 and 2), against x0.995 and x1.021 on main (5c4c0fd era); after landing on 82e759f, x0.968 and x0.939 against main 964a132's x0.988 and x0.966.
  The start has thin margins at the 21 km floor and more sediment, which the volume thermostat (PW-046) may lose
  faster.
- [ ] decide whether the breakup dip needs anything (it may be the planet's own history)
- [ ] check the volume ratio on more seeds; if it's the start's margins, look at subduction erosion of thin crust

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-23: Created from inbox draft draft-relief-spinup-erosion-rise.md (found by base-climate-laneB3).
