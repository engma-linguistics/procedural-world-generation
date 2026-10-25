---
id: PW-869
title: Peoples are static in closed country until the Holocene; late arrivals into a held country stay at a few dozen cells (elves 43-120 cells on 5 of 8 tries)
type: task
status: done
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
- 2026-10-25: Status todo -> done. Merged fun lane 27: pioneer advantage and rafts from 100 kyr; elves >=500 cells 8/8, half-elves 8/8. The pre-Holocene humans on the small continent went to a new ticket (see intake).
- 2026-10-25: Status needs-decision -> todo. RULING (coordinator): B, plus fix pre-Holocene dispersal by mechanism. Real humans crossed to Sahul by sea at least ~50-65 kyr ago and spread through held country (Neanderthals and Denisovans) within ~10-20 kyr, so a craft ladder that only starts at 6-10 kyr ago and ranges that stay static until the Holocene both contradict the record. Give boat use a realistic early rung for coastal and island-hopping peoples, and give expansive peoples a way to press into held country, measured against out-of-Africa timings. Bounded: don't recalibrate the whole history.
- 2026-10-25: Created from inbox draft draft-newcomers-stay-small-on-crowded-countries.md (found by fun-lane-26).
- 2026-10-25: (fun-lane-27) Part B and the early boat rung done; the checkbox met, the humans' pre-Holocene static range not fixed (draft draft-humans-stay-small-on-a-held-continent-before-the-holocene.md). Mechanism: `history.pioneer_factors` (a newcomer feels PIONEER_Q = 0.5 less competition ramping back over PIONEER_KYR = 8 kyr, and its founders are not displaced meanwhile; an expansive people, explore from 0.4, with a small share of its K >= 0.3 country filled feels up to EXPANSE_PRESS = 0.6 x expansiveness x unfilled share less) and a first craft rung (`spec.RAFT_KYR` = 100 kyr ago, 120 km, sea share 0.1, no animals). Measured on 2a7385, dnd, seeds 7000-7007, one try each: elves 850-2980 cells (>= 500) on 8 of 8 (baseline 3 of 8: 43-1693), half-elves on 8 of 8 (start 20 kyr ago; 564-3498 cells); the founding window alone (pressing off) gave elves >= 500 on 2 of 8, so the press is what carries it. Humans: on the big continent they hold 13-20k cells within 100 kyr of their origin and 36-43k at the present; when their origin falls on the small continent (7000, 7005, 7006) they sit at 1.1-3k cells until the farmers (4-12k at the present), unchanged by the change; they first reach the other big continent at 2.5-5.9 kyr ago (planked boats: the gap is ~1000-2300 km of open sea; the raft and canoes make the island hops: Munin, 662 km, at 54-64 kyr ago, Loshom 361 km).
