---
id: PW-1222
title: "Dragon intake leaves out growth and flight: the mesotherm law is a field metabolic rate, which Nagy 2005 says omits the food for growing"
type: task
status: needs-decision
parent: null
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: lane-90
blocked_by: []
relates: [PW-1066, PW-958]
refs: [planet/lineages/dragon_ages.py, docs/review/dragon-food-chain/report.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
**In plain words.** The model now says plainly what a dragon eats: about half of what a mammal of its weight would, as the paper the
dragons' numbers come from assumes for dinosaurs. Two costs are still left out. Dragons grow all their lives, and growing takes food on
top of living. And dragons fly, which costs more than walking. Both would make each dragon eat more, so the land would hold fewer. Nobody
has measured either for an animal like this, so it is a choice for the owner whether to add a margin.

Evidence: Nagy 2005 (J Exp Biol 208:1621, p. 1624): the food equations leave out growth ("this additional food is not accounted for").
The only flying line on file is Nagy et al. 1999's birds (10.5 M^0.681, Table 2 p. 260), which at dragon sizes sits near the mammal line
(sensitivity.py: x0.48 dragons against the model's law, as the mammal line is).

Options:
- **A.** Leave both out, as now (the law is a field metabolic rate; stated in dragon_ages' docstring).
- **B.** Add a growth margin (no source for its size in a reptile-like grower this big).
- **C.** Use the bird line for flying dragons as an upper bound on intake (x0.48 dragons).

Lean: A. The intake law is now a stated, sourced choice; B and C have no number to put in.

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Dragon-density tail; PW-961 stays. Still needs-decision; parking does not answer it.
- 2026-10-31: Created from inbox draft draft-dragon-intake-growth-and-flight.md (found by lane-90).
