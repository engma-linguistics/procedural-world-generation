---
id: PW-1605
title: "Languages: 2-5 case systems still 33% of living languages against WALS 49A's 20%, no case 38% against 47%"
type: task
status: todo
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: low
found_by: language lane 8 (PW-1586)
blocked_by: []
relates: [PW-1586]
refs: ["planet/language/grammar.py::_case_at_birth", "planet/language/grammar.py::_draw_feature", "planet/language/grammar.py::_wanted", "planet/language/grammar.py::case_bin", docs/review/language/calibration.md, "scratch pass lane8/pass (a24559, gone after the lane)"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: after lane 8 gave big-case protos their endings at birth, big systems (6+ cases) are 29% of living
languages in a24559 (real languages: 32%). The rest of the spread is still off: small systems of 2-5 cases are 33%
(real: 20%) and languages with no case or only clitic case are 38% (real: 47%).

**What misleads if never done:** a reader comparing the world's languages with real ones sees too many small case
systems and too few caseless languages; the WALS 49A comparison on the language page would be off by 10+ points.

Where the middle comes from (lane 8 reading, to confirm): lects whose aim is 'few' (about 14% of aims) grow 1-4 markers;
lects whose 'none' aim drifts to 'few'; big systems worn down by adult learners (L2 stripping) passing back through the
band. In the 700-generation harness (`caseharness.py`, lane 8) the band refills from 8% at 100 generations to 25% at 700.
Levers to screen, one small harness pass each: (1) how fast a 'few' system recruits a second and third marker
(`_wanted` asks GEN, LOC, DAT of any case system); (2) whether a 'none' aim should resist adopting a bound case
marker longer (`_adopt`); (3) L2 stripping of case versus other affixes.
- [ ] none + borderline within ~5 points of 47% and 2-5 within ~5 points of 20% in a full pass, 6+ kept near 30%

## Updates
- 2026-11-09: Lane 9 (lang-lane9): case clitics fuse at x0.1 under a 'case: none' aim (`grammar.UNWANTED_CASE_FUSE`); a 'few' system pulls no genitive of its own. a24559 full pass, lane 8 stored -> lane 9: none+borderline 38.0 -> 48.2% (47), 2-5 33.0 -> 28.2% (20), 6+ 29.0 -> 23.5% (32), 8+ 13.7 -> 12.7%. Partly met: 2-5 still 8 over, 6+ 8.5 under; borderline 20% vs WALS 9% (the clitic level reads as borderline whatever its form). L2-strip lever: noise in the harness, dropped. Next: split clitic case into phrasal affix vs postposition when binning, and re-read 6+ on a second seed.
- 2026-11-09: Created from inbox draft draft-language-case-middle-band.md (found by language lane 8 (PW-1586)).
