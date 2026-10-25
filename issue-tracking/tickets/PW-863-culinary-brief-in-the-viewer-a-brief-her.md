---
id: PW-863
title: "Culinary brief in the viewer: a 'brief here' for a picked cell, an era choice, and a list of every people"
type: task
status: done
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: fun-lane-25
blocked_by: []
relates: [PW-837]
refs: [viewer/index.html, planet/server.py]
created: 2026-10-25
updated: 2026-10-25
---

## Description
PW-837 (lane 25) shows a people's brief at the present from the Peoples panel (GET /api/brief). Still open: a "brief here" button for the picked cell (the endpoint already takes region=lat,lon,km), an era choice (the endpoint takes era= in kyr ago; the viewer sends 0), and a way to read every people's brief without selecting each one. The brief takes about 3 s per call on world 2a7385 (Ctx is rebuilt every request): cache a Ctx per run if several are asked in a row.

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 28.
- 2026-10-25: Created from inbox draft draft-brief-here-and-era-in-viewer.md (found by fun-lane-25).
- 2026-10-25: fun-lane-28: viewer done. The brief window now has a people list (every people of the run, switching re-asks), an era box (kyr ago) with Show, and Brief here (the picked cell, region=lat,lon, all peoples there; a toast asks for a pick first); the Peoples panel's Culinary brief button shows always (the selected people, else human). Checked with headless Chrome on port 8793 on run 62341d (50 peoples listed, orcs at 20 kyr ago, brief around a clicked cell). Not done: a per-run Ctx cache (the 3 s per call remains, see the ticket). Status left.
