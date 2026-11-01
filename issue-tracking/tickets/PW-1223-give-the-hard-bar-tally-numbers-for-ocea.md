---
id: PW-1223
title: Give the hard-bar tally numbers for "ocean loss" and "CO2 crash" and make the tally a tool
type: task
status: todo
parent: null
milestone: v1
subsystem: infra
effort: s
impact: med
found_by: lane92
blocked_by: []
relates: [PW-932, PW-825]
refs: [docs/review/v1-cut/tally.py, docs/review/base-climate/v1-finish-12/passrate4.py]
created: 2026-10-31
updated: 2026-10-31
---

## Description
The owner's two-tier bar (2026-10-30) names four hard failures: frozen over, boiled, oceans lost, CO2 crash. Only
two have code and numbers: frozen over (40% of land under ice inside `ice_criteria.hard_window`) and boiled
(`passrate4.judge` hellhouse: dT median above +10.5 C or max above +15.5 C). Lane 92 had to define the other two to run
the tally, in `docs/review/v1-cut/tally.py`:
- ocean loss: the ocean's share of the surface (1 - land) below 40% at any step after 300 Myr, or |sea level| above
  1000 m at any step. (The sim has no water sink, so this is mostly a sanity guard; it was 0 of 40 draws.)
- CO2 crash: pCO2 below 100 ppm at any step after 300 Myr.
These are lane 92's choices, not the owner's. Options: A keep them as the tag-time definitions and move the script to
`tools/hard_bar.py`; B the owner or coordinator sets different numbers (for example a crash as a drop of 8-fold in
under 50 Myr, as PW-1156 describes); C drop the two terms because the sim cannot lose water and the end-pCO2 band
is already a diagnostic. Lean: A now, B when the CO2 crash draft (draft-l6-co2-crash-639472-roll001) is ruled on.
- [ ] a ruling or a note on each definition
- [ ] the tally script moved under tools/ and linked from the playbook's PW-932 line

## Updates
- 2026-10-31: Status needs-decision -> todo. Owner 10-31 D32 = B: 'chase the science not a hard value'. A CO2 crash = pCO2 below the plants' own compensation point (vegetation._gstar at the draw's temperature). One collapse in 42 is acceptable to him; 85 ppm passes. Lane 102 moves the tally to tools/hard_bar.py.
- 2026-10-31: Plant floor merged; full min-pCO2 list in docs/review/v1-cut/plant-floor.md. Crash line put to Daniel as D32 on the owner's desk.
- 2026-10-31: Created from inbox draft draft-hard-bar-definitions.md (found by lane92).
