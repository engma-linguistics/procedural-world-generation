---
id: PW-1487
title: With live attitudes, the history's conquerors are almost never harsh (no razing winner on seeds 7 or 10)
type: task
status: needs-decision
parent: PW-661
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lane201b
blocked_by: []
relates: [PW-1465, PW-1481, PW-904]
refs: ["planet/lineages/history/polity_live.py::TOL_X", "planet/lineages/history/polity_live.py::LivePolities._fates", "planet/lineages/attitudes.py::temperament", docs/review/culture/polities/round10.md, "run cbf74f", "run 4bd35e", "run 51916e", "run 70cf9f"]
created: 2026-11-05
updated: 2026-11-05
---

## Description
**In plain words.** Conquest harshness now follows the winner's tolerance and aggression (PW-1481). A tolerant winner does keep the
peoples it takes. But the peoples who win wars on world 899985 are mostly tolerant ones, so a harsh conqueror (your "Genghis Khan
razing cities") almost never shows up. Seed 7 (run cbf74f): winners with tolerance of 0.6 or more kept all 118 of the peoples on land
they took. Winners under 0.4 met 6 peoples: they thinned 2 and expelled 1, and the expulsion cost 28 heads. Conquest cost 2,745 heads
in all. Main with the switch on, same world and seed (run 51916e), lost 19,571. On seed 10 (run 4bd35e) conquest cost more than main
(44,444 heads against 24,865 on run 70cf9f). Its winners of 0.6 or more again kept all 33. The 5 thinnings came from winners under
0.6, and nothing was expelled. One winner was both intolerant and aggressive: the orcs 500 years ago (tolerance 0.36, aggression 0.60).
They thinned the leonins and hobgoblins they took; they did not expel them.
Seven Meals, seed 7 (run 647e2f against main 0ea92b), is the exception: its intolerant winners (under 0.4) thinned 34 of the 64
peoples they met, for 906,832 heads. In all it lost 977,787 heads against 606,663 on main.

Why: the conquering peoples (humans 0.72, tabaxi 0.78 to start) are tolerant. The walk also drifts conquerors up. The orcs start at
0.5, but their wars on seed 7 came at tolerance 0.58-0.74 (contact +0.05, ruling many peoples +0.05, plus each people's own offset and
drift). TOL_X = 2 then takes up to 1 off the harshness of a tolerant winner.

**What misleads if never done.** With the switch on, the v4 card will say almost every conquest "kept" its peoples. That reads as a
peaceful world, but it comes from two judgement numbers: TOL_X, and the temperaments' bases.

**Options.**
- A. Keep (TOL_X 2): tolerance rules; harsh fates are rare and come only from the intolerant peoples (elves, dwarves, drow, firbolgs).
- B. TOL_X 1: tolerance moves the harshness by at most 0.5 either way. The enmity counts for more, so old enemies are thinned even by a
  tolerant winner.
- C. Let aggression raise the harshness too, not only the cut. A martial, intolerant winner then expels. (A mechanism: Daniel's era-free
  range of conquerors.)
Lean: C, with A's TOL_X. It gives the razing conqueror a cause in the model, instead of turning the dial for everyone.
- [ ] Daniel picks; then re-measure the fates by winner on seeds 7 and 10 (round10/measure.py)

## Updates
- 2026-11-05: Created from inbox draft draft-live-conquerors-rarely-harsh.md (found by lane201b).
