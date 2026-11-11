---
id: PW-1739
title: "Languages: output slips on the first page: 'the the' and numbered place names, random taboo words, rr for every trill, unnamed living families, 6 given names"
type: story
status: done
parent: PW-1736
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lang-assessment
blocked_by: []
relates: []
refs: [docs/review/language/assessment-2026-11-11.html, planet/language/names.py, planet/language/placenames.py, planet/language/personal.py, planet/language/lexicon.py, planet/language/romanize.py, planet/language/sentences.py, planet/language/texts.py, viewer/langview.js]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: cheap, visible defects a reader meets first (assessment 2026-11-11, gaps 4-6). Slam dunks, one lane:
- [ ] strings: 'the land of the named after the the river' (x62, names.py ~622/804 gloss starting 'the'), 'Market The Black Sea' (names.py ~359), 530 numbered names 'Loyings 2..5' (placenames.py ~259: give each a real distinguishing name, e.g. Upper/Lower, by a feature, by a founder)
- [ ] taboo paraphrases motivated per animal (a trait the animal has: the honey-eater, the croaker) and only for wild or dangerous animals, never pigs, cattle or fish scales (lexicon.py ~548 flag, ~1808 random quality)
- [ ] romanization: 'rr' only when the lect also has a tap (romanize.py MERGES ~142, romanization.tsv); one romanization per page for a lect (sentences.py ~148/1026: gram, sentence and paradigm currently differ); readable landmass endonyms
- [ ] living families and languages get names (scholars' glossonyms exist; viewer shows 'fam0', langview.js ~183)
- [ ] 20 given names per lect (plus the API/viewer can ask for more: see the name-generator ticket) and patronymics clipped to a sane length
- [ ] recipes get sequencing ('then', 'until') in texts.py WAYS templates
- [ ] peak and sea names from more than 6/5 adjectives (names.py PEAK_MODS) if PW-1656 has not already replaced them

## Updates
- 2026-11-11: Created.
- 2026-11-11: Lane 19 merged (suite 2165): 'the the' 400 -> 0, numbered names 457 -> 0 (qualifier, feature, then lord's name), doubled words and apostrophes 0, 'rr' in place names 28% -> 3-6% (only with a tap), one book spelling per page (output.Speller), living families and languages named (names.scholars/families/languages), given names 6 -> ~18, patronymic words clipped at 14 letters, recipes with then/until, peak/sea adjectives 16/13. Scanner tools/language/slips.py + test. Matrix identical to baseline on all 8 cells. Taboo item done in lane 20 (merging separately).
- 2026-11-11: Status todo -> in-progress until lane 20's taboo item lands.
- 2026-11-11: Taboo item done in lane 20: paraphrases motivated per animal, only for wild or dangerous animals, and relative to the speakers' size (owner 11-11: dragons and true giants taboo nothing; giant-kin only bear, big cat, crocodile, big snake). All items done.
