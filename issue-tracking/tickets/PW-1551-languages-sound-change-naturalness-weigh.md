---
id: PW-1551
title: "Languages: sound-change naturalness weights barely set how often a change fires (the draw renormalises over the changes that apply)"
type: task
status: needs-decision
parent: PW-767
milestone: later
subsystem: culture
effort: m
impact: med
found_by: lang-sound (sound lane pass 3)
blocked_by: []
relates: []
refs: ["planet/language/rules.py::pick_rule", "planet/language/rules.py::PICK_REDRAWS", "planet/language/lect.py::Lect.step", "planet/language/lect.py::Lect.line_pref", "planet/language/lect.py::REFIRE_KYR", "planet/language/history.py::RATE_SCALE", planet/language/data/sound_changes.tsv, "docs/review/language/calibration.md#sound-lane-pass-3-2026-11-08-evening-coda-drift-and-tone-shares", "scratchpad sound3/codah.py (isolated-lect harness)"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: each sound change in the catalogue has a "how common is this in the world's languages" weight from 1 to
5, but in the simulation a rare change fires almost as often as a common one, as long as the language has the sounds it
needs. So rare, dramatic changes happen on most family lines.

Measured in the isolated-lect harness (48 human protos, 20 kyr): paragoge (S124, a vowel added after every final
consonant) fired 100-190 times at weight 0.3, 1, 2, 4 and 20 alike; only weight 0.01 cut it to 12. The cause:
`rules.pick_rule` sets aside a drawn change that would alter no word and draws again (up to PICK_REDRAWS 16), so the draw
is effectively among the few changes that apply now (about 6.5 no-op draws per pick), and at ~20 picks per lect-kyr
nearly each applicable change fires as soon as its 4 kyr re-fire wait allows. Line drift (lognormal per row and family,
sigma 1.0 and 0.7) widens it further. Pass 3 worked around it for the coda rows (S099 and S124 once per line, a
phonotactic veto) but every other row has the same behaviour.

What misleads if never done: the catalogue's naturalness column, which a reader would take as the frequency of each
change, is close to ignored; rare one-off changes (total final consonant loss, paragoge, Tocharian-type stop mergers
before they were made one-offs) recur across most lines, which is part of why so many one-off lists and caps exist.

Options:
- A. Draw without conditioning (PICK_REDRAWS 1) and raise RATE_SCALE so the applied rate holds (harness: RATE_SCALE ~25
  with PICK_REDRAWS 1 gives 10 applied changes per lect-kyr against 12 now). Weights then set rates directly. Moves the
  horizon and every per-segment share; a full recalibration pass.
- B. Keep the draw; read naturalness as how many lines ever have a row (a per-line availability draw, p = weight/5),
  which works inside saturation. Smaller change, but a new mechanism on top of line drift.
- C. Leave it; keep adding one-off ids and caps where a row misbehaves.
Lean: A, as its own lane with a full pass, since it removes caps rather than adding them.

## Updates
- 2026-11-08: Created from inbox draft draft-language-rule-weights-saturate.md (found by lang-sound (sound lane pass 3)).
