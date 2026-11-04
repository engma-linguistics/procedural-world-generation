---
title: "Language rates: the scholars' horizon now reads 9 kyr by a split-based measure (the old pair measure read 11-13); rule whether the measure's tolerances stand, whether the sisters bar applies to the strict cognate test, and whether 6-year-generation peoples keep exponent 1"
type: task
status: needs-decision
parent: PW-767
subsystem: culture
effort: s
impact: high
found_by: lang-design
blocked_by: []
relates: [PW-986, PW-982, PW-1423]
refs: [planet/language/history.py, planet/language/families.py, planet/language/checks.py, docs/review/language/calibration.md, docs/review/language/demo.md]
---

## Description
In plain words: the engine's speed of change was tuned so that an automatic comparative method on the output goes blind
near 6-10 kyr (the design check). The first measure (per-pair edit distance on 100 words) read 11-13 kyr and rested on one
thin bin; the lane replaced it with a split-based measure under a stricter cognate test (aligned distance under 0.45 *and*
recurring correspondences, a clade in the scholars' UPGMA tree matching the true split at Jaccard >= 0.8, beating chance by
0.03). On a24559 it reads **9.0 kyr for human lects**, 9.6 for all. The check passes, but three choices inside it are
judgement, and if nobody rules on them the green check is worth less than it looks:
1. The tolerances: exact clades only (Jaccard 1) give 4.9 kyr; excess 0.05 gives 4.7; 0.02 gives 10.5. The lane chose
   0.8 / 0.03 as "a scholar would accept a near-match".
2. The sisters check (lects parted <= 2 kyr share > 0.5 of the core 100): sisters score 0.54 on the loose test, **0.46 on
   the strict one**, 0.57 by true roots. The check passes on the loose share. Should the bar move to the strict share?
3. Exponent 1 per generation (Daniel 11-03): aarakocra (5.8-yr generations) change ~5x faster per year than humans and
   their sisters 5 kyr apart share almost no core roots; kobolds (11.7) ~2x; elves (145) look like ~3 kyr of human change
   over 20 kyr; dragons keep most of their proto core words. Keep as ruled, or soften (0.7) for the short-generation peoples?
Also: the lexical-replacement curve is probably the wrong shape (sisters share 0.57 of true roots where ~0.7 is expected,
but 7-9 kyr pairs still 0.13-0.20 where ~0.10 is expected): a faster rare-word end and a slower core end would fix both.
- [ ] Daniel's rulings on 1-3 recorded on PW-986; `checks.HORIZON_RANGE`, `SIBLING_MIN` and the measure's constants set
