---
id: PW-1022
title: "Technology map: events older than a run's first stored moment are drawn on that moment's ranges"
type: task
status: todo
parent: PW-913
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: fun-lane-47
blocked_by: []
relates: [PW-913]
refs: [viewer/index.html, "run 3097e3"]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words: the map view of the Technology tab (the globe's "technology" layer) can only show where peoples lived at the moments the run stored. Run 3097e3 stores 153 moments from 20.3 Myr ago to the present, so this rarely matters there, but a peoples run whose stored moments start later than its oldest techs (language, fire) has no range to draw those first inventions and hand-overs on. The globe then draws such a star or arrow at the people's centre in the first stored moment (or, failing that, at its present centre or its origin), and says so in the legend. Clicking such an event in the side list goes to the first stored moment.

What to try: draw old events at the people's `origin_place` when it is older than the first frame, or grey them out with a note "before the stored history"; check on a run whose frames start late (a recent-pass run).
- [ ] an event older than the first stored moment is drawn where the people was, or plainly marked as approximate

## Updates
- 2026-10-29: Created from inbox draft draft-techtab-map-before-first-stored-moment.md (found by fun-lane-47).
