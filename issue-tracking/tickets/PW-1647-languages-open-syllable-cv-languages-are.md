---
id: PW-1647
title: "Languages: open-syllable (CV) languages are 5% of living lects, against about 12% in WALS"
type: task
status: todo
parent: PW-767
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lang-lane14b
blocked_by: []
relates: [PW-1642, PW-1641]
refs: ["planet/language/lect.py::pattern_resist", "planet/language/lect.py::PATTERN_K", "planet/language/inventory.py::retemplate", "planet/language/lexicon.py::borrow"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: languages built only of open syllables (Hawaiian, Yoruba-like: no codas, no clusters) are about 12%
of the world's languages (WALS 12A). On a24559 they are now 5% of living lects (main had 22%). Main's 22% was the old
drift: coda languages wore down to open syllables (116 of main's 138 open-syllable lects came from protos with codas).
The word-shape anchor (PW-1642, lane 14) stopped that drift, which was the point, but now nothing flows the other way:
0 coda-language lines became open-syllable on lane 14b's pass.

Lane 14b's diagnosis (scratch scripts lane14b/simple.py, seen.py, first.py):
- Not the suspected "medial codas the anchor never sees": the anchor's 120-word sample tracks the core-100 within
  about 0.02 in every lect checked.
- The proto draw is fine: 37 of 321 protos (11.5%) are open-syllable.
- Open-syllable lines keep their shape in 56% of their living daughters (main 31%). The rest slip through loans and
  shifted words from coda-language neighbours, coined words once the template opens (retemplate: a lect whose words pass
  the template share gets CVC shapes, and coins and loan repairs then use them), and syncope or vowel loss getting past
  the anchor one step at a time while the anchor follows the words (PATTERN_KYR).
- Nothing flows in: real languages do lose codas wholesale (Oceanic to Polynesian, Latin to Italian finals), but under
  the anchor a coda line reaches under 3% codas only through a signature change.

Try, one at a time, judged on a24559 + de1cc6 (scratch syl.py) and `real_inventory.py --check`:
1. Loans into a line that holds an open-syllable pattern are repaired to the pattern (Japanese, Hawaiian epenthesis),
   not to a template the words have just opened.
2. Wholesale final-consonant loss (S099-type) allowed as a signature change at a split, so a branch can go open the
   way Polynesian did.
- [ ] simple syllables 9-15% of living lects on a24559; moderate and complex stay near WALS (0.56, 0.31)
- [ ] benchmark: no metric worse than the baseline

## Updates
- 2026-11-10: Created from inbox draft draft-open-syllable-stable-state.md (found by lang-lane14b).
- 2026-11-10: Lane 16 (merged 15b6fea2): step 1 done (retemplate keeps CV while the anchor holds), gain under 1 point (a24559 5.0 > 5.8%). Step 2 (S099 final-consonant loss as a split signature, one-off cap lifted for it) is written but not run; the edit script is kept at docs/review/language/lane16/ed_1647b.py (an untested patch script).
