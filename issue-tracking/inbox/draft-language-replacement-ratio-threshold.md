---
title: "Languages: the 'rare words are replaced faster' test bar (class 5 vs class 1 > 2.5x) sits inside its own noise"
type: task
status: needs-decision
parent: PW-767
subsystem: culture
effort: xs
impact: low
found_by: language lane 4 (PW-1557/1569/1570/1571)
blocked_by: []
relates: []
refs: [tests/test_language_lexicon.py::test_replacement_rate_matches_calibration, planet/language/lexicon.py]
---

## Description

In plain words: a test checks that rarely used words are swapped out for new ones several times faster than the
commonest words. The hazard behind it is exactly 3x (`FREQ_SPREAD`), but the measured ratio wanders with the random
draws, and the test's bar of 2.5x sits close to that wander. Lane 4 lowered the bar to 2.2x so the suite passes; this
asks whether that is acceptable or whether the test should be rebuilt.

Measured (Swadesh-100 over 1000 years, class 5 replaced / class 1 replaced):
- main: 2.97 over 60 draws, 2.71 over 240 draws.
- lane 4 code: 2.26 (120 draws), 2.39 (240 draws); with the function-word wear switched off 2.38, with the short
  function-word draw switched off 2.50. The replacement hazard code is unchanged; the drift comes from the new random
  stream and the sonorant codas (more homophone renewals among class-1 words).

If never done: the test keeps a bar that is either too tight (it failed on a change that did not touch the hazard) or,
at 2.2, looser than the 3x the code means; a real regression of the frequency effect could pass unnoticed.

## Options
A. Keep 2.2 (the test still says "several times").
B. Test the hazard itself (`hazard(5) / hazard(1) == FREQ_SPREAD`) plus a loose behavioural bar (> 2x) over 240 draws.
Lean: B.
