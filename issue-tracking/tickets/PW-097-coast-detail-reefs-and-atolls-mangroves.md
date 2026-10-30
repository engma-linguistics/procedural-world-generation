---
id: PW-097
title: "Coast detail: reefs and atolls, mangroves, barrier islands, cliffs vs beaches"
type: story
status: todo
parent: PW-090
milestone: v2
subsystem: coast
effort: l
impact: med
found_by: daniel
blocked_by: []
relates: [PW-004, PW-077]
refs: [planet/coast.py, planet/zoom/regional.py]
created: 2026-10-14
updated: 2026-10-23
---

## Description
Coral reefs and atolls in warm, clear water (atolls on subsiding volcanic islands: ties to PW-004 in the
volcano epic), mangroves on tropical sheltered coasts, barrier islands on wave-dominated low coasts, and
cliffs vs beaches by rock strength and wave power. See also PW-077 (spits, beach ridges, tidal channels).

## Updates
- 2026-10-23: Coast-detail lane: stage 1 built (planet/coastform.py: coast_type classes, barrier/cliff scores, seabirds, seals,
  nav_hazard; `planet coast <world>`; viewer layers, summary; tools/coast_check.py 26/32 on Earth). Stage 2 in part
  (planet/zoom/coast.py: shore classes, barrier islands with inlets and lagoons, colonies, hazards; `planet coast
  zoom:<id> [--terrain]`). Proposal docs/proposals/coast_detail.md; 4 inbox drafts.
- 2026-10-23: Milestone null/later -> v2 (PW-597 triage, coordinator, 2026-10-23): coastal detail (reefs, atolls, mangroves; coastal life) is v2.
- 2026-10-14: Rescoped (backlog housekeeping): coast form only (cliffs vs beaches, spits, beach ridges, tidal channels, barriers beyond coastal plains); absorbs PW-077. Reefs, mangroves, kelp, seagrass belong to PW-188.
- 2026-10-14: Atolls, barrier and fringing reefs on subsiding volcanoes are now drawn by the zoom (PW-004, zoom_volcanoes.py); reefs on non-volcanic coasts are still open here.
- 2026-10-14: Created from the owner's world-finishing epic (2026-10-14).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
