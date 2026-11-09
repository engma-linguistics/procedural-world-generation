---
id: PW-1570
title: "Languages: free function words run about one segment longer than real ones (you, this/that, and, in: median 4 segments)"
type: task
status: needs-decision
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: med
found_by: language lane (owner question, 2026-11-08)
blocked_by: []
relates: [PW-1537]
refs: [planet/language/lexicon.py, "planet/language/grammar.py (free-word grams)", "run a24559"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: Daniel noticed common little words and add-ons look long. Bound affixes are fine; free grammatical words and some core pronouns are long.

Living lects, a24559 (segments, tone and length marks not counted):
- affixes mean 1.95 (median 2): about right (typical affixes are 1-2 segments).
- clitics 3.0, free grammatical words 3.2 (25% are 4+): long; cross-linguistically function words are overwhelmingly one syllable, 1-3 segments.
- lexicon median segments: I 2, WHAT 2, ONE 2, but YOU 4, THIS 4, THAT 4, AND 4, IN 4, WITH 4 (English you/this/and/in 2-3, Spanish tú/este/y/en 1-4, Swahili wewe/hii/na/ndani). FUNC class mean 4.13 vs nouns 4.91: shorter than nouns, but not by as much as real languages (Zipf; Piantadosi et al. 2011).
- frequency does shorten words (class 1 3.65 vs class 5 4.8), so the slope exists; function words just start too long and don't erode enough.

Likely causes to check: proto function words drawn from the same root-length law as content words; no extra phonetic reduction for unstressed function words (Bybee 2001: high-frequency words reduce faster).
Options: (a) draw proto function words (FUNC, pronouns, deictics) at 1 syllable with CV/VC/CVC shapes; (b) frequency-scaled reduction: unstressed/function words take reductive sound changes (vowel loss, coda loss) at a higher rate; (c) both. Lean: (c), small.
- [ ] owner: (a)/(b)/(c)
- [ ] measure FUNC median segments and the list above; keep the FUNC-vs-noun gap near real-language values

## Updates
- 2026-11-08: Created from inbox draft draft-language-function-words-long.md (found by language lane (owner question, 2026-11-08)).
