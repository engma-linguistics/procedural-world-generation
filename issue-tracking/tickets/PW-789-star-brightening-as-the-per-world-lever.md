---
id: PW-789
title: "Star brightening as the per-world lever: expose it to the user (form + docs), and what it can and can't do per seed"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: v1-finish-8
blocked_by: []
relates: [PW-780, PW-761, PW-564, PW-481]
refs: [planet/make.py, planet/tectonics/params.py, planet/tectonics/earth.py, docs/review/base-climate/v1-finish-8/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
The owner (2026-10-24): for Earth-like worlds, no ice ages at all counts against the bar. The star's brightening is
the one external lever per world: slower for worlds that never ice, faster for icy ones. v1-finish-8 measured it
(docs/review/base-climate/v1-finish-8/README.md, sections 4-5).

Strict tallies (never-ice < 5% fails):
- L6 1 Gyr at 0.45: 13/18 (v1-finish-7's draws, against 16/18 lenient).
- L7 1 Gyr: 7/8.
- L6 2 Gyr Earth-like: 6/7 (whole run).
- L7 2 Gyr: 1/2. Seed 12 is never-ice at 0.9% over 300-2000. Both L7 draws are ice-free at 1500-2000, dT +9.1 / +7.4.

A lower rate on the three never-ice draws (L6 1 Gyr; icehouse % at 0.45 / 0.2 / 0.1 / 0):
- 53669: 5 / 28 / 11 / 46;
- 583167: 0 / 60 / 12 / 11;
- 957317: 11 / 44 / 57 / 45.

So the rate shifts dT by ~2-4 C, but the share each seed lands on is chaotic: two of three draws overshoot past 40%
at some lower rate. `star_age` can't be the lever: an older star brightens faster in relative terms (+5.6 / +6.4 /
+7.9 C at 1 Gyr for star_age 0 / 2000 / 4570).

Options:
- A. Expose `star_brightening` in the New planet form (planet/make.py SETTINGS, range 0-1, default 0.45). Help text,
  for example: "How fast the star brightens, as a multiple of a Sun-like star. Slower gives a cooler late history
  with more ice ages; faster gives a warmer one. 0.45 is a K-type star (~0.75 solar masses); 1.0 is Sun-like and
  usually melts out all ice within ~1 Gyr." Docs: the README's parameter list and overview.md's climate section say
  it is a world-builder choice. It moves the climate a few C, like climate_offset; it doesn't pick a seed's ice
  history.
- B. A, plus recipe presets that set it (e.g. a "cool star" Earth-like at 0.2). This adds no new mechanism.
- C. Keep it a `--set`-only parameter for v1 (it already works there), and document it in the README only.

No auto-tuning, per the owner. Lean: A. It is cheap and honest: the docs say it is a climate-temperature knob, not an
ice-age-count knob.

Also open, owner call: L7 runs warmer than L6 late in 2 Gyr runs (two draws). If 2 Gyr L7 runs matter for v1, the
2 Gyr presets (water world, Earth-like B at 1500) could set a slower star, or the default could drop. It needs more
L7 draws than this lane's budget (~1.5 h per 2 Gyr L7 run).
- [ ] owner picks A / B / C
- [ ] if A or B: SETTINGS entry and docs; test_make still green

## Updates
- 2026-10-24: Coordinator lean: expose in the New planet form as a warmer/colder knob, not an ice-age picker; asked owner.
- 2026-10-24: Created from inbox draft draft-star-brightening-per-world-lever.md (found by v1-finish-8).
