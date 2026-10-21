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
- 2026-10-20: Built on branch worktree-agent-a37d9b944587e6d92 (not merged): viewer/navigator.js: a bar with the provenance chain (thumbnails, click to jump; ancestors open at the child's moment) over the globe and the Regional zoom tab, a Family tree drop-down, "make from here" (time zoom, finish, highlights) on /api/timezoom and /api/finish, zoom outlines on the globe with a clickable edge. The store already recorded every parent link (source_run, timezoom, world, parent_zoom); no new fields. The slider's existing ticks stay as the timeline markers. Gaps: draft-navigator-from-here-gaps.
- 2026-10-20: Created.
