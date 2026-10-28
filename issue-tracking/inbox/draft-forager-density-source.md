---
title: Giants' forager baseline of 0.1 per km2 has no located source
type: task
status: needs-decision
parent: null
subsystem: infra
effort: s
impact: low
found_by: citation-check-hamilton-chatterjee-mcnab
blocked_by: []
relates: [PW-938, PW-963]
refs: [planet/lineages/history/megafauna.py, docs/proposals/megafauna-scaling.md, docs/references/megafauna/README.md]
---

## Description
`FORAGER_KM2 = 0.1` in `planet/lineages/history/megafauna.py` (human foragers per km2, "the proposal's median of hunter-gatherer densities", scaled by M^-0.75 from `FORAGER_KG = 65` to give the mesotherm/mammal giants' density: hill giants ~1 per 140 km2, storm ~1 per 345) is cited to Binford 2001 and Hamilton et al. 2007. The citation check of 2026-10-28 (PW-938) read Hamilton et al. 2007 (PNAS 104:4765) and found:
- the paper analyses Binford's 339 societies but fits area used against group size N, not density against body mass; the ~0.1/km2 median is not printed in it;
- its all-forager fit (Table 1, p. 4767) is A = e^4.44 N^0.70 km2, i.e. 0.031 per km2 at N = 25, 0.047 at 100, 0.076 at 500, 0.094 at 1,000 (hunters alone, beta 0.90, C0 4.46: lower again, ~0.016-0.018 for N = 25-100); r2 is only 0.24 and the scatter is about 2 orders of magnitude;
- the M^-0.75 body-mass scaling is Kleiber/Damuth, not from Hamilton (whose 0.70/0.756 exponents are for group size).

So 0.1 is the top of what the paper's fit implies, not demonstrably wrong, but its source is unlocated. The constant was NOT changed (it moves the giants' densities and the 70% pass rate).

Options:
- A: keep 0.1 and find the figure in Binford 2001 (a book, not on file); cite it there.
- B: replace with a value from Hamilton's fit at a typical band-to-tribe size (~0.05, doubling giant spacing to roughly 1 per 280 km2 for hill giants).
- C: leave as an owner-set setting and say so in the docs.
Lean: C, since the giants are hand-waved placement anyway (PW-936) and the note in the proposal already says the 0.1 is unsourced; A only if Binford turns up.
- [ ] decision made; constant, comment and proposal agree
