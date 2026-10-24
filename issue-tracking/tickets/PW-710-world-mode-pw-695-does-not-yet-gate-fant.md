---
id: PW-710
title: World mode (PW-695) does not yet gate fantasy domestications, because none exist (PW-691)
type: task
status: done
parent: PW-691
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun4
blocked_by: [PW-691]
relates: [PW-695, PW-691, PW-692]
refs: [planet/lineages/spec.py, planet/lineages/horses.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
The world mode (`meta.mode`, `fantasy` | `real`; `planet lineages --mode`) now decides which peoples live (real: only
lines marked `real = true`, i.e. the humans) and drops the fantasy goods (mithril, adamant, star-iron) from the
peoples' land use, the zooms' deposits and the world's `res_x_*` layers (`planet resources --mode real`). The
third piece of PW-695 -- rare, non-Earth domesticated animals and plants in fantasy mode, Earth's only in real mode -- has
nothing to gate: only horses exist (horses.py, a real animal, kept in both modes). When PW-691 lands its
catalogue, mark each entry `fantasy = true` or real and have the mode filter it the same way `real` filters lines
(a flag on the entry, a filter at parse time, a test next to `test_real_mode_keeps_only_the_marked_lines`).
- [ ] domestication entries carry a real/fantasy flag; real mode lists only the real ones
- [ ] viewer/workbench shows the mode on the domestication rows

## Updates
- 2026-10-23: Status todo -> done. Merged: two rare fantasy rows (great elk, riding lizards), off by default, forceable; dropped in real mode.
- 2026-10-24: Built on branch fun6: fantasy rows (great_elk, riding_lizard) are `fantasy = true` in the animal table; `spec.parse` drops them in real mode (`animals`, `animals_force`), `rare` chance when listed in fantasy mode, `animals_force` for tests; the workbench and results show the mode on those rows; test_fantasy_animals_are_off_unless_forced_and_never_in_real_mode.
- 2026-10-23: Created from inbox draft draft-mode-gates-fantasy-domestications.md (found by fun4).
