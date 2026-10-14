---
id: PW-044
title: Seasonal winds (July / January) as a viewer toggle
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-045]
refs: [planet/climate.py, planet/store.py, planet/timeline.py, viewer/index.html, docs/proposals/rounds_1_2_plan.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The wind overlay shows the annual-mean surface wind, which hides the monsoon reversals the owner expected
to see. The climate already computes `wind_jul` and `wind_jan`; store them per frame (int8, like
`wind_e`/`wind_n`) and in worlds, and add a season toggle to the overlay. From plan item 5 ("possibly
also"), never done.

## Updates
- 2026-10-14: Status in-progress -> done. Worlds now store wind_jul_e/n and wind_jan_e/n (world.finish; store specs added, int8 like wind_e). The viewer's Winds overlay has a season picker (year / July / January; URL ?season=jul|jan) shown only when the world has the layers; the legend names the season; runs fall back to the yearly mean. Checked with headless-Chrome screenshots of world 63f57e (01b0f7 @ 384 Myr, sliced for this) in July and January, and run 01b0f7. Run keyframes don't get the seasonal winds yet: that needs the simulation snapshot, filed as an inbox draft (draft-seasonal-winds-in-run-frames).
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Migrated from plan_next@bdc967f item 5 (winds), the optional seasonal toggle that wasn't built.
