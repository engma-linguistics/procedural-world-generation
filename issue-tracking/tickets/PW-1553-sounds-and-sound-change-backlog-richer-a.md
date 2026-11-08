---
id: PW-1553
title: "Sounds and sound-change backlog: richer allophony, geminates, vowel re-dispersion, bigger clusters, long-distance rules, a reconstruction step, phrase sandhi"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: xl
impact: med
found_by: lang-design (phonology and sound-change coverage reviews, sound lanes, 2026-11-07/08)
blocked_by: []
relates: [PW-982, PW-1423, PW-983]
refs: [docs/review/language/phonology-gaps.md, docs/review/language/soundchange-gaps.md, docs/review/language/audio.md, docs/review/language/for-daniel.md, planet/language/inventory.py, planet/language/rules.py, planet/language/lect.py, planet/language/phonology.py, planet/language/speak.py, tools/language/sketch.py]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: the two sound reviews (phonology-gaps.md, soundchange-gaps.md) ranked what real sound systems and
sound histories have that the generator lacks. The items needed before the merge are done (series-based inventories,
tone counts in protos, stress in IPA and speech, dragon sub-bass, line drift, staged chain shifts, missing common
changes, live phonological rules). Coda drift, tone counts and stress/diffusion have their own drafts. This is the rest,
as one backlog to pull from. If never done, the sound systems stay a little too regular and too uniform: for example
real languages almost all have several allophones, ours 27% (11-04 run).

From phonology-gaps.md §6 (rank):
- [ ] 9 richer allophony (aspiration in stressed onsets, flapping, affrication before high vowels, vowel reduction,
  l-darkening); phonemic and phonetic forms side by side; speak the phonetic form
- [ ] 10 geminates: 18% of protos -> 1% living (find the one-way rows); treat CC of one consonant as a geminate
- [ ] 11 boundary morphophonology beyond the live rules (English -s/-ɪz, consonant gradation, rendaku)
- [ ] 12 onsets and codas of 3-4 in "complex" lects; syllabic sonorants
- [ ] 13 vowel re-dispersion after change (35% of lects had two qualities closer than the draw's floor; WALS 2A skew
  toward 7+ qualities)
- [ ] 14 syllable weight, moras and pitch accent (Japanese, Swedish types)
- [ ] 15 clicks root-initial, more accompaniments, click-vowel constraints
- [ ] 17 root-and-pattern morphology (shared with grammar)
- [ ] 18 audio: per-lect eSpeak voice choice for uvulars/pharyngeals/retroflexes, syllable boundaries, downdrift

From soundchange-gaps.md §6:
- [ ] 8 long-distance contexts and identity in the parser (Grassmann S091-S094, haplology S106, Meinhof, Dahl)
- [ ] 10 a reconstruction step: correspondence sets and an asterisked proto per scholars' clade beside the true proto;
  rename the sketch's "reconstructed ancestor" to "true ancestor"
- [ ] 11 phrase sandhi with a history (fixed phrases as single forms, Celtic mutations when the trigger erodes)
- [ ] 12 analogy in the lexicon (level derived words to their base; S183/S184-type extension)
- [ ] 13 inventory folds listed in the sketches (old and new sound) so a tenth of events are not unexplained mergers
- [ ] 15 syllabic consonants (ṛ > ri/ru)
- [ ] the unmerged helper branch `worktree-agent-a394b320cf12664f2` (an alternative take on SC items 1-4 and a draft on
  catalogue saturation): read once for anything worth keeping, then delete the branch

## Updates
- 2026-11-08: Created from inbox draft draft-language-sound-backlog.md (found by lang-design (phonology and sound-change coverage reviews, sound lanes, 2026-11-07/08)).
