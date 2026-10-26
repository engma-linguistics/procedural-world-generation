---
id: PW-313
title: "The run's ice rule can't hold Earth's Antarctica at today's climate (dT 0): it decays to ~0.1% of the surface"
type: task
status: wontdo
parent: null
milestone: null
subsystem: climate
effort: m
impact: high
found_by: pw308
blocked_by: [PW-015]
relates: [PW-112, PW-039, PW-308, PW-033]
refs: [planet/tectonics/earth.py, planet/icemass.py, docs/review/audit/pw308-glaciation.md]
created: 2026-10-15
updated: 2026-10-26
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
- 2026-10-26: Status blocked -> wontdo. Wontdo: merged into PW-462. (PW-900 backlog reorg).
- 2026-10-23: Merged PW-332 (closed as duplicate; PW-597 triage), the same Antarctic snow gap: after the polar bundle (baabbba) the probe's remaining gap is margin snowfall, which is PW-332's subject. PW-332 as left: the cells the probe loses are the Ross and Ronne shelves and WAIS margins (bed clamped at +1 m in the Earth source), at the observed summer temperature (-4.0 vs -4.7 C) with 20-100 mm/yr of snow against ~100-250 mm observed on the shelves and 200-600 on WAIS and coasts. With the sheet's carried air (option A) plus Antarctic snowfall x2.5 (diagnostic) the probe holds ~2.6% (-50 m) over 8 updates; snowfall x2.5 alone gives 1.7%, polar snowfall x3 alone grows the ice to 5.9%. After baabbba Antarctic land 70-80S precipitation is 158 mm (GPCP 210) and Greenland 304 (375): margins still about half of GPCP, owned by PW-015 (storm-track moisture over 55-65S seas at 0.4 of GPCP; rain transport PW-013). Acceptance carried over: Antarctica 70-80S land precipitation within ~30% of GPCP, ice-shelf/WAIS cells >= 100 mm; probe at dT 0 holds ~3% over 8 updates and grows toward ~-120 m at dT -6. Refs from PW-332: tools/ice_probe.py, docs/review/audit/pw313-polar-summers.md.
- 2026-10-16: Status in-progress -> blocked. Polar bundle merged (baabbba): probe at dT 0 holds 2.33% after 8 updates (was 0.10%), still losing ~12 margin cells/update; dT -6 -66 m (target ~-120). Remaining gap is margin snowfall from the storm tracks (PW-015). Health quick: icehouse spells on 4 seeds; seed 2 reaches -340 m at a 3.0 C global (PW-240). earth_check Koppen group 71% unchanged; 60-70N land rain 487 -> 361 (GPCC 424), now too dry.
- 2026-10-16: Polar bundle agent started.
- 2026-10-16: Agent (2026-10-16) found three coupled causes, none merged alone: PW-335 frozen-sea summer air, PW-336 sheet air carried along the winds (option A), PW-332 margin snowfall. Probe: base 0.10%, +A 1.18%, +A + Antarctic snow x2.5 (diagnostic) ~2.6% holds. To land as one polar-climate bundle. Write-up docs/review/audit/pw313-polar-summers.md.
- 2026-10-16: Run lane (pw313): not fixed; nothing merged. Sound temperature fixes (frozen-sea summer air; carrying the sheet's own summer air) bring Earth's polar coasts and Antarctica's coast/WAIS within 0-4 C of observations, but the probe still decays: its losing margins are at the observed summer with ~100 mm/yr of snow (obs 100-500). With carried air + Antarctic snowfall x2.5 it holds ~2.6%. See docs/review/audit/pw313-polar-summers.md and drafts frozen-sea-summer-air, ice-sheet-air-carried (needs-decision), antarctic-margin-snowfall (PW-013).
- 2026-10-15: Status todo -> in-progress. Run-lane agent started (polar summers / Antarctica).
- 2026-10-15: Coordinator: also owns PW-240's reopened question (merged draft there, 2026-10-15): after PW-293, seed 11's 3.5 C era reaches -264 m of ice (-370 m total). Fixing the warm polar summers will make ice grow more readily, so re-check cold-era ice depth on the same seeds (PW-240's goal: -150 m typical, -250 m worst) when this lands.
- 2026-10-15: Created from inbox draft draft-run-ice-cannot-hold-antarctica.md (found by pw308).
