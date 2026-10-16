---
id: PW-369
title: "Envelope test: the L5 arid share samples one seed's 340-400 Myr window, which one cold era or flooded interval takes out of band"
type: task
status: done
parent: null
subsystem: infra
effort: xs
impact: low
found_by: icehouse-depth
blocked_by: []
relates: [PW-364, PW-338, PW-240]
refs: [tests/test_envelopes.py, docs/review/audit/icehouse-depth.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`tests/test_envelopes.py::test_climate` checks the arid (Koppen B) share of land, averaged over
340-400 Myr of one L5 run per seed, against 12-45%. PW-364 (docs/review/audit/icehouse-depth.md) traced
the 7.7% that PW-338's patch gives seed 1 on the pre-PW-364 code: a genuine geography, not a model
error. A continent drifts over each pole (land poleward of 60 deg: N 52 -> 90%, S 25 -> 87%), ~1.1 km
high, the ocean old (sea_tect -250 m), and the climate drift dips to -4.7 C. A third of the land is iced
(not arid), only ~38% of the land lies below 35 deg, and at 380-400 Myr the young ocean floods the
planet (land 33 -> 27%, land rain 960 -> 1250 mm): low-latitude land is only 10-17% arid (49% at
264 Myr). Arid share every 20 Myr from 100 Myr, patched: 26 29 33 30 30 33 38 36 36 29 25 16 10 10 7 4.

Any change that reshuffles the history re-rolls that window: with PW-364's settled ice the same
patched seed has no icehouse and passes. So the test is fragile to chaos, not a guard of the climate.

Options (the band stays 12-45%):
- A. Average the arid share every 20 Myr over 100-400 Myr (16 samples; patched seed 1 then 24.5%,
  unpatched 26.5%). Costs nothing (the run is there).
- B. A as well as both seeds' mean in the band (one seed may stray, the pair may not).
- C. Keep the window and add seeds until it passes (costs ~1 min per seed; still one window each).
Lean: A. A healthy planet may spend 60 Myr dry-poor; the band asks whether its climate is plausible
over a run, which the 100-400 Myr mean measures.

## Updates
- 2026-10-16: Status todo -> done. Done: arid share averaged every 20 Myr over 100-400 Myr (16 samples), bands unchanged; envelope tests pass (2 min).
- 2026-10-16: Status needs-decision -> todo. Coordinator 2026-10-16: take the lean (average the L5 arid share over 100-400 Myr; bands unchanged): a single-window test is fragile to any history reshuffle.
- 2026-10-16: Created from inbox draft draft-envelope-dry-window.md (found by icehouse-depth).
