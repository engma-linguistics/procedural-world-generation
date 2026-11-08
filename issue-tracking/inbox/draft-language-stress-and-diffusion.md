---
title: "Stress stored per word with a history, and sound changes that spread word by word (lexical diffusion)"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: l
impact: med
found_by: lang-design (sound lanes, 2026-11-08)
blocked_by: []
relates: [PW-982]
refs: [docs/review/language/soundchange-gaps.md, docs/review/language/phonology-gaps.md, docs/review/language/for-daniel.md, docs/review/language/handoff.md, planet/language/rules.py, planet/language/lect.py, planet/language/inventory.py, planet/language/speak.py, tools/language/demo_page.py, tools/language/sketch.py]
---

## Description
In plain words: today a language has one stress rule (first, second-to-last or last syllable) applied to every word,
and every sound change hits every eligible word at once. Real languages have words with their own stress (English
*record* noun vs verb) and changes that creep through the vocabulary, frequent words first, and sometimes stall, leaving
exceptions. Without these, histories are too regular: every correspondence is perfect, which a historical linguist
will notice at once, and stress-driven changes (Verner, Romance stressed-syllable survival, French final stress) cannot
happen.

**Now.** IPA in sketches and pages carries ˈ from the lect's pattern; speech (`/api/speak?stress=`) stresses the right
syllable. Not stored per word; 32% of lects show "no stress" (WALS 14A: free/lexical stress is common, not absent).
`demo_page.py` IPA is not stress-marked. The catalogue rows carry a `scope` field nobody reads.

**Wanted** (soundchange-gaps rec. 5 and 6, phonology-gaps rec. 4 remainder):
- [ ] stressed vowel stored on each form, carried through changes (deletion keeps it, a merged syllable keeps it);
  stress-shift rows (to initial, weight-sensitive, to final after apocope); "none" lects can gain stress
- [ ] a diffusing row spreads over several intervals, frequent words first for reductive changes, and can stall with a
  residue; a small sporadic channel (one-word metathesis, dissimilation)
- [ ] demo page IPA stress-marked
- [ ] sisters/horizon checks re-read after (irregularity lowers measured cognacy)
