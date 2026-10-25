---
id: PW-886
title: "Rename continents from the viewer: a button or inline edit beside each landmass name, saved through the server (owner won't use the CLI)"
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: med
found_by: owner
blocked_by: []
relates: [PW-867, PW-853]
refs: [viewer/index.html, planet/server.py]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner, 2026-10-25: "let's get a button for that in the viewer ... I won't be using [the CLI]". PW-867 added `planet name <world> A=Jangwa`, which stores names in `worlds/names/<id>.json`. Add a viewer control: click a continent label or its landmass row, type a name, and save it with a POST to the server, which writes the same file. Also allow clearing a name back to the generated one. The CLI can stay as a tool for agents.
- [ ] rename and clear from the viewer, persisted, shown on labels and in later peoples runs

## Updates
- 2026-10-25: Created from inbox draft draft-rename-continents-in-the-viewer.md (found by owner).
