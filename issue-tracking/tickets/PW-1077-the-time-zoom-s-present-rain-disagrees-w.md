---
id: PW-1077
title: "The time zoom's present rain disagrees with its world's in places (70 mm against 570 mm): prey is read from one, habitats from the other"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: fun-lane-50
blocked_by: []
relates: [PW-1024, PW-966, PW-599]
refs: [planet/lineages/recent.py, planet/lineages/prey.py, docs/review/megafauna/open-niches/README.md]
created: 2026-10-30
updated: 2026-11-03
---

## Description
**In plain words.** The peoples simulation reads two different climates for the same moment. Prey, meaning the wild herds and the grazing they live on, comes from the finished world's rain. Habitats, meaning where peoples and dragons can live, come from the time zoom's own recomputed climate at the present. In most places the two agree: over land the log-rain correlation is 0.95. In some places they disagree badly. Those places look rich in prey but are a desert to everyone, so they show up as "rich land nobody holds".

Seen in lane 50's diagnosis (PW-1024), world 2a7385, roll 7000, current dnd tree:
- 843 land cells (1.4%) have world rain above 600 mm while the time zoom's present env rain is under 200 mm.
- On the "rich empty" cells (prey >= 3 t/km2, < 0.02 people/km2): world rain 319 / 571 / 1,037 mm (10th / 50th / 90th percentile), env rain 35 / 70 / 109 mm, temperatures nearly the same (19.3 against 19.1 C).
- 47% of the rich land no dragon kind can live in on 2a7385 has world rain over 3x env rain. On 1df1c3 and e71172 the share is 5-6%, about the land-wide share (4-5%).

Sources:
- `recent.Pass._rain_ref` loads `rain0` and `graze_npp` from the world.
- The steps' `env["precipitation"]` comes from the time zoom's climate (PW-599 `_climate`).
- `lineages.prey.wild` is built on `ps.graze_npp`.

What to try:
- Find why the recomputed present climate is so much drier in those cells: an orbit or ice state, the vegetation feedback the world has and the recompute lacks, or the frame chosen.
- Then either make the present's env rain match the world's at 0 kyr (anchor it), or build the static prey from the env rain at the present.

- [ ] cells where world and env rain differ more than 3x at the present: under ~1% of land on the 6 sweep worlds
- [ ] the rich empty class re-measured afterwards

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: peoples refinement or later mechanism (tuning, follow-ups), not needed for a first culinary brief
- 2026-10-30: Created from inbox draft draft-time-zoom-rain-vs-world-rain.md (found by fun-lane-50).
