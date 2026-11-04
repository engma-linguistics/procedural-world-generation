---
id: PW-1449
title: "Polities: 25 polities over 1 Mkm² at once, about ten times history's (state reach is too long)"
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane-175
blocked_by: []
relates: [PW-1431, PW-1432]
refs: ["planet/lineages/polities.py::_reach", "planet/lineages/polities.py::STATE_KM", "planet/lineages/polities.py::DISTANCE_X", docs/review/culture/polities/round2.md, docs/review/culture/polities/round1.md, docs/review/cultures-proposal/proposal.md, "docs/review/cultures-proposal/proposal.md#212-formation-growth-and-reach", "run 3c1caf", "run a2b637"]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** On the Seven Meals showcase (3c1caf), 25 polities are bigger than 1 million km² at the present. On the D&D run
(a2b637) there are 14. History had about 2-3 at a time. Turchin 2009 counts 60+ empires of 1 Mkm² or more between 3000 BCE and 1800
CE (via `proposal.md` 2.1.2); if each lasted about 200 years, that is 2-3 at once (my arithmetic, not his figure). If this is never
fixed, ordinary states look like empires on the Polities layer. The real empires (the ones war builds, up to 3-5 Mkm²) hardly stand
out, and a campaign map has two dozen Rome-sized neighbours.

The cause is reach, not war: war v0 (lane 175) left the count unchanged (25 before, 25 after). A state with law, a distance tech,
riding and roads gets 150 x 4/3 x 2 = 400 foot-km, and each km costs 1/1.5 x 1/1.5. That is about 900 km of real travel, or
~2.5 Mkm² if the land is open. The median state at the present is 0.9-1.2 Mkm² on 3c1caf. The multipliers for law, distance, riding
and roads are all judgement calls (round 1).

What I would try:
- Read Spencer 2010's 50-250 km as the reach of a state *with* its usual techs. Make the multipliers smaller (or stop them
  stacking), so a typical state is 0.05-0.3 Mkm² and only the conquest-built empires pass 1 Mkm².
- Check the count over 1 Mkm² per century against the 2-3 above, and the largest against Taagepera's 2.3-5.5 Mkm² band (round 2
  measures both).
- [ ] polities over 1 Mkm² at the present: under ~8 on 3c1caf and a2b637; the largest still inside 2.3-5.5 Mkm² on 3c1caf

## Updates
- 2026-11-04: Created from inbox draft draft-polities-too-many-giant-states.md (found by lane-175).
