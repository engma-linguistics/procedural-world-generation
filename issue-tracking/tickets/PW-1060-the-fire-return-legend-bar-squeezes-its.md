---
id: PW-1060
title: The fire-return legend bar squeezes its colours into the left edge (stops spaced by value on a log-scale ramp)
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: xs
impact: low
found_by: viewer-lane-53
blocked_by: []
relates: [PW-1027]
refs: [viewer/globe/panel.js, viewer/globe/layers.js, "world 2a7385", docs/review/viewer-ux-sides/img/g-fire_return-cur.jpg]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The colour bar under the fire-return map does not show the map's colours: the reds and oranges for frequent fires are crushed into a sliver at the left end, so the bar looks yellow to grey-blue.

Why: `rampLegend()` in viewer/globe/panel.js places each stop at `(value - lo) / (hi - lo)` along the bar. Fire return's stops are 0, 1, 3, 10, 50, 300, 3000 years (a log scale, with 0 as "never burns"), so everything up to 50 years lands in the first 2% of the bar. Seen on world 2a7385 with layer=fire return.

Fix to try: let a ramp say it is log-scaled (or give rampLegend the stop positions), space the bar by log value, and draw "never" as a separate swatch. Check every ramp for the same problem (any whose stop values span more than ~2 orders of magnitude).
- [ ] the fire-return bar shows the same colours as the map, in order
- [ ] "never burns" shown as its own swatch

## Updates
- 2026-10-30: Created from inbox draft draft-log-scale-legend-bar-crushes-stops.md (found by viewer-lane-53).
