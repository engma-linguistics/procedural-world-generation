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
- `core words rarely borrowed` (0 of 8 cells): I, WE, MOTHER and FATHER are under 0.05 everywhere; TWO and THREE reach
  0.06-0.08 in 4 cells (0141d1, 3e0eb4, de1cc6 s7919); Swadesh-100 words borrowed across families in the last 3 kyr
  are 2.3-3.0% in every cell against 2%. Matrix tables: docs/review/language/matrix/lane20-2026-11-11.md. Lever:
  `lexicon.CORE_LOAN_DAMP` 0.35 -> ~0.25 (the replacement calibration `KEEP_COMPENSATION` may then need re-solving:
  test_replacement_rate_matches_calibration).
- `late things arrive as loans`: words for late things (animals met, biome kinds, tech items, crops) first made or taken
  in the last 6 kyr are loans or calques 41-51% (2 of 8 cells pass) against 50%. Most coinages are crop and herd
  origins ("tamed here", legitimate) and `tech_step` / `wild_step` coinages when a neighbour already had a word. Levers:
  `WILD_LOAN` 0.6 -> 0.7, and in `tech_step` borrow from any contact lect that has the word more often; or exclude route
  origins (a taming deme coins by definition) from the share.
Round 2 (lane 20, 05edb1aa: CORE_LOAN_DAMP 0.25, WILD_LOAN 0.8, tech words not intensity-scaled, calques first): late
loans now pass 8 of 8 (50-57%); core loans 4 of 8. The fails are THREE 0.059-0.062 on a24559 own and 0141d1 own; on
de1cc6 (Seven Meals) the cross-family share is 2.3% on both draws and TWO is 0.103 on one. CORE_LOAN_DAMP 0.2 made
tests/test_language_history.py::test_root_families_in_the_document fail on a draw-dependent colex/etymology node
mismatch (('colex:MANY', 'rɛri') not among the word's steps), which needs chasing before going lower. The check now reports
`item_loan_sources` (each loan step's note) to show which path borrows TWO and THREE. Suspects are trade or elite
contact kinds and numeral-system loans.
What misleads if never done: the matrix shows two red realism rows on every cell, which hides a real regression there.
- [ ] both checks pass in >= 70% of matrix cells, no other check worse by more than one cell
