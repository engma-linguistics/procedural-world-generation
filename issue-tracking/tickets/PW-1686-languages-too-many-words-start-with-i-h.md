---
id: PW-1686
title: "Languages: too many words start with /i/, /h/ and /l/, too few with /m/ and /p/"
type: task
status: done
parent: PW-767
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: coordinator (owner's eye, 2026-11-10)
blocked_by: []
relates: [PW-1641, PW-1647, PW-1642]
refs: ["run a24559", tools/language/data/reference_words.tsv, tools/language/real_inventory.py, "planet/language/lexicon.py::proto_lexicon", planet/language/placenames.py, planet/language/rules.py]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: Daniel noticed many words start with "i" and few start with consonants or clusters. He is right.
Across a24559's 625 living lects (476,594 words), the most common word starts are /l/ 10.9%, /h/ 10.8%, /i/ 8.2%,
/t/ 8.0%; /m/ is 3.1% and /p/ about 1.5%. The repo's real word lists (reference_words.tsv, 11 natural languages,
~50 words each; small sample) start with /m/ 11.6%, /k/ 11.3%, /t/ 7.5%, /i/ 6.5% (3% without Zulu, whose noun-class
prefixes start 46% of its words with i-), /h/ 2.7%, /l/ 3.1%. Labials (m, p, b) are among the commonest word starts
in real languages; ours almost lack them, and h/l are 3-4x too common.

Where it comes from (coordinator's scratch measurements, 2026-11-10):
- /h/, /l/ high and /m/ low are already in the protos (l 11.0%, h 9.4%, m 2.5%): the proto lexicon draw, not drift.
- /i/ grows with time: median lect 3.9% i-initial in protos, 6.9% living; the top lects reach 27-29% (kenku d647,
  lizardfolk d2, human d783.1), 40-50% vowel-initial. Real languages reach that only with Bantu-type i- noun prefixes.
- A third of i-initial living words (13.8k of 40.6k) begin with a derivational prefix of their own lect that starts
  with i (272 of 2,031 prefixing affixes: little, agent, like, place, time...). Prefix draws may favour i.
- Most of the rest are renewed words, not sound change on old ones (proto word and living word unrelated).

What breaks if never done: every language reads alike on the page ("ih", "ili", "hili"), and the real-language
benchmark (PW-1641) does not measure word starts, so nothing catches it.
- [ ] a standing check of word-initial segment shares against the real lists (or a larger reference), living lects
- [ ] /m/ /p/ /b/ word-initially within the real range; /h/ /l/ and /i/ shares down to it
- [ ] no lect over ~20% i-initial unless it has live i- noun-class prefixes

## Updates
- 2026-11-10: Created from inbox draft draft-word-initial-profile.md (found by coordinator (owner's eye, 2026-11-10)).
- 2026-11-10: Lane 16 (merged 15b6fea2): fixed by mechanism. Word-initial weights from NorthEuraLex, lexical diffusion now actually works, h-loss and j-/w-prothesis rows S242-S245. a24559 word starts: l 10.9 > 6.5%, h 10.8 > 6.2%, i 8.2 > 4.8%, m 3.1 > 4.1%, p 2.0 > 3.1%. Lects over 20% i-initial: 39 > 7. Standing check checks.word_starts passes on a24559 and de1cc6; one de1cc6 re-roll still fails on liquids (14.0% against a 10.2% bar).
