---
title: "Tone languages end with four tones too often (53-60% of tonal lects); real ones mostly have two"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: s
impact: med
found_by: lang-design (sound lane pass 2, 2026-11-08)
blocked_by: []
relates: [PW-982]
refs: [docs/review/language/for-daniel.md, docs/review/language/calibration.md, docs/review/language/phonology-gaps.md, docs/review/language/soundchange-gaps.md, planet/language/lect.py::tonemes, planet/language/inventory.py, planet/language/data/sound_changes.tsv, planet/language/phonology.py, "run a24559"]
---

## Description
In plain words: a language that has tone gains more tones over its history faster than it loses them. Proto-languages
start with a realistic spread, but today's tone languages are mostly four-tone systems. Real tone languages are mostly
simple two-tone systems (WALS 13A). A reader sees Cantonese-style tone everywhere.

**Now.** Proto draws are fine: 2/3/4/5 tones at 28/31/23/18%. Living tonal lects on a24559 after sound pass 2 (pass G):
2/3/4/5 tones at 8/14/60/16% over all tonal lects (human-voiced 5/13/53/26%). Before pass 2, five tones were the
commonest (51-78%). Tonogenesis rows put contours on short vowels; the new merger rows S227-S232 (rising and falling
level to high, mid merges, extremes merge inward) pull back, but under the functional-load veto (`rules.FL_K`) they
lose. The lane stopped at one nudge.

**Wanted.** Raise the merger rows' weight or soften the veto for tone mergers; tone stability when a vowel is lost
(the tone moves to a neighbour, soundchange-gaps rec. 7); tone loss as a change with stress gained. If never done, every
tonal page reads as a five-tone language family.
- [ ] two- and three-tone systems together at least ~45% of living tonal lects (WALS 13A: simple tone systems
  commonest), across two seeds
- [ ] tonal share stays near WALS 13A ~42% (now 31% humans, 38% all)
