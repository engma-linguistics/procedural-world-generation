---
title: "Languages: words, grams and paradigms now carry only the book spelling; the workbench's full spelling for them is gone"
type: task
status: needs-decision
parent: PW-1736
subsystem: culture
effort: s
impact: low
found_by: lang-lane19
blocked_by: []
relates: [PW-1739]
refs: [planet/language/output.py::Speller, planet/language/sentences.py::book_spelling, planet/language/romanize.py, viewer/langgram.js, docs/review/language/for-daniel.md]
---

## Description
In plain words: one lect's page used to show three spellings (the full "workbench" spelling for words, grams and
paradigms; the book spelling for sentences and names). Lane 19 made them all the book spelling (output.Speller), so a
page reads alike. The full spelling (tone marks, è for ɛ, ř for ɹ) is still there for names (`roman_full`) but no longer
for words, grams or paradigm cells. The IPA sits beside every one of them.

What misleads if never decided: a reader who wants the exact contrastive spelling of a word (tone, open e) has only the
IPA; tools that searched the full spelling (find.py by letters) now match book letters.

Options:
- A (now): book everywhere, IPA beside it. Simple, one spelling per page.
- B: add a `roman_full` column to the lexicon only (about +2 MB on a24559) and a toggle in the grammar tab.
- C: revert words to full, keep grams/paradigms/sentences book (two spellings again).
Lean: A, B only if Daniel misses the full spelling.
