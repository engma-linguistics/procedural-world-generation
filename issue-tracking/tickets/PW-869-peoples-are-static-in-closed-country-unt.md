---
id: PW-869
title: Peoples are static in closed country until the Holocene; late arrivals into a held country stay at a few dozen cells (elves 43-120 cells on 5 of 8 tries)
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-26
blocked_by: []
relates: [PW-861, PW-852]
refs: [planet/lineages/history.py, "world 2a7385", "dnd tries 7000-7007"]
created: 2026-10-25
updated: 2026-10-25
---

## Description
PW-861 (fun lane 26) found why humans do not behave like "a gas": in closed country the rivals' niche overlap plus the territorial extra (ALPHA_CLOSED) leaves a newcomer no room (room = K - competition), so a range is static until something relaxes it: the farmers' push and the late mixing (the last ~6 kyr), and a sea crossing needs boats (the craft ladder starts ~6-10 kyr ago), so before then a people neither pushes into held country nor crosses oceans. On 2a7385 (L7) the humans hold 2.4k cells at 30 kyr ago on the small continent in 3 of 8 tries (a continent where 25-39k cells are the other peoples') and 4 kyr of Holocene growth is all they get. The PW-861 fix (an arrival whose hybrid is wanted takes the freest country near its partner, `history.ARRIVAL_ROOM`; sea landings are pulled toward the partner coast, `PARTNER_PULL`) puts the elves next to the humans, so the half-elves now appear in 8 of 8 tries (3 of 4 before). The cost: an arrival squeezed into held country keeps what it can hold, and ends at 43-120 cells in 5 of 8 tries (1000-1700 in the other 3; 1138, 1352, 4148 and 2 in the 4 baseline tries before the fix).
Options: (A) leave it (fey arrivals are rare and insular; the half-elf needs only a frontier). (B) a newcomer's pioneer advantage: for a few kyr after it arrives the founders are protected from displacement (the `over` decline in `History.run`) and push into poor country as a pioneer (`enter`), so it settles a real range before the incumbents press back. (C) an arrival that finds no free room near the partner lands at the partner's coast in the nearest *free* pocket even farther (ARRIVAL_ROOM tier 4, up to 2.5 reaches), accepting a looser contact. Lean B, small; the owner's expectation ("humans are basically a gas") would otherwise need the pre-Holocene static ranges relaxed, a bigger physics call (a people's own growth in empty country is not the problem: the continent is full).
- [ ] elves hold at least ~500 cells on 7 of 8 tries of the dnd tree on 2a7385 with the half-elves still appearing

## Updates
- 2026-10-25: Status needs-decision -> todo. RULING (coordinator): B, plus fix pre-Holocene dispersal by mechanism. Real humans crossed to Sahul by sea at least ~50-65 kyr ago and spread through held country (Neanderthals and Denisovans) within ~10-20 kyr, so a craft ladder that only starts at 6-10 kyr ago and ranges that stay static until the Holocene both contradict the record. Give boat use a realistic early rung for coastal and island-hopping peoples, and give expansive peoples a way to press into held country, measured against out-of-Africa timings. Bounded: don't recalibrate the whole history.
- 2026-10-25: Created from inbox draft draft-newcomers-stay-small-on-crowded-countries.md (found by fun-lane-26).
