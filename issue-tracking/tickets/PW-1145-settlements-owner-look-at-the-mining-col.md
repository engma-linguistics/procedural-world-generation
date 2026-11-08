---
id: PW-1145
title: "Settlements: owner look at the mining colonies and the 'mining follows need' rule (D12)"
type: task
status: needs-decision
parent: PW-856
milestone: later
subsystem: culture
effort: xs
impact: low
found_by: fun-lane-72
blocked_by: []
relates: [PW-1131, PW-1116]
refs: [planet/lineages/settlements.py, viewer/globe/settlements.js, docs/review/settlements/README.md, "run 488d7e", "run 570701"]
created: 2026-10-30
updated: 2026-11-03
---

## Description
In plain words. Dwarves, kobolds, gnomes and drow now find ore. Each of these peoples sends miners to the ore
districts within about 300 km of its own country, even where humans or halflings farm the land, and works them as a
mining town of incomers. Every other people opens mines only when it wants what they give:
- farmers and herders who need metal tools and salt,
- a town or city nearby to sell to,
- or, slowly, from seeing a neighbour's mine (after about 1,000 years of it).
A people that learns copper smelting also waits about 1,000 years, more or less, before opening ore mines of its own.
Each diamond on the globe is a mining district (the pits and mining town of one seam), not a single pit. That is why a
world has only 280-410 of them.

To see it: Overlays > Settlements > "only the mines". Or these links (the cell under the pointer is a colony):
- dwarves, gold: http://localhost:8765/viewer/?run=488d7e&settle=mines&layer=peoples&lat=39.77&lon=75.096&dist=2.3
- kobolds, gold: http://localhost:8765/viewer/?run=570701&settle=mines&layer=peoples&lat=32.445&lon=118.717&dist=2.3
- gnomes, iron: http://localhost:8765/viewer/?run=488d7e&settle=mines&layer=peoples&lat=3.045&lon=145.776&dist=2.3

Judgement calls (CONST in settlements.py; `planet settlements RUN --set K=V` tries another value):
- A. How far a colony reaches (COLONY_KM 300; at 500 km dwarves get up to 26 a run, kobolds up to 80).
- B. Which deposits colonies take (COLONY_ORE 0.5, any ore district; at 0.75, the rich ones only, dwarves get 0-5).
- C. How much farming makes a people want metal (MINE_NEED 0.3 of its people farming or herding), and the lag after
  smelting (1 kyr median). No source gives a number for either.
- D. Dwarves stay few (4-18 districts a run) because the dwarves themselves are few. Making them more is a history
  question (see the companion draft on miners leaning to rich ore).
Lean: keep as is.
- [ ] Owner looks at the links

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: settlement mining-colony check; not a must-have
- 2026-10-30: Created from inbox draft draft-mining-colonies-owner-look.md (found by fun-lane-72).
