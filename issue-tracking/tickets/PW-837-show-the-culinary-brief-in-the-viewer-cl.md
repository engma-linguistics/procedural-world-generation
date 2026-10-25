---
id: PW-837
title: "Show the culinary brief in the viewer: click a people (or a spot) to read its brief"
type: task
status: done
parent: PW-692
milestone: v2
subsystem: viewer
effort: m
impact: high
found_by: owner-2026-10-24
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-10-25
---

## Description
Owner asked how to find and read the briefs; today they exist only via 'planet brief <run> --people ID' or '--all --out DIR'. A viewer panel (people list in the Peoples panel, and a 'brief here' click on the globe for --region) would make them discoverable.

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 25.
- 2026-10-24: Created.
- 2026-10-25: Fun lane 25: GET /api/brief?run=&people=&era= (or &region=lat,lon,km) builds the brief (server.brief, ~3 s) and the Peoples panel shows a 'Culinary brief...' button when one people is selected: a dialog with the Markdown text, Copy text and Download JSON. Checked on run bbfba8 (orcs). Left: a 'brief here' for a picked cell (the endpoint takes region= already), an era choice (present only), and a brief list of every people.
