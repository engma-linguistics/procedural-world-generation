---
title: Hill, cloud and frost giants never reach most of their core country (out of a walker's reach); peoples still press megafauna at full strength
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-38
blocked_by: []
relates: [PW-936, PW-924]
refs: [planet/lineages/history/megafauna.py, planet/lineages/history/model.py, "world 2a7385, dnd 7001"]
---

## Description
Fun lane 38 diagnosis (2a7385 dnd 7001, per-kind tracking of core-country patches: in scatter reach, ever held, lost by K / competition / viable fade).

After the metapopulation fix (megafauna.metapop_km: pockets within scatter reach are one population for the fade), 12/15 kinds reach >= 0.5 of
their core country (was 7). The three still short are walkers whose country lies mostly out of reach: hill giants 0.11 (ever in reach 0.16),
cloud giants 0.16 (0.19), frost giants 0.43 (0.68). Nothing faded them; their scatter (5 x 800 km, sea at 2x cost) never got there.
Options:
- A: count only the country a kind could reach (from its origin landmasses by its own mobility) in `suitable_reached`. Changes the target.
- B: give walkers' scatter the line's crossing craft over water (crossing.modes, as History._jump). Giants have only the raft, so this needs a sea trait on giants.
- C: accept: giants are absent from far continents (the owner's 800 km walk).
Lean: C for the v2 target (13/15 met with fire and storm giants), A if the owner wants the metric to say so.

Second finding: the peoples press megafauna at their full niche overlap (only the reverse is cut by MEGAFAUNA_PUSH). Cutting it both ways
(variant tested) takes the target to 13/15 and nearly every dragon kind to >= 0.93, but counts jump 3-40x (gold 210 -> 1,566, red 61 -> 925,
hill giants 2,400 -> 11,400) and elves fell 757 -> 222 cells on that roll. Not merged: it breaks the owner's "a few hundred of each kind" at
1 per 5,000 km2. If wanted, it needs a density re-trial (PW-923).
- [ ] owner picks A/B/C for walkers
- [ ] decide whether peoples should press megafauna less (with a re-trial of densities)
