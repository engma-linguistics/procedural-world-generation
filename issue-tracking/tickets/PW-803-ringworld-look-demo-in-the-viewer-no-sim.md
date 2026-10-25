---
id: PW-803
title: "Ringworld look demo in the viewer: no sims, just see one"
type: task
status: in-progress
parent: PW-802
milestone: later
subsystem: viewer
effort: s
impact: low
found_by: owner-2026-10-24
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-10-24
---

## Description
Owner: 'Let a subagent take our visualizer for how a world works and just demo a ringworld. Nothing fancy, no actual sims. I just wanna see it.' A standalone viewer page (three.js, reusing the viewer's style and palette) showing a ringworld: a ribbon around a star, inner surface with land/sea/biome-like colours from noise, rim walls, shadow squares, orbit controls.

## Updates
- 2026-10-24: Created.
- 2026-10-24: Built viewer/ringworld.html + ringworld.js (open at /viewer/ringworld.html on `planet serve`, ?cam=over|edge|surf); screenshots in docs/review/viewer/ringworld/. Crude: noise land, one hull colour, no link from the main viewer, flat unlit shading.
