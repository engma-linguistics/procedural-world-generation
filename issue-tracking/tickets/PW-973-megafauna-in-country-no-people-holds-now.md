---
id: PW-973
title: Megafauna in country no people holds now sit at their natural density - 2.5x the dragons, 3.8x the giants per world
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-41
blocked_by: []
relates: [PW-957, PW-963, PW-966, PW-967]
refs: [planet/lineages/history/megafauna.py, planet/lineages/prey.py, docs/review/megafauna/age-of-dragons.html]
created: 2026-10-28
updated: 2026-10-28
---

## Description
Since PW-957/PW-963 (fun lane 41), a megafauna kind sits at the user value (meta.dragon_km2, meta.giant_km2) where peoples press it. Where no people does, it sits at its natural density. The 6 planets x 4 dnd rolls (7000-7003) sweep at the defaults (prey / base / schedule) gives these present counts per run:

| | main | branch |
|---|---|---|
| dragons | 7.0k | 17.6k |
| giants | 1.8k | 6.7k |

- In peopled country the realised density holds at the user value: dragons ~1 per 4,800-5,200 km2.
- The rise comes from country no people holds:
  - deserts. Blue dragons on 1df1c3/7000 run at 1 per 280 km2 in their wild country and 1 per 663 overall, 19,742 of them. The model's deserts are prey-rich: see the prey-fit draft, where the desert grazing NPP gives ~1.9 t/km2;
  - tundra. Frost giants run at ~1 per 350-390 km2.
- The owner's ruling on PW-963 was "players should not find far more giants than they expect, or flocks of dragons". A party crossing a wild desert would now meet a blue dragon every ~17 km.

Options:
- **A.** Keep it: this is the age of dragons surviving where no people lives, which is the design. Fix only the desert prey (prey-fit draft), which brings the blue dragons down most.
- **B.** Cap the wild country's density at a multiple of the user value (e.g. 5x).
- **C.** Count peoples' reach (raids, patrols, adventurers) beyond their held cells: smooth the pressure a few hundred km out, so wild country next to peoples is partly pressed.

Lean: A plus C, decided on the PW-967 review page. C is persecution by mobile adventurers, a mechanism; B is a clamp.

## Updates
- 2026-10-28: Created from inbox draft draft-megafauna-unpeopled-country-counts.md (found by fun-lane-41).
