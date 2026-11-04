---
title: "The ladder farms cells where the crop layer has no crop growable: a quarter of farmed cells in a2b637, so some cuisine sheets cannot name the staple"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: lane164
blocked_by: []
relates: [PW-1275, PW-1385, PW-1391]
refs: ["planet/lineages/ladder.py (who farms per cell: FARM_SHARE of the fertile good once a people knows cultivation)", "planet/lineages/landuse.py::frame_inputs (eraq farm)", "crops.py GROWN_MIN (crop_known = known and growable)", "planet/lineages/cuisine.py::staple", "run a2b637 culture 572 (humans of the east of Simath)", docs/review/food/cuisine-sheet/round1.md]
---

## Description
In plain words: the density ladder says a cell farms once its people knows cultivation and the land is fertile, but the crop layer
(`crop_known`) only marks a crop where it is both known and growable. In run a2b637 at the present, 25,814 cells farm (eraq farm > 0)
and 6,608 of them (26%) have no crop at all in `crop_known`. One human culture (572, 1,626 land cells) is 98% farmers by heads with no
crop on any of its cells. The cuisine sheet then says "farmed food ... but the run's crop layer has no staple growable on its land".
What breaks if never done: the book's Staple line is blank for such cultures, and the density there is a farmer's density with nothing
to farm (an overcount the peoples numbers inherit).

What to try: let the ladder's farm share read the crop layer (no growable staple, no farming rung), or find why the two disagree (the
crop's grown range vs the fertile good; a crop known by the people but not yet spread to those cells).
- [ ] farm share > 0 only where `crop_known` has a staple, or the gap explained and the sheet's fallback kept
