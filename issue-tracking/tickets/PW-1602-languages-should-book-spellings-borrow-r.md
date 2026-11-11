---
id: PW-1602
title: "Languages: should book spellings borrow real-world looks (Polish sz cz, Czech š č, German sch) or invented ones?"
type: task
status: done
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: low
found_by: language lane 7 (PW-1546)
blocked_by: []
relates: [PW-1546]
refs: ["planet/language/romanize.py::LETTER_STYLES", "planet/language/romanize.py::LETTER_W", "planet/language/romanize.py::LENGTH_W", "planet/language/romanize.py::Orthography._styled", "planet/language/history.py::History.make_proto", docs/review/language/names-spelling-gaps.md, docs/review/language/for-daniel.md]
created: 2026-11-09
updated: 2026-11-11
---

## Description
In plain words: each language family now has its own way of writing its words in the book spelling, picked when the
family begins and kept by its daughters (with an occasional spelling reform). The eight "looks" are modelled on real
spelling traditions: English-like (sh ch y), Czech-like (š č ž, ch for the kh sound), Polish-like (sz cz ż), German-like
(sch tsch), Basque-like (x tx tz), Turkish-like (ş ç c), French-like (ch j gn) and Swedish-like (sj tj j); long vowels
are doubled (aa), take a macron (ā) or an acute (á). So two related languages now look alike on the page and two
unrelated ones look different, which was the point of names-spelling-gaps.md item 12.

**What misleads if never decided:** a reader may take a Polish-looking fantasy language as "the Slavic one", since the
look carries real-world associations the history does not have.

Options:
- **A (as built): real-world looks.** Readable at once (a reader knows how to say sz or š), and the variety is real.
  The associations come along.
- **B: invented looks.** The same mechanism with letter sets no real language uses as a whole (e.g. ʃ as "xh", tʃ as
  "tc", length as a following h). No associations, but harder to read aloud and they can look like a cipher.
- **C: real looks, renamed and mixed.** Keep the letters but mix two traditions per family (Polish consonants with
  Turkish length), so no family looks like one real language.

Lean: A. Real orthographies are the best-tested answer to "how do I write ʃ in Latin letters", and the house style is
still the commonest (30% of families). The weights (`LETTER_W`, `LENGTH_W`) are taste calls either way.

## Updates
- 2026-11-09: Created from inbox draft draft-language-spelling-traditions-look.md (found by language lane 7 (PW-1546)).
- 2026-11-11: Done: the owner answered the Language Desk card o.looks 'real' (11-10); book spellings borrow real-world looks.
