---
id: PW-1541
title: "Optional grammar is stripped in the full run: 3-way demonstratives and graded pasts at half the harness rate, questions by intonation alone 36% vs ~14%, core grams lost with no renewal"
type: task
status: todo
parent: PW-767
milestone: null
subsystem: culture
effort: m
impact: med
found_by: lang-design (grammar C and D lanes, finish lane, 2026-11-08)
blocked_by: []
relates: [PW-985, PW-982]
refs: [docs/review/language/for-daniel.md, docs/review/language/grammar-gaps.md, docs/review/language/calibration.md, planet/language/grammar.py, planet/language/inputs.py, planet/language/sentences.py, "run a24559"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: in a test bench of isolated languages the grammar engine produces close to real shares of features
like 'this / that / yonder' and graded pasts. In the full world run, where languages are in contact and many speakers
learn as adults, these optional words are dropped and never become grammar, so the world's languages come out plainer
than real ones. Most visibly, half again as many languages ask yes/no questions by intonation alone as real ones do,
and some languages lose negation or the past tense outright without renewing it, which real languages almost never do.

**Now** (a24559 full pass after grammar D, 612 living lects; harness = 300 isolated human protos, ~20 kyr):
| feature | harness | full pass | reference |
| --- | --- | --- | --- |
| 3-way demonstratives | 31% | 16% | WALS 41A about 37% |
| graded past, of lects with a past | 20% | 11% | WALS 66A about 30% |
| polar question by intonation only | 32% | 36% | WALS 116A about 14% |
| applicative / antipassive | 12% / 1% | 9% / 0% | WALS 109A ~45% / 108A ~25% |
| verb synthesis, 0-1 bound categories | 24% | 55% | WALS 22A about 3% |

Cause, per the lanes: high adult-learner shares (median 0.53) strip free words before they bind, and a wanted free
particle is often abandoned (`KEEP`, `PULL_BOOST`). The antipassive has one source (a live reflexive in an ergative lect).

Also (finish lane): a whole function (NEG, PAST, PL) sometimes drops out with nothing replacing it: goliath d152 lost
NEG ~1.5 kyr ago; hobgoblin d641 ends at complexity 0.38, almost no grammar. Real languages renew negation (Jespersen's
cycle) rather than lose it.

**Synthesis** is being changed tonight by lang-synth (`FUSE`, the L2 exponent on fusion). If the 0-1 bin is still above
~25% after it merges, that is the first box here, not a new decision.

**Wanted.**
- [ ] core functions (NEG, PAST where a past existed, PL, Q) cannot be lost without a renewal path being recruited
- [ ] full-pass shares within ~10 points of WALS for 3-way demonstratives, graded past, intonation-only questions
  (lever: L2 stripping of *wanted* grams, not of all free words)
- [ ] an antipassive source that can be cited, or accept ~0% in writing
- [ ] synthesis 0-1 bin under ~25% (if lang-synth did not reach it)

## Updates
- 2026-11-08: Created from inbox draft draft-language-grammar-shares-full-pass.md (found by lang-design (grammar C and D lanes, finish lane, 2026-11-08)).
