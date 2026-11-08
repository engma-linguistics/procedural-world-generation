---
title: "Languages of long-lived peoples stay almost all isolating (93% with 0-1 bound verb categories)"
type: task
status: needs-decision
parent: PW-767
subsystem: culture
effort: s
impact: med
found_by: lang-synth (synthesis lane, 2026-11-08)
blocked_by: []
relates: []
refs: [planet/language/grammar.py::step, planet/language/lect.py, docs/review/language/calibration.md, "run a24559"]
---

## Description
In plain words: grammar changes (a word wearing down into an ending) are counted per generation. Dragons and other
peoples whose generations last 150+ years get fewer than ~130 generations in our 20,000 years, so their languages almost
never grow endings: 93% of their living languages mark at most one verb category with an affix, against 10% for
short-lived peoples after the synthesis lane. Every dragon language reads like Classical Chinese or Vietnamese.

Measured on a24559 (synthesis lane pass 1, living lects): generation >= 150 yr, 118 lects: bins 0-1 / 2-3 / 4-5 / 6-7 / 8+
= 93 / 6 / 1 / 0 / 0%; generation < 60 yr, 375 lects: 10 / 41 / 37 / 11 / 0%; 60-150 yr: 23 / 38 / 28 / 11 / 0%.

This is consistent with sound change, which is also per generation (the "long generations change less" check wants it),
so it may be intended: slow-changing peoples with old, conservative, analytic speech. But a conservative language can
also be one that kept old inflection (Lithuanian, Icelandic), and our long-lived protos start with only 1-3 free grams,
so "conservative" here always means "isolating".

**What misleads if never done:** the language pages of every dragon, giant and other long-lived people show the same
isolating type, which reads as a rule of the world nobody chose.

Options: (a) accept it (long-lived peoples' speech is analytic: a world fact); (b) give long-lived protos a richer
starting grammar (more grams already bound at 20 kyr, as a language with a deep unrecorded past would have), so
slowness conserves inflection instead of preventing it; (c) count grammaticalization partly per year rather than per
generation. (b) is the cheapest and keeps the per-generation clock. Your call.

- [ ] decide (a), (b) or (c)
- [ ] if (b) or (c): re-measure the WALS 22A bins by generation class (`scratchpad synth/fullan.py`)
