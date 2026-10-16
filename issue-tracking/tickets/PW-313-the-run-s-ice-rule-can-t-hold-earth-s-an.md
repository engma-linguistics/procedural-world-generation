---
id: PW-313
title: "The run's ice rule can't hold Earth's Antarctica at today's climate (dT 0): it decays to ~0.1% of the surface"
type: task
status: in-progress
parent: null
subsystem: climate
effort: m
impact: high
found_by: pw308
blocked_by: []
relates: [PW-112, PW-039, PW-308, PW-033]
refs: [planet/tectonics/earth.py, planet/icemass.py, docs/review/audit/pw308-glaciation.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Found while bisecting PW-308. A fixed-planet probe runs the run's ice rule (`earth.ice_sheets`, with glacial
isostasy, every climate update) on Earth's L6 bed at a fixed global dT, starting from Earth's real ice. At dT 0
the ice decays in every code version tried, before and after the physics audit, with and without PW-308's leads:
-32 m / 2.1% of the surface after the first update, then -19, -11, -5, -1, and -0.4 m / 0.1% from the sixth on
(post-audit main; pre-audit main ends at -0.8 m / 0.2%). It takes about dT -6 to keep roughly today's ice
(-44 m / 3.1% with PW-308's leads). So a generated planet's dT 0 is ice-free, and icehouses need ~5 C more
cooling than Earth does.

Why, on Earth's real ice at dT 0: 42% of Antarctica's iced cells have a negative balance (mean -1.2 m/yr). They sit
at a mean -80 deg with ~1.2 km of ice. Their bare-ground summer is +13 C, so the ice surface's warmest month is
-0.8 C, against -13 C observed (PW-112: bare polar lowland summers far too warm; PW-039). Snowfall is ~60-100 mm
on those cells against ~170 mm observed for the ice sheet. The run's ice then sheds its margins, the Nye
surface from the new margins comes out lower (warmer), and the sheet shrinks a little more at each update.

What to try: fix the polar bare-ground summer (PW-112) first, then repeat the probe (script in the pw308
write-up). Today's Antarctica should hold at dT 0 and grow toward the LGM's ~-120 m at around dT -6.
- [ ] Earth probe at dT 0 keeps an ice share near 3% over 8 updates

## Updates
- 2026-10-15: Status todo -> in-progress. Run-lane agent started (polar summers / Antarctica).
- 2026-10-15: Coordinator: also owns PW-240's reopened question (merged draft there, 2026-10-15): after PW-293, seed 11's 3.5 C era reaches -264 m of ice (-370 m total). Fixing the warm polar summers will make ice grow more readily, so re-check cold-era ice depth on the same seeds (PW-240's goal: -150 m typical, -250 m worst) when this lands.
- 2026-10-15: Created from inbox draft draft-run-ice-cannot-hold-antarctica.md (found by pw308).
