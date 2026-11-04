---
id: PW-1166
title: Droughts cut the food the land gives (famine) and send peoples to rivers and herders into farmland, instead of only moving their comfort window
type: task
status: todo
parent: PW-917
milestone: later
subsystem: peoples
effort: m
impact: med
found_by: lane-82
blocked_by: []
relates: [PW-917, PW-661, PW-1108]
refs: [planet/lineages/recent.py, planet/lineages/history/habitat.py, planet/lineages/prey.py, docs/review/peoples-counterpressures/design.md]
created: 2026-10-30
updated: 2026-11-03
---

## Description
**In plain words.** Today a drought only shifts where a people is comfortable. Its fields and herds give as much food as ever, so a
people just thins out at its dry edge and fills back in afterwards. Nobody moves. In the real 4,200-year-ago drought, farmers left the
rain-fed plains for the river banks and springs, and herders pushed down the Euphrates into the cities' farmland (Weiss 2016).

The fix:
- **Food.** In a drought, the land gives less: rain-fed farmers and herders lose in proportion to the rain, foragers half as much,
  fishers and river farmers little.
- **Moving.** Peoples are drawn toward rivers and lakes nearby, and herders get an edge against the farmers in their way.

Design: docs/review/peoples-counterpressures/design.md, section (d). Depends on draft-counterpressure-plug, and matters only once
draft-recent-droughts-earthlike-rate makes droughts common enough.
- **K cut.** On drought cells, K x (rain / rain_ref)^e_way: e = 1 for rain-fed farmers and pastoralists, 0.5 for foragers, 0.2 for
  fishers and river farmers (judgements).
- **River pull.** A temporary habitat pull toward river, lake and spring cells within ~300 km (Weiss: "riparian, paludal and karstic
  refugia").
- **Herders' edge.** Pastoral peoples under drought take the momentum edge's contest bonus against farmers (the Amorites).
- **Size check.** Famine-scale losses are 10-15% (Great Famine of 1315-1317, southern England; Wikipedia citing the New Cambridge
  Medieval History).

- [ ] productivity cut by rain deficit per way of life
- [ ] habitat tracking to refugia; pastoral push
- [ ] lost.famine reported; settlements' "drought" abandonments line up with it

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: war, plague, events and life-history belong with the v3 civilization epic (PW-661); not needed for a first culinary brief
- 2026-10-30: Created from inbox draft draft-drought-famine-and-habitat-tracking.md (found by lane-82).
