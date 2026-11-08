---
id: PW-1018
title: "Food budget: dense 'hunter' peoples (halflings 12/km2, goblins 5, hobgoblins 4) take ~85% of the wild offtake in foragers' country, so dragons get almost nothing there before farming"
type: task
status: needs-decision
parent: null
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: fun-lane-45b
blocked_by: []
relates: [PW-977, PW-974, PW-990]
refs: [planet/lineages/history/megafauna.py, planet/lineages/landuse.py, docs/review/megafauna/age-of-dragons.html]
created: 2026-10-29
updated: 2026-11-03
---

## Description
**In plain words.** Some fantasy peoples are tagged as hunters but live as densely as farmers: halflings at 12 per km², goblins at 5. Real hunter-gatherers live at well under 1 per km². Because the model lets every hunter people get half its food from wild game, these dense peoples eat nearly all the wild animals in their country, and dragons there starve. Before farming, dragons end up living only where no people live. The question: should a dense people get less of its food from hunting (they must be gathering or growing most of it), which leaves game for the dragons? Coordinator's lean: yes (B). Physically, game can't feed that many people.

PW-977 stage 2 lets each people's hunters take their game first: density x a person's food x the game share (WILD_MEAT: 50% for
a forager, 5% for any other way; `landuse.shares(...)["forage"]` decides which, and the `hunter` trait counts as a full forage use).
In dnd several lines with that trait sit at farmer-like densities: halflings 12/km2, gnomes 12 (half forage), goblins 5,
hobgoblins 4, lizardfolk and tabaxi 1.5. Real foragers live far sparser: spec.py's forager_km2 note reads Hamilton et al. 2007's
fit as 0.03-0.09/km2 for groups of 25-1,000 (PW-976); a wider ethnographic range is UNVERIFIED here (Binford 2001 not on file). At 3.7/km2 mean, half their food from game is ~1.2 t/km2/yr of prey, against a wild
offtake of ~0.1-0.7 t/km2/yr, so the min() in `budget` hands them all of it.

On the 6 x 4 dnd sweep (fun lane 45b), in foragers' country the peoples take 82-88% of the supply at 25 kyr, 10 kyr and the
present, and the dragons' share left is 2-3% (15-16% in country nobody holds). The proposal's picture, "before civilisation the
dragons eat most of the surplus and foragers live in the gaps", is the reverse of this.

Options:
- **A.** Keep: dense peoples hunt out their country, dragons live where peoples do not.
- **B.** The game share falls with density: a people can only be a forager at forager densities, so WILD_MEAT[0] applies up to
  ~0.1-0.5/km2 and the rest of a denser people's food is gathered or grown (a sourced form wanted).
- **C.** Treat the `hunter` trait as a part forage use (say 0.3) for lines with a farming or other use, not a full one.

Lean: B. It follows from the energetics (game cannot feed people at those densities) and needs no per-people tuning.

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: dragon and giant food budget re-tunes the peoples balance; not a must-have for December
- 2026-10-29: Created from inbox draft draft-dense-hunter-peoples-eat-the-wild-offtake.md (found by fun-lane-45b).
