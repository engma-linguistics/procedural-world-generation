---
title: "Languages: the phonotactic veto is per draw, so CV languages gain codas within 2.5 kyr"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: lang-realinv
blocked_by: []
relates: [PW-1551]
refs: [planet/language/lect.py::Lect.phonotactic_veto, planet/language/lect.py::Lect.step, "planet/language/lect.py::PHONO_VETO", planet/language/inventory.py::retemplate, tools/language/real_inventory.py, docs/review/language/for-daniel.md]
---

## Description
In plain words: a language built to have only open syllables (Hawaiian- or Swahili-like, every word ending in a vowel) stops being one within about 2,500 years. Real Polynesian and Bantu languages kept that shape for millennia.

Measured with the real-inventory harness (`uv run python -I tools/language/real_inventory.py`, full-toolkit tier, 10 seeds, 2.5 kyr, no contact). Hawaiian and Swahili protos start with 0% closed syllables and 100% vowel-final words. Their daughters reach about 25% closed syllables, and 63-69% of their words end in a vowel. Hawaiian daughters end words in -w 22, -h 19 and -n 18 times (of 86 consonant finals in 300 words). Japanese stays CV only because its stress is "none", so stress-conditioned vowel loss never applies.

Cause. `Lect.phonotactic_veto` turns a shape-breaking change down with probability PHONO_VETO 0.8 per draw. But `Lect.step` makes about 440 draws per 0.5 kyr step (RATE_RULE x RATE_SCALE x 20 generations), and a refused rule stays in the pool. It is drawn again and gets through within an interval or two, so the 80% resistance is close to none per interval. The hiatus family is exempt outright: glide formation S127, S125 and S205 turns -ai into -aj and -au into -aw. And every change that gets through re-templates the lect (`inventory.retemplate`), so the next one is not resisted.

Fix direction: decide the veto once per rule per interval (or per line, with a memory), so 0.8 means 0.8. Also consider whether a glide made from a final vowel should count as a new coda. Then re-check the coda numbers in calibration.md "Sound lane pass 3", since codas came back partly through this leak.

If never done: every CV-language seed (hand-seeded or drawn "simple") drifts toward (C)V(C) in a few thousand years. Families do not keep their syllable type, and the finder's Hawaiian or Japanese look-alikes get rarer as runs get older.
