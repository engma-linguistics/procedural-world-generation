---
id: PW-1624
title: "Language finder: sparse profiles win by default and long vowels count as vowel qualities"
type: task
status: done
parent: PW-767
milestone: v4
subsystem: peoples
effort: s
impact: low
found_by: lang-realinv
blocked_by: []
relates: []
refs: ["tools/language/find.py::distance", "tools/language/find.py::lect_features", tools/language/data/reference_profiles.tsv, tools/language/real_inventory.py]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: the language finder's "nearest real language" can name the wrong one. Some reference profiles leave fields blank, and those profiles look closer to everything. Separately, a language with long vowels is counted as having twice the vowels it has.

Measured with `uv run python -I tools/language/real_inventory.py` (scores of protos against all 16 profiles):
- **Sparse profiles win.** `find.distance` sums only the terms a profile fills. Black Speech leaves stress, word order, adposition, case and synthesis blank, so it has five fewer terms. It came out "nearest" for 5 of 10 normal human protos, and for most inventory-only Spanish, Swahili, Japanese and Arabic protos. Ranking across profiles (which `--like` does not do, but the harness and any "which real language is this closest to" question does) is biased toward thin profiles.
- **Vowel count.** `lect_features` counts every vowel phoneme (`len(inventory.vowels)`), long and nasal ones included. The profiles count qualities, as the profile file's header says. A Hawaiian-inventory lect reads 10 vowels against 5 (0.44 of its distance), and Arabic 6 against 3.

Fix direction: count vowel qualities in `lect_features` (length and nasality are already series). Normalise the distance by the weight of the terms the profile fills, so profiles are comparable. Or say in find.py's docstring that distances compare lects for one profile, not profiles for one lect.

If never done: the long-vowel count mis-ranks lects with long vowels for `--like hawaiian`, `japanese`, `finnish` and `arabic` (Daniel's language-finder skill). Any "closest real language" readout leans to Black Speech, Klingon and Sindarin.

## Updates
- 2026-11-10: Status todo -> done. Lane 14: the finder counts vowel qualities (length and nasality as series) and scores a sparse profile on the terms it fills (rescaled), so sparse profiles no longer win by default; tests in test_language_find.py.
- 2026-11-10: Owner 11-10: the real-language experiment is a standing benchmark for the language model, like Earth for physics; its gaps are now-work, not later. Moved to v4; lane 14.
- 2026-11-10: Created from inbox draft draft-language-finder-distance-not-comparable.md (found by lang-realinv).
