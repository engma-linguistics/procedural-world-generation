---
id: PW-1567
title: Second-voice vowels never take part in literal vowel changes (e > i leaves eᴖ alone)
type: task
status: wontdo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: lang-syrinx
blocked_by: []
relates: []
refs: ["planet/language/rules.py::_tonekey", "planet/language/rules.py::lit", docs/review/language/syrinx.md]
created: 2026-11-08
updated: 2026-11-11
---

## Description
In plain words: in bird languages the vowels sung with a second voice (iᴖ, eᴖ...) are frozen. When a sound change
moves e to i, the plain e moves but eᴖ does not, because a rule written with a vowel letter matches a vowel only when
every feature but the first voice's tone is the same, and the second voice is a feature.

Rule matching strips only `tone` (`rules._tonekey`); a literal pattern (`lit`, "e > i", the Great Vowel Shift rows) needs
`source2` and `tone2` equal too. Class rules (V, [+front]) do reach second-voice vowels. Checked on the syrinx lane:
`e > i` turns te into ti but leaves teᴖ and te˦ᴖ˨ unchanged.

What breaks if never done: an aarakocra or kenku lect's second-voice vowels keep their proto qualities for 20 kyr while
the plain vowels shift, so the two series drift apart (an iᴖ with no plain i beside it, a plain e whose second-voice twin
is still the old a). That reads as a second, unchanging vowel system, which no real vowel shift would leave, and it
inflates the vowel inventory of exactly the lects the second-voice tone work made richer.

Fix sketch: strip `source2`/`tone2` (and maybe `register`, growl/purr phonation) in the match key the way tone is, and
carry them through `_make` onto the output, as tone is carried. Needs a check that the hiatus fusion and harmony paths
still treat second-voice vowels as their own quality where they should. Golden outputs will change for syrinx lects only.

## Updates
- 2026-11-08: Created from inbox draft draft-second-voice-vowels-skip-vowel-shifts.md (found by lang-syrinx).
- 2026-11-11: Dropped per the 11-11 assessment: a tiny edge case nobody will see; reopen if a syrinx language shows it.
