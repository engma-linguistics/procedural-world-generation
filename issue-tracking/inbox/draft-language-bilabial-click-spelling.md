---
title: "Languages: how the book spells the bilabial click (px beside the click letters ǀ ǁ ǃ ǂ)"
type: task
status: needs-decision
parent: PW-767
subsystem: culture
effort: xs
impact: low
found_by: lang-lane6
blocked_by: []
relates: [PW-1537]
refs: [planet/language/data/romanization.tsv, "planet/language/romanize.py::spell", "tests/test_language_romanize.py::test_no_ipa_letters_in_spellings", "docs/review/language/sketches/d551-elf.md (pxagǂhabu)", "PW-1537 R7"]
---

## Description
In plain words: click languages here spell four clicks with the Khoekhoe letters ǀ ǁ ǃ ǂ, but the lip click ʘ as "px"
(the house's p + x). A word with both reads as two writing systems at once (elf pxagǂhabu). The cold review (PW-1537
R7) asked for clicks all letters or all digraphs. If nothing is done, every click language with ʘ keeps the mixed look.

Why it is a choice: the obvious letter ʘ is in the IPA block, which the spelling rules bar (no IPA letter in a book or
workbench spelling, `test_no_ipa_letters_in_spellings`); Khoekhoe, whose letters the house uses, has no lip click.

Options:
- A. Keep px (as now). Cheap; mixed look stays.
- B. Allow ʘ as the one IPA letter in spellings (it is also used in some Tuu orthographies). Letters all round; the
  rule against IPA letters gets one exception.
- C. All clicks as digraphs, Juǀʼhoan-style (c ǀ, q ǃ, x ǁ, tc ǂ, and px ʘ). Consistent and ASCII, but c q x then mean
  clicks only in click languages, and the house letters for other sounds collide (x is the velar fricative).
Lean: B (one exception, reads as a click at once).
