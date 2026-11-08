---
title: "Most languages end nearly every word in a vowel (64-70% of lects vs ~12% real); then re-derive each lect's syllable rules from its words"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: m
impact: high
found_by: lang-design (sound lane pass 2, 2026-11-08)
blocked_by: []
relates: [PW-982]
refs: [docs/review/language/for-daniel.md, docs/review/language/calibration.md, docs/review/language/phonology-gaps.md, docs/review/language/soundchange-gaps.md, docs/review/language/handoff.md, planet/language/inventory.py, planet/language/rules.py, planet/language/lect.py, planet/language/data/sound_changes.tsv, tools/language/sketch.py, "run a24559"]
---

## Description
In plain words: almost every language the generator makes drifts toward words that end in a vowel, like Hawaiian or
Japanese. Real languages mostly keep some final consonants. A linguist opening the pages sees two thirds of the world's
languages with the rarest syllable type. And the syllable rules each page prints ("max onset 2, codas l n s") are frozen
from the proto-language, so they no longer describe the words beside them.

**Now.** On a24559 (scratch passes E-G, sound lane pass 2), in 64-70% of living lects fewer than 5% of core words end in
a consonant; WALS 12A puts simple (C)V-only languages at about 12%. Cause: final-consonant loss rows outweigh the ways
codas come back (vowel apocope, syncope, borrowed codas); see calibration.md "Pass 2". The sound lane wrote a
phonotactics re-check (re-read the lect's templates from its words) and dropped it, because it moved 419 of 620 lects to
"no codas" and so fed the drift (calibration.md pass F).

Also stale since the proto draw (phonology-gaps 5.2, 5.3, rec. 7): `shapes`, `max_onset`, `max_coda`, `coda_class` in
`inventory.py` never update; ŋ was word-initial in 276 of 277 human lects that have it (WALS 9A about 38%, 11-04 run,
re-measure); clicks, h and ʔ take no positional limits.

**Sound pass 3 (lang-sound, running 11-08 evening) has the coda balance as its first item.** If it lands with the share
in range, close the first box and keep the rest.

**Wanted.**
- [ ] living lects with fewer than 5% consonant-final core words: under ~25% (WALS 12A simple about 12%), across two
  seeds; levers: weight of final-consonant loss rows vs apocope/syncope rows in `data/sound_changes.tsv`, a "lect has
  codas" conspiracy in `inventory.repair`
- [ ] the phonotactics re-check back in (templates re-derived from words after history, shown in the sketch)
- [ ] per-segment positional limits in `inventory.legal` / `draw_word` (initial ŋ near WALS 9A; clicks mostly
  root-initial)
- [ ] horizon and sisters checks not worse than the pre-change pass
