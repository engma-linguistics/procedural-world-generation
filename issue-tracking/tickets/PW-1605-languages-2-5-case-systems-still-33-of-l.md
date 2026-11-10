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
refs: ["planet/language/grammar.py::PRE_CASE_CLITIC", "planet/language/grammar.py::PRE_FUSE", "planet/language/grammar.py::_case_at_birth", "planet/language/grammar.py::_draw_feature", "planet/language/grammar.py::_wanted", "planet/language/grammar.py::case_bin", docs/review/language/calibration.md, "scratch pass lane8/pass (a24559, gone after the lane)"]
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
- 2026-11-09: Lane 10 (lang-lane10): clitic-only was mostly not counting but case PREPOSITIONS turning into proclitics and stalling there (PRE_FUSE): a24559 lane 9 had 13.6% of living lects with only case proclitics against WALS 51A's 1.6%; 70% of borderline lects had a single case clitic. Now a preposed case marker cliticises at x0.05 (grammar.PRE_CASE_CLITIC; WALS 51A: 17 prepositional vs 123 postpositional case-clitic languages). a24559 full pass, lane 9 -> lane 10: none 28.1 -> 35.2% (WALS 38), borderline 20.1 -> 10.5% (9), none+borderline 48.2 -> 45.6% (47), 2-5 28.2 -> 28.1% (20), 6+ 23.5 -> 26.3% (32), 8+ 12.7 -> 13.5% (18); WALS 51A-like: proclitic-only 13.6 -> 3.4% (1.6), case prefixes 5.8 -> 4.0% (3.7), suffixes 43.5 -> 50.2% (43.8). Harness (lane 10 caseharness.py, gram cycle and also full Lect.step with sound change) holds 6+ at 33-35% for 800 generations: the 6+ and 2-5 gaps come from the history, not the gram cycle (draft draft-language-case-big-systems-history).
- 2026-11-09: Lane 9 (lang-lane9): case clitics fuse at x0.1 under a 'case: none' aim (`grammar.UNWANTED_CASE_FUSE`); a 'few' system pulls no genitive of its own. a24559 full pass, lane 8 stored -> lane 9: none+borderline 38.0 -> 48.2% (47), 2-5 33.0 -> 28.2% (20), 6+ 29.0 -> 23.5% (32), 8+ 13.7 -> 12.7%. Partly met: 2-5 still 8 over, 6+ 8.5 under; borderline 20% vs WALS 9% (the clitic level reads as borderline whatever its form). L2-strip lever: noise in the harness, dropped. Next: split clitic case into phrasal affix vs postposition when binning, and re-read 6+ on a second seed.
- 2026-11-09: Created from inbox draft draft-language-case-middle-band.md (found by language lane 8 (PW-1586)).
