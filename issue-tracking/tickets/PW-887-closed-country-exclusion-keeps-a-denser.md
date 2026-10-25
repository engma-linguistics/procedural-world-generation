---
id: PW-887
title: Closed-country exclusion keeps a denser newcomer (humans, 10 per km2) boxed in by 13-15 thinner incumbents on a shared continent; pick the mechanism or accept the niche
type: task
status: done
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-28
blocked_by: []
relates: [PW-885, PW-869]
refs: [planet/lineages/history.py, planet/lineages/spread.py, "world 2a7385", "dnd tries 7000, 7005, 7006"]
created: 2026-10-25
updated: 2026-10-25
---

## Description
PW-885 (fun lane 28) measured why humans stay at 1.8k cells on landmass 1 of 2a7385 (tries 7000, 7005, 7006). At 100 kyr ago, of the 568 unheld cells next to their range, 538 have K >= EST and are all held by other peoples (orc, hobgoblin, leonin, bugbear, lizardfolk, tabaxi, halfling...; 13-15 peoples); none is empty and only ~30 are outside the niche. The load on a frontier cell is q ~1.07 (median) against K ~0.81, so room = K - q x qm is ~0.01 even with the expansive press (qm 0.73); inside their range q is 0.47. The exclusion is the closed-country alpha_eff > 1 summed over many rivals (bistable: first holder wins). Raising EXPANSE_PRESS (ticket) or EXPANSE_FILL (lane 28) did not move it. Humans are the densest line there (10 per km2 against 0.5-5 for the incumbents, halfling 12); `DENSITY_PUSH` (0.1, clip 0.7-1.4) is the existing density term, and a stronger one cost the elves/orcs in an earlier lane.

Options:
- A. Accept it as the niche/tree (the continent holds only ~4.2k suitable human cells anyway, so 8k cells needs the sea, which opens at 58 kyr and with the planked boat). Close PW-885 as a tree question.
- B. A frontier-invasion term: a newcomer's pressure at the contact line scales with its density advantage over the incumbent (sum the rivals by people-weighted load, not presence), so a denser people takes a thinner people's cells only along the front. Needs a multi-seed check on the elves/orcs (>= 500 cells on 7 of 8).
- C. Let the incumbents' claim fade where they hold below their own viable population in a patch (the MVP fade for non-separate patches).
Lean: B, behind a seed sweep; A if the owner prefers the tree to say it.
- [ ] humans on landmass 1 reach their whole niche (~4k cells) within 30 kyr of their origin on 3 of 3 tries without the elves dropping under 500 cells on 7 of 8

## Updates
- 2026-10-25: Status todo -> done. Built in fun lane 29 (6e66244): front term INVADE 0.5 floor 0.3, crowding drive. Small-continent humans fill the ~4k-cell niche; the 8k line is sea-limited.
- 2026-10-25: (fun-lane-29) Option B built, plus the owner's crowding drive: `history.invasion_weights` (on the cells touching its range, a rival thinner than one weighs exp(-0.5 x ln density ratio), floor 0.3; every people by the same rule) and `history.crowding` (the share of held habitat rivals take drives the crossing rate x (1 + 2 crowd), within the craft, and the entry into poor country). Measured on 2a7385, dnd, seeds 7000-7007: humans on the small continent 1.8k -> 3.5k at 100 kyr ago, 4.1k at 40, 5.1k at 20 (the continent holds ~4.2k suitable cells), 10.5-13.2k at the present (9.3-12.3k); the big-continent tries 17-24k at 100 kyr (13-21k). Elves 721-3221 cells on 8 of 8 (>= 500), half-elves 8 of 8. The crowding drive alone is small here (v1 invasion-only and v2 differ by under 5%); the front term carries it. Cost: hobgoblins at the present fall to 82-141 cells on 7000/7005/7006 (209-484 before), elves on 7003 2765 -> 814. Status left.
- 2026-10-25: Status needs-decision -> todo. RULING (coordinator): B, a frontier-invasion term. A denser people takes a thinner people's cells along the contact line; this is the modern-human vs Neanderthal replacement mechanism (a small demographic advantage at the front, e.g. Banks et al. 2008, Kolodny & Feldman 2017). Not ruled: A, accepting it, because the owner expects humans to spread like the record. Check over 8 seeds: elves >= 500 on 7 of 8, half-elves still appear, orcs and the other incumbents keep viable ranges.
- 2026-10-25: Created from inbox draft draft-incumbent-exclusion-vs-denser-newcomer.md (found by fun-lane-28).
