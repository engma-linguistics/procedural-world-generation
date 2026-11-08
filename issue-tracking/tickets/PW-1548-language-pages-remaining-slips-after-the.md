---
id: PW-1548
title: "Language pages: remaining slips after the polish lane (loan family shown as native, 'then' forms unmarked, gods without names, one-vowel god names, odd recipes)"
type: task
status: todo
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lang-design (polish lane, faiths pass 3, grammar D, finish lane, 2026-11-08)
blocked_by: []
relates: [PW-986]
refs: [docs/review/language/for-daniel.md, docs/review/language/demo-read-4.md, tools/language/demo_page.py, tools/language/sketch.py, planet/language/sentences.py, "planet/language/faiths.py::Plan", "planet/language/faiths.py::coin_name", planet/language/texts.py, planet/language/inventory.py, "run a24559"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: a full read of the demo page (demo-read-4.md) found about forty slips; the polish lane fixed them at the
cause, except the ones below. Each is small, but a linguist reading the pages will trip on them, and a few look like
bugs (a god with no name, a word family labelled native that is a loan). Numbers from the polish lane's pass of a24559
(commit c5a5c885).

**Bugs**
- [ ] 8 faith gods are not named by every holder: a name coinage failed (`faiths.coin_name`); find the case and fix it
- [ ] the kobold 'belly' word-family card shows a human proto-form: the word is a loan, and the card does not say so
- [ ] dwarf vowel ä appears in words but is missing from the vowel chart (inventory vs chart; sound lane's files)

**Wording on the pages**
- [ ] history event lines quote a gram's form when it was made (Aliy'unun 2SG.POSS /ŋɨ̞n/ then, /ŋɨ̞ŋ/ now) without
  saying "then"
- [ ] instrument 'with' (free word) and comitative 'with' (COM case) in one language are not explained
- [ ] the polite-address note says "rank is marked in speech" though only population drives it (see the polities draft)
- [ ] complexity tab dates its causes from today's L2, population and isolation; a per-snapshot `l2`/`pop` would date
  them (finish lane)

**Odd but plausible output (decide per item: fix, or leave and explain on the page)**
- [ ] god names worn to one vowel ('A', 'I', 'Ì') after 15-20 kyr; a god name equal to a grammatical marker (Moow)
- [ ] gods whose domain has no word borrow a neighbour's: a desert spirit is 'chief of the fire', a sun spirit 'lord of
  the sky' (add DESERT/SUN-type domain words)
- [ ] many sister lects replace a god's name with the same kind of epithet ('the lord' in four languages)
- [ ] recipes on a people's first crop whatever it is ("How to cook cane ... grind it with a stone")
- [ ] Hawaiian-type kin: cousins called by the BROTHER word only (no sex split of cousins)

## Updates
- 2026-11-08: Created from inbox draft draft-language-page-slips.md (found by lang-design (polish lane, faiths pass 3, grammar D, finish lane, 2026-11-08)).
