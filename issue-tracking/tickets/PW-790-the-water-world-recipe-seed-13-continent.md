---
id: PW-790
title: The water-world recipe (seed 13, continental_start 0.1, heat_start 2) is an always-icebox over 2 Gyr, with or without the brightening star
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: v1-finish-8
blocked_by: []
relates: [PW-780, PW-564, PW-202, PW-576]
refs: [planet/make.py, planet/tectonics/earth.py, docs/review/base-climate/v1-finish-8/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
v1-finish-8 (docs/review/base-climate/v1-finish-8/README.md) ran the water-world preset at L6 over 2 Gyr through
`tools/ice_diag.py`, judged with `passrate2.py` (v1-finish-6's bar on any window):

| draw | 300-2000 icehouse | deep (< -150 m) | dT median | CO2 term 1500-2000 |
|---|---|---|---|---|
| star 0.45, offset 0 / +0.001 / -0.001 | 100 / 86 / 93% | 37 / 40 / 32% | -4.3 / -4.2 / -4.2 | -13.3 / -14.1 / -14.1 |
| star off (star_brightening 0), offset 0 / +0.001 | 93 / 100% | 62 / 59% | -10.1 / -9.9 | -11.4 / -10.9 |

All five are always-icebox. The star is not the cause: it warms the recipe by ~6 C (dT -10 to -4).

What drives it (wwns_0, star off): the raw CO2 source falls ~3x after the 300 Myr frozen reference (9700 at
100 Myr, 8200 at 300, 2900 at 1000, the heat_start 2 mantle cooling) while the sink grows with the emerging land
(land 8% to 30%, sink_raw 57 to 132). With the thermostat's realised global e-folding of ~21-38 K (v1-finish-7),
a ~3x drop in source against sink is met by ~10 C of cooling. That is the mechanism doing what it should with a
fast-cooling mantle; the question is whether the recipe should read as a snowball.

The Earth-like seeds don't do this (source 3500 to 2300, land flat at ~33%).

Options:
- A. Leave the physics alone and re-pick the preset: a `climate_offset` of about +6 (untested) to bring the
  1-2 Gyr dT to the Earth-like runs' +4..+8. That is a recipe change, like the hothouse's 5 to 3.
- B. Treat it as physics: check whether heat_start 2's outgassing decline (x0.35 over 300-1000 Myr) is the right
  size, against a ~x0.5-0.7 per Gyr decline in mantle heat flow usually quoted for an Earth-like planet. If it is
  too fast, slow it (a tectonics change: redo the scorecard and goldens).
- C. Keep it: a water world whose mantle cools fast becomes a snowball. Rename the preset's blurb to say so.

Lean: B first, a short check of the outgassing curve, since a 3x fall in ~700 Myr looks fast. Then A only if the
curve turns out to be right and the owner wants the preset to show emerging land under a living climate.
- [ ] outgassing decline under heat_start 2 measured against a literature heat-flow decline
- [ ] the preset reads as intended (not an always-icebox unless the owner picks C)

## Updates
- 2026-10-24: Status needs-decision -> todo. Coordinator (geophysics delegated): check the outgassing decline (heat_start=2 mantle cooling) first; recipe re-pick only after.
- 2026-10-24: Created from inbox draft draft-water-world-recipe-icebox.md (found by v1-finish-8).
