---
title: Culinary brief in the viewer: a "brief here" for a picked cell, an era choice, and a list of every people
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: fun-lane-25
blocked_by: []
relates: [PW-837]
refs: [viewer/index.html, planet/server.py]
---

## Description
PW-837 (lane 25) shows a people's brief at the present from the Peoples panel (GET /api/brief). Still open: a "brief here" button for the picked cell (the endpoint already takes region=lat,lon,km), an era choice (the endpoint takes era= in kyr ago; the viewer sends 0), and a way to read every people's brief without selecting each one. The brief takes about 3 s per call on world 2a7385 (Ctx is rebuilt every request): cache a Ctx per run if several are asked in a row.
