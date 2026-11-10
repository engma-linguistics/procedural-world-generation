---
id: PW-1623
title: "Languages: words use sounds by world inventory presence, not lexical frequency (a too rare, p/b/d/g/m too common, r and ʔ too rare)"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: peoples
effort: m
impact: med
found_by: lang-realinv
blocked_by: []
relates: []
refs: ["planet/language/inventory.py::_weights", "planet/language/inventory.py::LEXICAL_MANNER", "planet/language/inventory.py::draw_word", tools/language/real_inventory.py, "tools/language/find.py::word_stats", tools/language/data/reference_words.tsv]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: even when a proto is handed a real language's sounds, syllable shapes, stress and word length, its words do not sound like that language. It uses the sounds in the wrong proportions. This is the largest part of what is left of the distance to the real language (the finder's "texture" term, 0.4-1.3 of 1.1-2.9), in all seven languages tried.

Measured with `uv run python -I tools/language/real_inventory.py` (full-toolkit tier, 10 seeds; token shares by the finder's sound classes, ours against the reference word lists):
- /a/ is under-used: Arabic 31% of segments real against 13% ours; Hawaiian 22% against 14%; Spanish o 14% against 7%. i and u run 2-8x the real share (Arabic, Spanish, Mandarin).
- Stops and m are over-used: Japanese b d g p about 0.5% each real, 4-5% ours; Hawaiian p 1.8% against 8%; m 8-10% in every language against 3-6%.
- Approximant r, glottals and other "rare but busy" sounds are under-used: English ɹ 5.8% against 0.6%, Hawaiian ʔ 8% against 1.6%, Arabic ʔ and ħ, Japanese ɾ and h.

Cause: `inventory._weights` weights a segment by LEXICAL_MANNER (approximants x0.45, stops x1.4, nasals x1.2) x sqrt(PHOIBLE presence share / (1 + cost)), and glottals x0.5. A sound's presence across the world's inventories is not its token frequency in a lexicon. i, a and u are all in about 90% of inventories, yet a is the commonest vowel token almost everywhere.

Fix direction: token-frequency priors by sound class (vowel height, manner) from lexical counts (the reference lists are a start; a larger source such as NorthEuraLex or the ASJP word lists would be better), in place of presence shares. Keep the house manner factors only where they are measured.

If never done: every language's texture is flatter and more stop-heavy than real ones. Hand-seeded and drawn languages alike sound "engine-made", and the finder's texture term stays the main reason nothing in a run reads as close to a real language.

## Updates
- 2026-11-10: Created from inbox draft draft-language-segment-token-frequencies.md (found by lang-realinv).
