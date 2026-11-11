---
id: PW-1738
title: "Languages: core words (I, one-three, mother, father) are borrowed in 10-22% of languages; paradigm repair borrows before it derives"
type: story
status: todo
parent: PW-1736
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lang-assessment
blocked_by: []
relates: []
refs: [docs/review/language/assessment-2026-11-11.html, "planet/language/lexicon.py::_renew_cell", "planet/language/checks.py::borrowability", planet/language/data/borrowability.tsv, "run a24559"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: real languages almost never borrow 'I', low numerals or mother/father; ours do in 10-22% of living lects (a24559: I 0.10, THEY 0.087, ONE 0.16, TWO 0.18, THREE 0.22, MOTHER 0.195, FATHER 0.20). 38 of 52 'I' loans and 42 of 109 FATHER loans come from the paradigm-repair step (`_renew_cell`, lexicon.py ~2481), which borrows a form before trying to derive one and ignores borrowability. The pronoun-loans check passes (0.063) only because it is a lect-level average.
- [ ] `_renew_cell` derives/renews from the lect's own material first; a loan there is scaled by contact intensity x WOLD borrowability
- [ ] a per-band check: Swadesh-100 cross-family loans within 3 kyr <= ~2% (WOLD several times lower than all-words), plus per-item caps for I/WE/ONE-THREE/MOTHER/FATHER
- [ ] A->B->A ping-pong loans (3.8% of words) looked at while here

## Updates
- 2026-11-11: Created.
