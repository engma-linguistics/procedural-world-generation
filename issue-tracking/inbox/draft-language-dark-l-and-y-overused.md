---
title: "Languages: ɫ and y in 16-20% of living lects since codas came back (overused-segments check fails)"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: s
impact: med
found_by: lang-sound (sound lane pass 3)
blocked_by: []
relates: []
refs: [planet/language/checks.py, planet/language/data/sound_changes.tsv, tools/language/knowledge_tables.py, planet/language/inventory.py::phonemic, planet/language/inventory.py::ALLO_TESTS, planet/language/history.py, planet/language/rules.py::SAME_AS, docs/review/language/calibration.md#sound-lane-pass-3-2026-11-08-evening-coda-drift-and-tone-shares, "scratchpad sound3/passK (a24559 scratch output)", "scratchpad sound3/codah.py"]
---

## Description
In plain words: after the sound lane brought word-final consonants back (pass 3), two sounds that are rare in the
world's languages became common in ours: "dark l" ɫ (as in English "feel", but here a separate sound of the language)
in 16.5% of living lects against 0.7% in PHOIBLE, and the rounded front vowel y (German ü) in 20% against 5%. The
"overused segments" check fails on a24559 (pass K); every other check except the horizon passes.

Where they come from: S152 (l > ɫ in the coda) and i-umlaut (S135; its demo twin is now deduplicated). Both are
introduced often but, in the isolated-lect harness (no contact between lects), fold back: ɫ 2.3% and y 2.9% of harness
leaves. Weight cuts (S152 5 -> 2) did not move the full run, so the surplus comes from what the harness lacks: wave
adoption of the change between neighbouring lects, or long lines where the conditioning context (a final vowel after
umlaut, an l before a vowel after dark l) is lost and the sound phonemicizes. Dark l in the coda should mostly stay an
allophone (inventory.ALLO_TESTS has a "coda" test), so check why it phonemicizes: likely apocope or the new syncope rows
put a plain l in the coda after S152 ran, so l and ɫ contrast.

What misleads if never done: the overused-segments check stays red, and a fifth of all languages read as
German/Albanian-like in their vowels and laterals.
- [ ] find which path keeps ɫ and y (wave adoption vs phonemicization; `gain.py`-style tracing of the first lect on each
  line that has them in a full pass)
- [ ] fix at the cause (e.g. dark l as a live allophonic rule rather than a lexical rewrite, or an exit row), then the
  overused-segments check passes on a24559.
