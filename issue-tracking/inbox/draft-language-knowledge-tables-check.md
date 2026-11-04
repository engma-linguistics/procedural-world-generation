---
title: Spot-check the hand-written sound-change and grammaticalization tables before the generator leans on them
type: task
status: todo
parent: null
subsystem: culture
effort: s
impact: low
found_by: lang-design reference-data gatherer
blocked_by: []
relates: [PW-1423]
refs: [planet/language/data/sound_changes.tsv, planet/language/data/grammaticalization_paths.tsv, tools/language/knowledge_tables.py, docs/review/language/reference-data.md]
---

## Description
In plain words: two of the language reference tables (185 sound changes, 72 grammaticalization paths) were written from the agent's memory, not downloaded. The naturalness weights, frequency classes and the real-language examples are judgement. A few examples are flagged weak in the row (S156 χ > ħ, the Cʔ > Cʼ ejective row, K'iche' chuxe', Tibetan -thong). If they are never checked, a generated language's "etymology notes" or a viewer tooltip could quote a wrong real-world example as fact, and the generator's weights would rest on unreviewed numbers.

Fix: one pass (a Sonnet reviewer with web access is enough) over the example column against a textbook or Wikipedia, correcting or dropping the doubtful ones, and confirming the naturalness weights are in a sane order. Edit `tools/language/knowledge_tables.py` and regenerate.
