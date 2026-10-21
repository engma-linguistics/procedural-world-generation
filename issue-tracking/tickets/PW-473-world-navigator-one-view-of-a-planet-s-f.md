---
id: PW-473
title: "World navigator: one view of a planet's family, from the tectonic run through time zooms and finished worlds to regional and fine zooms"
type: story
status: todo
parent: PW-244
subsystem: viewer
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-248]
refs: [planet/viewer/index.html, planet/viewer/zoom.html, planet/store.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
Owner 2026-10-20: a better way to see a world from tectonic to time-zoomed to finished, and the other zooms around it.
- A persistent breadcrumb or tree panel showing the provenance chain: run (Myr timeline) -> world slice or time zoom (kyr timeline) -> finished world -> regional zooms -> fine zooms. Each node has a thumbnail; clicking jumps there.
- On the globe, outlines of existing zooms, clickable. On a timeline, markers for the moments that have worlds or time zooms.
- 'Make from here' actions at each level: time zoom from this moment, finish this kyr, zoom this region. These reuse the existing POST /api/zoom, /api/timezoom and /api/finish.
- Builds on store provenance (planet/provenance.py, store.py). Read what links already exist and add any missing parent ids as needed.

## Updates
- 2026-10-20: Created.
