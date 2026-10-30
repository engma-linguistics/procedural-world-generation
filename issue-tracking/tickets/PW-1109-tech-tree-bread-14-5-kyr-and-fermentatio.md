---
id: PW-1109
title: "Tech tree: bread (14.5 kyr) and fermentation (13 kyr) also miss the late-chain rate floor (late_kyr = 12), as villages did"
type: task
status: wontdo
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-60
blocked_by: []
relates: [PW-1011]
refs: [planet/lineages/techtree.py, planet/lineages/samples/techtree.toml]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The tech tree speeds up the short chain of recent inventions (villages up to writing) so that peoples climb it within thousands of years. It does this with a minimum invention rate (late_rate 0.12 per kyr) for techs no older than 12 kyr (late_kyr). Villages (14.5 kyr) missed that cutoff, so a people with huts and food storage waited about 30 kyr on average to get them. Lane 60 gave villages its own rate of 0.12.
- Paired check: 4 runs x 4 draws; dwarves got villages in 12 of 16 draws before, 16 of 16 after.
- With villages earlier, towns and cities come earlier too: elves had cities in 4 of 16 draws before, 9 of 16 after; orcs 6 -> 11; kenku 9 -> 13.

Bread (14.5 kyr) and fermentation (13 kyr) sit just past the same cutoff and stay slow.

Options:
- A: leave them (bread and brewing are not gates for anything the settlements read);
- B: give each its own rate of 0.12, like villages;
- C: move late_kyr to 15, which catches all three and any later addition.

Lean: C, but it shifts the dates of every people's bread and beer, so it is a call for the owner.

## Updates
- 2026-10-30: Status needs-decision -> wontdo. Owner 10-30: tech tree is a placeholder; superseded by the tech rework (catalogue + inventiveness model).
- 2026-10-30: Created from inbox draft draft-techtree-late-chain-cutoff.md (found by fun-lane-60).
