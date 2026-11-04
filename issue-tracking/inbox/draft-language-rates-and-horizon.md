---
title: "Language rates: keep exponent 1 per generation for the shortest-generation peoples (kobolds 12 yr), or soften it to 0.7?"
type: task
status: needs-decision
parent: PW-767
subsystem: culture
effort: s
impact: med
found_by: lang-design
blocked_by: []
relates: [PW-986, PW-982, PW-1423]
refs: [planet/language/history.py, planet/language/families.py, planet/language/checks.py, docs/review/language/calibration.md, docs/review/language/demo.md]
---

## Description
In plain words: languages change once per generation, so a people with short generations changes faster per year. Daniel
ruled exponent 1 (no softening) on 11-03. One question from that is still open: is that too fast for the shortest-lived
peoples?

Already ruled (Daniel, 11-04), recorded here so the draft holds only what is open:
- **Horizon target** 6-10 kyr for human lects ("sounds right"); **longer for long-lived peoples** (dwarves, elves,
  dragons): the horizon check now also asserts that the long-lived peoples' horizon is longer than the humans' (or that
  their splits are still recovered as far back as they go).
- **Smoothing:** the horizon is the start of the first two consecutive 2-kyr windows where fewer than half the true splits
  are recovered; a smoothed read (split-weighted moving average over 3 windows) is reported beside it.
- **Sisters bar:** the strict cognate share (aligned distance and recurring correspondences, a linguist's view), bar 0.5.
- **Strictness inside the measure** (clade tolerance, chance excess): the lane's call, aiming at "real-looking". Kept at
  Jaccard 0.8 and excess 0.03; windows with under 3 splits widen by up to 1 kyr per side instead of being skipped
  (calibration.md, "Measures and phonemes round"). Run F reads human 10.25 kyr (just over 10), long-lived censored at
  22 kyr or more.

Still open:
- With exponent 1, kobolds (11.7-yr generations) change about twice as fast per year as humans; a third of their living
  lects keep no proto core word after 20 kyr, so their families are barely visible. Aarakocra are no longer the extreme
  case: the preset now gives them 18.6-yr generations (adult 12, lifespan 60, like kenku 19.3), and the language pass uses
  it. Keep exponent 1 for everyone, or soften it (rate x (28 / generation) ** 0.7) below human generation length?
- [ ] Daniel's ruling recorded on PW-986; `history` / `lect` per-generation scaling set accordingly
