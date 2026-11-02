---
id: PW-1379
title: Den peoples gain from raiding but their farming and herding neighbours lose nothing
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: lane 138 (density ladder sources round 2)
blocked_by: []
relates: [PW-1377, PW-1350, PW-1275]
refs: [docs/review/peoples/density-ladder/sources-round2.md, "planet/lineages/ladder.py::Ladder.line", "planet/lineages/ladder.py::Ladder.settled_near", "planet/lineages/ladder.py::RAID_CAP", "planet/lineages/ladder.py::RAID_HALF", "planet/lineages/ladder.py::RAID_REACH", "paper:Hendrickson1998", "paper:Glowacki2015", docs/review/peoples/density-ladder/build.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: goblins, kobolds and troglodytes get up to 30% more food from raiding the farmers and herders near them, but
those farmers and herders lose nothing for it. The one area number found for raiding goes the other way: in 1982-84, 47% of
Turkana district in Kenya, including much of the best grazing, stood virtually unused because of the threat of raids (a 1985
study, quoted in the ENN summary of Hendrickson, Armon & Mearns 1998). Raided stock also went to bridewealth and trade rather than
food (Glowacki & Wrangham 2015; the NPS Gila Cliff Dwellings history for Apache stock).

Where: `Ladder.line` adds the raid share to a den people's density from `Ladder.settled_near` (farmers' and herders' density within
RAID_REACH 2 rings); nothing feeds back on the victims' density.

Options:
- A: leave it. The raid share is small (r <= 0.3 on a forager-rung people at ~0.06-0.9 per km²), so the victims' loss in people
  would be tiny anyway; the effect worth having is on land use, not numbers.
- B: within RAID_REACH of a den people, lower the farmed and herded share of a cell by a small factor that grows with the den
  people's presence (a buffer zone of half-used land), with the factor a stated judgement until a source is read.
- C: fold it into the later tech-tree / polity work (raiding as a relation between peoples), not the ladder.

Lean: A for now, C when peoples' relations exist. A number for B would need the Turkana raid series (Schilling et al. 2012,
McCabe 2004, on `docs/references/wishlist.md`).

## Updates
- 2026-11-02: Coordinator: A now (leave), C later: fold into relations between peoples (polities v0/v1).
- 2026-11-02: Created from inbox draft draft-raiders-thin-their-neighbours.md (found by lane 138 (density ladder sources round 2)).
