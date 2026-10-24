---
title: World mode (PW-695) does not yet gate fantasy domestications, because none exist (PW-691)
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun4
blocked_by: [PW-691]
relates: [PW-695, PW-691, PW-692]
refs: [planet/lineages/spec.py, planet/lineages/horses.py]
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
