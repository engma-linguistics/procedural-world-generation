---
title: "Languages: two lane-20 checks sit just under their bars (Swadesh-100 cross-family loans 2.4-3.0%; new things loaned 41-51%)"
type: task
status: todo
parent: PW-1736
subsystem: culture
effort: s
impact: med
found_by: lang-lane20
blocked_by: []
relates: [PW-1738, PW-1745, PW-1737]
refs: ["planet/language/checks.py::core_loans", "planet/language/checks.py::late_things", "planet/language/lexicon.py::CORE_LOAN_DAMP", "planet/language/history.py::WILD_LOAN", "planet/language/history.py::tech_step", "planet/language/history.py::food_step", "lane 20 matrix (scratch, gone): a24559 / de1cc6 cells"]
---

## Description
In plain words: lane 20 cut core-word borrowing from 10-22% to under 4% per item and gated late animals, but two of the
new checks it added fail narrowly on the matrix, so they count as failing realism checks until tuned.
- `core words rarely borrowed`: every item (I, WE, ONE-THREE, MOTHER, FATHER) is under 0.05 in all cells, but
  Swadesh-100 words borrowed across families in the last 3 kyr are 2.4% (a24559) and 3.0% (de1cc6) against 2%. Lever:
  `lexicon.CORE_LOAN_DAMP` 0.35 -> ~0.25 (the replacement calibration `KEEP_COMPENSATION` may then need re-solving:
  test_replacement_rate_matches_calibration).
- `late things arrive as loans`: words for late things (animals met, biome kinds, tech items, crops) first made or taken
  in the last 6 kyr are loans or calques 41-42% (a24559), 51% (de1cc6) against 50%. Most coinages are crop and herd
  origins ("tamed here", legitimate) and `tech_step` / `wild_step` coinages when a neighbour already had a word. Levers:
  `WILD_LOAN` 0.6 -> 0.7, and in `tech_step` borrow from any contact lect that has the word more often; or exclude route
  origins (a taming deme coins by definition) from the share.
What misleads if never done: the matrix shows two red realism rows on every cell, which hides a real regression there.
- [ ] both checks pass in >= 70% of matrix cells, no other check worse by more than one cell
