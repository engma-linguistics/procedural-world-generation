---
id: PW-1377
title: "Den peoples' raiding share: cap 0.3 and half-cap 5 /km2 are judgements, no measured share found"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: lane 136 / lane 137 (density ladder build)
blocked_by: []
relates: [PW-1275, PW-1350]
refs: ["planet/lineages/ladder.py::RAID_CAP", "planet/lineages/ladder.py::RAID_HALF", "planet/lineages/ladder.py::RAID_REACH", "planet/lineages/ladder.py::Ladder.settled_near", docs/review/peoples/density-ladder/build.md, "Opler 1941 An Apache Life-Way p. 332", "Encyclopedia of World Cultures 2008, Western Apache - Economy (secondary)", "Burckhardt 1831 Notes on the Bedouins and Wahabys vol. 1 pp. 71-72", "Khazanov 1994 Nomads and the Outside World pp. 155, 187, 221-222", "Hendrickson, Mearns & Armon 1996 IDS Bulletin 27(3) (abstract only)"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
Q4 A (PW-1350): goblins, kobolds and troglodytes live on the forager rung x kind 1.2, topped up by raiding: density = forager /
(1 - r), r = RAID_CAP x settled / (settled + RAID_HALF), settled = the farmers' and herders' density within RAID_REACH rings. Lane 136
looked for a measured share of food from raiding (sources in build.md, "Raiding") and found none: raiding is described as a top-up
("approaches hunting in economic significance", Opler; "an important supplementary means of livelihood", "too unreliable", Khazanov),
and the Western Apache's meat share (raided stock inside it) is ~35% (secondary). So RAID_CAP = 0.3 sits under that meat share and
RAID_HALF = 5 /km2 is a gardening-village country; both are judgements.

What would firm it up: an ethnography giving the share of a raiding people's food (or stock) taken in raids (Apache or Plains studies,
Turkana or Nuer cattle-raiding counts). If found, set the cap from it; until then the numbers stay marked as judgements.

## Updates
- 2026-11-02: Created from inbox draft draft-raid-share-unsourced.md (found by lane 136 / lane 137 (density ladder build)).
