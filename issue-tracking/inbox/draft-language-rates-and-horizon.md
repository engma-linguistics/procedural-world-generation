---
title: "Language rates: the scholars' horizon reads 11-13 kyr against the 6-10 target, and sisters-recognisable pulls the other way (needs a ruling on the target, and on per-generation scaling for 6-yr-generation peoples)"
type: task
status: needs-decision
parent: PW-767
subsystem: culture
effort: s
impact: high
found_by: lang-design
blocked_by: []
relates: [PW-986, PW-982, PW-1423]
refs: [planet/language/history.py, planet/language/families.py, docs/review/language/calibration.md, docs/review/language/demo.md]
---

## Description
In plain words: the engine's speed of change was tuned so that an automatic comparative method on the output goes blind
somewhere near 6-10 kyr (the design check). On a24559 it goes blind at 11 kyr (one run) or 13 kyr (another). Pushing the
rates up to hit 6-10 makes sister dialects split 2 kyr ago fall below "recognisably related" (0.45 against the 0.5 bar).
The two checks pull against each other at the current word-replacement shape, so one of them has to give. If this is never
ruled on, the horizon check stays red on every run and nobody knows whether the languages are too conservative or the
measure is too generous.

Facts (calibration.md, trials t1-t9 and final):
- Final constants: RATE_SCALE 5 on RATE_RULE 0.1 per generation (humans ~22 rules per kyr, long-lived peoples ~6),
  REPLACE_SCALE 1.25 (Swadesh-100 retention ~86%/kyr x 1.25), COGNATE_DIST 0.45.
- Sisters: 0.53 blind cognate share; cross-family 0.005; chance floor 0.017.
- The horizon is read from the present back, per 1-kyr bin of true split ages, as the first bin where fewer than half the
  pairs still beat their own chance level; a24559 has few human splits between 9 and 12 kyr, so it jumps 9 -> 11 -> 13.
- Two runs of the same seed gave 11 and 13: the driver is not bit-for-bit deterministic across runs (548 vs 547 languages),
  probably the fork pool or set ordering; worth a fix before any calibration is trusted to 1 kyr.
- Exponent 1 per generation (Daniel 11-03) means aarakocra (5.8-yr generations) change 4.8x faster per year than humans and
  their own horizon is ~2-3 kyr; elves (145 yr) look like ~3 kyr of human change over 20 kyr. The numbers are in demo.md.

Options for Daniel:
1. Widen the target to 6-13 kyr and keep sisters at 0.5 (the lane's lean: the measure is a blind UPGMA on 100 words, which
   is more generous than a real comparative method on a few hundred words; real families are reconstructable to ~8-10 kyr
   only with much more data than 100 words).
2. Keep 6-10 and accept sisters near 0.45 (trial t4).
3. Change the replacement shape (faster rare words, slower core) so both can hold; a half-day of calibration.
And separately: keep exponent 1, or soften it (0.7) for the very-short-generation peoples.
- [ ] Daniel's ruling recorded on PW-986; the check's target updated; a determinism fix so two runs agree
