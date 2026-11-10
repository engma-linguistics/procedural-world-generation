---
id: PW-1653
title: "Languages: basic words merge into one form too often (what = one in 7% of lects); renewed 'not' loses its negator; sisters page fixes"
type: task
status: done
parent: PW-767
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-1642]
refs: [tools/language/sisters_page.py, planet/language/lexicon.py, "planet/language/lexicon.py::cross_repair", "planet/language/lexicon.py::_renew_cell", tests/test_language_lexicon.py, docs/review/language/for-daniel.md]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: owner noticed 'what', 'not' and 'one' are one word (zi / ni) in the two sister languages.
- 'what' and 'one' were separate roots that sound change wore down to zi. Over a24559's 622 living lects, WHAT=ONE in 45, I=ONE 15, NOT=ONE 13. Real languages repair clashes between basic words (Gilliéron's Gascon: 'cat' and 'rooster' both became gat, and the rooster was renamed 'pheasant' or 'vicar'). Add a repair: when a change merges two core words of different meaning, one is renewed (synonym, compound or loan) within a few centuries. Leave the real colexifications (EAT=DRINK 69, WOMAN=MOTHER 21: both attested, CLICS) alone, or compare their rates to CLICS.
- 'not' in d713.2 was renewed 1.5 kyr ago from ONE (attested path: Latin non < ne oinom 'not one', French pas) but kept only the 'one' part: a renewal should keep the negator plus the reinforcer.
- Sisters page: CHILD looked up as 'CHILD' (the concept is 'CHILD (YOUNG HUMAN)'), so the row is empty; the ancestor's form shows *? for words outside the 100-word snapshot list (mother, father, child, three): trace them through the etymology instead; prefer 3-6 sisters (Romance/Bantu-like fans), widening the window to the biggest recent fan.

## Updates
- 2026-11-10: Created from inbox draft draft-core-word-homophones-and-sisters-page.md (found by coordinator).
- 2026-11-10: Done in language lane 15. `lexicon.cross_repair`: a merged pair of basic words of different paradigms (both frequency class <= 2, on a core list or closed-class; CLICS3 < 5 families; not a paradigm pair, a system colexification or a deliberate shift) is repaired with a chance that halves its life every 8 generations (~200 years); the rarer member is renewed (a content word before a function word, a pronoun last and never by a loan) by reinforcement, loan, derivation, compound or fresh root (`_renew_cell`, shared with core_repair). a24559 living lects: pairs in scope 1808 -> 350 (2.9 -> 0.56 a lect); WHAT = ONE 45 -> 0, I = ONE 15 -> 1, NOT = ONE 13 -> 2; EAT = DRINK (26 CLICS families) 69 -> 82 and WOMAN = MOTHER (7) 21 -> 13 left alone. de1cc6: 1293 -> 295, WHAT = ONE 6 -> 0. The 'not' that lost its negator: sound change ate the final NOT of a head-final 'one-not' compound; the repair now renews such a merged 'not'. That 'not one' is the only NOT reinforcer (~40% of lects) is a lane 15 draft. Sisters page: CHILD looked up as 'CHILD (YOUNG HUMAN)'; ancestor forms outside the snapshot list traced through a sister's etymology; picks the biggest fan of 3-6 daughters, widening the window until 3+ turn up; a place-names row.
