---
title: "Tech tree: region learners (D55) bring the dnd world's writing 4 kyr early; the anchor rates need re-setting for them"
type: task
status: needs-decision
parent: PW-661
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lane-200
blocked_by: []
relates: [PW-1471, PW-1461]
refs: ["planet/lineages/techtree.py::Calendar.learners", "planet/lineages/techtree.py::rate_of", planet/lineages/samples/techtree.toml, docs/review/culture/techtree/round1.md]
---

## Description
**In plain words.** Daniel's D55 said each region of a people should learn on its own. Lane 200 built that: each continent holding
a tenth or more of a people's land counts as its own learner. On the humans-only world it works. The humans alone reach chiefdoms,
cities and kingship in 7 of 8 draws; main's tree gets 1, 3 and 1 of 8 on the same history. But on the dnd world (run 0141d1, 12
draws) the world's first writing moves to 8,219 years ago. Main's tree gives 4,153 and Earth 5,300. The tree's invention rates were
tuned on the assumption that a people is one learner. With region learners on, a people on five continents gets about five times
the chances. So the switch (`[defaults] regions`) is off.

**Options.**
- **A: re-set the anchor for regions.** The anchor (Earth's first date = the first find among `anchor_peers` = 4 peoples) becomes
  the first find among Earth's regions. Raise anchor_peers (8-12, from Earth's independent origins: four for writing, about 11 for
  farming) and re-run anchor_check and the showcase dates. This is a re-tune of an existing judgement, with Earth's counts behind it.
- **B: regions share one pool.** The regions split the people's skill strength (S) instead of each taking ln of its own share. That
  is close to no regions for a big people, so it does little for humans alone.
- **C: keep regions off.** Humans alone stay stuck (chiefdoms 1/8).

**Lean: A.** It keeps D55's mechanism and fixes the number it broke. Check: the showcase's first writing stays within main's
12-draw range (2,797-4,795 on 0141d1), and humans alone get chiefdoms and cities in most draws.
