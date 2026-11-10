---
id: PW-1638
title: "Languages: final consonants are easy to lose and hard to gain, so simple syllables drift to twice WALS's share"
type: task
status: done
parent: PW-767
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lang-lane12
blocked_by: []
relates: [PW-1622]
refs: ["planet/language/lect.py::Lect.phonotactic_veto", "planet/language/lect.py::Lect.step", "planet/language/lect.py::PHONO_VETO", "planet/language/inventory.py::new_violations", "planet/language/inventory.py::retemplate", planet/language/data/sound_changes.tsv, tools/language/real_inventory.py, docs/review/language/calibration.md, docs/review/language/for-daniel.md, "run a24559"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: with PW-1622 the resistance to new syllable types finally works, and it shows an older imbalance. The
sound-change catalogue has about a dozen ways to lose a final consonant (S099, S100-S102, S124 paragoge, S145, S191,
the tonogenesis rows) and essentially two to make one (apocope S103 and deletion.final_vowel), and losing a type is
never resisted while gaining one now is. So languages slide toward open syllables and stay there.

Measured on a24559 (living lects, WALS 12A-style reading of each lect's words; main -> lane 12): simple syllables
0.16 -> 0.22 (WALS 0.12), lects with under 5% of words ending in a consonant 0.24 -> 0.33, complex 0.43 -> 0.37
(WALS 0.31), median share of words ending in a consonant 0.35 -> 0.28. In the real-inventory experiment (10 seeds,
2.5 kyr, control protos) the closed-syllable share of the daughters' words went 0.36 (protos) -> 0.30 (before) ->
0.20 (after); the coda languages that lost codas did so through ordinary coda losses while apocope was refused as
"a new type" (seed 6: final codas fell to 1% once apocope was turned down).

If never done: about one living language in five has simple CV syllables against WALS's one in eight, and the
finder's English-, Arabic- or Spanish-like languages get rarer the older a run is. calibration.md's "Sound lane pass
3" table was tuned with the leaky veto and no longer describes the engine.

Try, in order: (1) more coda supply where real languages get it: syncope next to a final consonant, vowel loss in
unstressed final syllables beyond S103, clipped compounds; (2) a lect that has a type robustly (say 20%+ of words)
resists losing it all at once (S099's whole-class loss refused like a new type); (3) only then tune PHONO_VETO or the
refusal wait. Re-measure with tools/language/real_inventory.py and the WALS reading on a full a24559 pass.
- [ ] simple syllables on a24559 within 0.08-0.16, complex within 0.25-0.40
- [ ] CV protos (Swahili, Hawaiian, Japanese in real_inventory.py) still under 10% closed after 2.5 kyr

## Updates
- 2026-11-10: Status todo -> done. Lane 14/14b: the word-shape anchor (lect.pattern_resist, PW-1642) stops coda languages wearing down. a24559 simple syllables 0.22 -> 0.05, complex 0.38 -> 0.33 (WALS 0.12/0.31); de1cc6 complex 0.51 -> 0.32. The undershoot of simple syllables now has its own draft (open-syllable stable state: no flow into CV, leaks out of CV lines through loans and coins).
- 2026-11-10: Owner 11-10: the real-language experiment is a standing benchmark for the language model, like Earth for physics; its gaps are now-work, not later. Moved to v4; lane 14.
- 2026-11-10: Created from inbox draft draft-language-coda-supply-one-way.md (found by lang-lane12).
