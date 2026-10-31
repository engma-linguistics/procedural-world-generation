---
title: "One-spot founding strands the kobolds: a split of the worldwide dragon stem lands on a landmass with little of its country"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: highlights
effort: m
impact: high
found_by: lane83
blocked_by: []
relates: [PW-1152, PW-1181, PW-1174]  # (and PW-1202, on main after this branch's base)
refs: [planet/lineages/history/origins.py, docs/review/peoples-d20/report.md, "world 4360a3"]
---

## Description
**In plain words:** since founding happens at one spot (your ruling D20 (2)), the kobolds nearly vanish. In the full dnd tree they fall
from 6–9% of all people to 0.05–5%; in the three-people tree (humans, goblins, kobolds) from 17–21% to 0.3%. They start at one spot
in the dragons' worldwide range, often on a landmass with little kobold country. They can't cross the sea, so they stay small for
350 kyr, and when the humans arrive they take most of what the kobolds have. Before, the kobolds inherited every scattered piece of
the dragons' range, so they were everywhere from the start.

Measured (lane 83, 4360a3, dnd3, seed 7, one try):
- The kobolds are founded 350 kyr ago on landmass 2. It has 334 of their 2004 good cells (habitat ≥ 0.3); landmass 5 has 867.
- They hold 152 cells at founding and 96–137 through the next 150 kyr, with no rival anywhere: they never spread beyond it.
- Today they hold 54 cells of that landmass; humans hold 208 of its 334 good cells.

Why: in `_origin_split` the parent's range is the whole world, so every landmass scores. "Isolated part of the parent's range" weighs
×3, and `_by_landmass` draws a landmass by habitable area^SPECIES_AREA_Z, which gives small or poor landmasses a fair chance. The parent
is megafauna (flying dragons), so its range says nothing about where a walking people's country lies. Also, `explore` 0.3 and
`sea_share` 0.02 come from the dragon stem.

Options:
- A. For a split of a megafauna (or flying) stem, draw the landmass by the child's own habitat (founders its country would carry), not
  by the parent's range. That is PW-1152's "start from the founding spot" with a better spot.
- B. Draw every split's landmass by the founders its whole landmass would carry, not by area^z of the scored cells (PW-1202 A's
  re-weighting).
- C. Accept it: one-spot founding makes island peoples, and the kobolds are one of them in some seeds.

Lean: A, then judge on the suite. Without it, small trees stay human-only (dnd3 99% human).
