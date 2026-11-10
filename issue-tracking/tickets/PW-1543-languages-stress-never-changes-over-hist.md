---
id: PW-1543
title: "Languages: stress never changes over history and is never stored per word; sound changes never spread word by word"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: m
impact: med
found_by: lang-sound (sound lane pass 3)
blocked_by: []
relates: [PW-982]
refs: ["planet/language/rules.py::stressed_vowel", "planet/language/rules.py::weight_stress", "planet/language/inventory.py::STRESS", "planet/language/inventory.py::stress_marked", "planet/language/lect.py::Lect.step", planet/language/lexicon.py, planet/language/history.py, tools/language/sketch.py, planet/server.py, "docs/review/language/calibration.md#sound-lane-pass-3-2026-11-08-evening-coda-drift-and-tone-shares", docs/review/language/soundchange-gaps.md, docs/review/language/phonology-gaps.md, "Hayes 1995 Metrical Stress Theory", "Wang 1969 lexical diffusion"]
created: 2026-11-08
updated: 2026-11-09
---

## Description
In plain words: every word of a language gets its stress from one fixed rule that the language keeps for its whole
history, and every sound change hits all its words at once. Real languages move their stress (Proto-Indo-European free
stress became fixed initial stress in Germanic, penultimate in Polish), end up with stress that has to be learned word
by word (Russian, Spanish exceptions, English), and many changes spread a word at a time, frequent words first or last.

What is there now (sound lane pass 3): each lect has one stress pattern: initial, penult, final, "weight" (the Latin
rule, new in pass 3: penult when heavy, else antepenult) or "none" (no word stress: tone languages, French-type phrase
prominence). The pattern is drawn for the proto (WALS 14A) and never changes; a shifting people keeps its stress
(history.py). There is no per-word stress, and sketch pages still say "the engine has no word-by-word lexical stress".

What misleads if never done: stress-conditioned changes (apocope, syncope, reduction, open-syllable lengthening) apply
by one rule for 20 kyr, so whole families share a stress pattern their real counterparts would have lost; a linguist
reading the pages sees no family where stress moved, and every sound change is perfectly regular (no residue, no
doublets).

Work:
- [ ] stress shift as a rare history event (free/weight -> initial or penult; fixed -> another fixed), recorded as a change;
- [ ] per-word stress for lects whose stress became unpredictable (a stress shift plus apocope or syncope leaves old
  stress positions as lexical; store the stressed syllable on the word: needs a field in lexicon.py, the polish lane's
  file), used by rules.apply through the stress_index callable it already accepts, by stress_marked and by speech;
- [ ] lexical diffusion: a change marked diffusing reaches a share of its words per step, frequent words first for
  reductions and lenitions, last for analogical levelling (Phillips 1984), finishing or stalling (residue).

## Updates
- 2026-11-09: Language wrap-up 11-09: realism polish, parked as later (owner: language good enough to move forward).
- 2026-11-08: Created from inbox draft draft-language-lexical-stress-and-diffusion.md (found by lang-sound (sound lane pass 3)).
