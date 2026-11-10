---
id: PW-1613
title: "Languages: growled voice is written on every sound of a syllable (w‼ɔ‼j‼); mark it once per syllable on the page, or make it a syllable feature?"
type: task
status: done
parent: PW-767
milestone: null
subsystem: culture
effort: m
impact: low
found_by: language lane 9 (PW-1537 R6)
blocked_by: []
relates: [PW-1537]
refs: [planet/language/percepts.py, "planet/language/percepts.py::page_growl", "tools/language/sketch.py::render", "tools/language/demo_page.py::build", tests/test_language_percepts.py, "planet/language/percepts.py::word_ipa", "planet/language/percepts.py::from_ipa", planet/language/romanize.py, tools/language/demo_page.py, tools/language/sketch.py, docs/review/language/sketches/d48-blue-dragon.md, "run a24559"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: dragon languages have a growled voice (written ‼). The engine stores it on each sound, so a growled
syllable reads w‼ɔ‼j‼ 'dog' (blue dragon). A linguist would write the growl once for the syllable, as voice quality
is a property of a syllable or word in the human languages that have it (the cold review, PW-1537 R6). This is the
last open R6 item; lane 5 already stopped counting ‼ as non-human in the sketches.

**What misleads if never done:** dragon pages keep reading as clumps of marks (w‼ɔ‼j‼, thurhdeïkhomhwïnerhḷ in the
old book spelling); a reader takes the notation for a bug. Nothing is wrong in the sounds themselves.

Options:
- **A. Page-only notation (small).** In the demo and sketch IPA, a syllable whose voiced sounds are all growled shows
  one ‼ after its vowel (wɔ‼j); a syllable with a growl on only some sounds keeps the per-sound marks. The stored
  data and the IPA round-trip stay per sound. Cost: two notations side by side (pages vs data and the viewer).
- **B. Growl as a syllable feature (bigger).** A sound change that growls a vowel growls its syllable's voiced
  margins too, and one that clears it clears them, so a syllable is all growled or not at all; then the writer marks
  it once per syllable and the reader spreads it back (`word_ipa` / `from_ipa`). Cost: a percept-model change that
  touches the dragon inventories, sound changes and speech; needs a pass over the dragon lects.
- **C. Leave it.** Per-sound marking is precise and the voice-quality symbols allow it.

Lean: A. It answers the review at page level without touching the model; B only if the dragons' growl should
behave as a register in sound change too.

Coordinator call 2026-11-09: A (page-only, one mark per fully growled syllable); B only if a later lane wants the growl to act as a register in sound change.

## Updates
- 2026-11-09: Status todo -> done. Lane 10 (lang-lane10): option A done. percepts.page_growl writes one ‼ after the vowel of a syllable whose voiced sounds are all growled (w‼ɔ‼j‼ -> wɔ‼j; sa‼n‼ -> sa‼n); partly growled syllables keep per-sound marks; applied to the whole demo page body (demo_page.build) and every sketch page (sketch.render); the mark keys say 'one ‼ after a vowel growls its whole syllable'. Data, word_ipa and from_ipa stay per sound; audio reads the data. d48/d116 sketches re-noted. Test: tests/test_language_percepts.py::test_page_growl_marks_a_fully_growled_syllable_once.
- 2026-11-09: Created from inbox draft draft-language-growl-per-syllable.md (found by language lane 9 (PW-1537 R6)).
