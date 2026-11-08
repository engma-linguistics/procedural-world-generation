---
title: "Sea branch: merfolk reach reef towns but rarely vent metal or records; sea peoples still 10-19 kyr behind on the world clock"
type: task
status: todo
parent: PW-661
milestone: later
subsystem: culture
effort: s
impact: low
found_by: lane-207
blocked_by: []
relates: [PW-1490]
refs: [docs/review/culture/techtree/round3.md, docs/review/culture/techtree/round3/lag.py, planet/lineages/samples/techtree.toml, "planet/lineages/land.py::_sea_goods", "planet/lineages/techtree.py::is_sea", "planet/lineages/techtree.py::rate_of", "runs 07c755 0141d1 3e0eb4"]
---

## Description
**In plain words.** (Follow-up to PW-1491, which this branch does not hold yet.) The sea peoples now have a ladder of their own. On Seven Meals (07c755) the merfolk reach reef towns in 6 of 8
draws, but vent smelting comes in only 3 of 8 draws and records and script in 1 of 8. On the D&D world (0141d1, 3e0eb4) the storm
giants hold about 5 of the 16 sea techs, because their country has few vents and kelp beds. On the world clock (spread1's "years
behind") the merfolk went from 23,300 to 19,100 years behind and the storm giants from 11,400 to 10,600. The baseline is main at
faa4fb8c.

**What misleads if never done.** A viewer reader comparing peoples sees sea peoples as stone-age even when they hold reef towns. The
world clock counts techs, so a 16-tech branch can never close the gap. The clock either needs a per-ladder reading or the branch
needs its upper rungs.

**Likely causes (not tuned, by the brief):**
- the soft techs' rates are set for a 10-million anchor people (techtree.rate_of), while the merfolk are small;
- vents count only at today's ridges (res_vms at sea);
- the incised-shell script waits for reef towns and shell tallies, both slow.

- [ ] Decide whether "behind" for a people with its own branch should be read on its own ladder (rung reached).
- [ ] If the upper rungs should come more often: check the pool (S) of the sea peoples against the anchor before touching rates.
