---
id: PW-974
title: Read lineages.prey.productivity into people density (way-of-life factor x f(absolute NPP))
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-41
blocked_by: []
relates: [PW-833, PW-966, PW-964]
refs: [planet/lineages/prey.py, planet/lineages/history/megafauna.py, planet/lineages/history/model.py]
created: 2026-10-28
updated: 2026-10-28
---

## Description
PW-966 built the shared productivity base. `planet/lineages/prey.py` makes a static wild-prey field per cell from the world's grazing NPP. `productivity()` returns that field over its land median. `History` holds it as `prey_wild` and `prey_prod` (made in `history.megafauna.setup`) whenever megafauna are in the tree.

Only the giants read it so far, under `meta.megafauna_natural = "prey"`. People density still uses each line's fixed `density`.

PW-833's ruling: people density = way-of-life factor x f(absolute NPP).

What is left:
- Make `prey_prod` whether or not there are megafauna. Today `setup` skips it for a tree without them.
- Multiply a people's density per cell by f. Two ways to do it:
  - **A.** Scale the habitat K.
  - **B.** Use a per-cell density through `dens_at`, as the megafauna do.
- Keep each way of life's mean density where it is, so the per-people pass and the PW-964 remnants don't move all at once.
- Note that grazing NPP undercounts forest foragers: their food is mast, fish and game, not grass. f may want the `foraging` layer, or the total NPP, for foragers, and grazing for herders.
- Run the 6 x 4 dnd sweep (rolls 7000-7003) against main.

## Updates
- 2026-10-28: Created from inbox draft draft-people-density-reads-productivity.md (found by fun-lane-41).
