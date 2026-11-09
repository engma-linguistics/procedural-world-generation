---
title: "Languages: sound-change weights cut while weights did not bite now bite 3-9x harder; review them on the log scale"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: s
impact: low
found_by: lang-weights (PW-1551 lane)
blocked_by: []
relates: [PW-1551]
refs: [planet/language/data/sound_changes.tsv, "planet/language/rules.py::NATURAL_BASE", "planet/language/history.py::RULE_WEIGHT", "docs/review/language/calibration.md#pw-1551-lane-2026-11-08-lang-weights-the-draw-without-redraws"]
---

## Description
In plain words: before PW-1551 a change's "how common" weight hardly changed how often it fired, so earlier lanes cut
some weights hard to fight an overused sound and saw little effect. Now the weight is read on a log scale (each step
of the 1-5 column is 3x), so those cuts take full effect: some changes may now be rarer than the catalogue's own
judgement says.

The rows: S097 (Tocharian-type stop merger) 2 -> 1; S124 (paragoge) 4 -> 1; S142 (prenasalisation) 3 -> 1; S068
(labialisation) 2 -> 1; S221 (secondary palatalisation before i) 3 -> 0.3 (now 0.05 of a middling row, half a "rare"
one); S152 (dark l in the coda) 5 -> 2 (9 -> 0.33: dark l in the coda is among the commonest lateral changes); S086
(retroflexion of r + coronal) 4 -> 2. And `history.RULE_WEIGHT`: tone family 0.3, onset-voicing tonogenesis 0.05,
reduction 0.5, S042 0.15 (also naturalness 1 by `rules.ROW_OVERRIDES`), S073 0.1, which now multiply a weight that
already spans 81x.

**What misleads if never done:** the naturalness column is now what sets frequency, so a reader takes S152's 2 as
"dark l is uncommon"; the column states the overused-segment fixes, not the typology. Nothing breaks: the PW-1551 pass
passes its checks with them as they are.

What I'd try: restore each row to its typological naturalness one at a time in the isolated-lect harness and a full
pass, and fix any overused segment it brings back with an exit row (as S240 did for ɳ) rather than a weight cut.
