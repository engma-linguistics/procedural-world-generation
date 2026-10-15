---
id: PW-031
title: "Time zoom: generated worlds glaciate too hard"
type: task
status: done
parent: null
subsystem: timezoom
effort: m
impact: high
found_by: timezoom
blocked_by: []
relates: [PW-032]
refs: [planet/timezoom.py, docs/proposals/glacial_timezoom.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
At dT 0, generated worlds reach about −400 m sea level, roughly 3× Earth's last glacial maximum; the
global temperature hits the floor set by the CO₂ and albedo feedback caps. Time zooms started from the
viewer button run away too (one reached −520 m with ice 7.4 km thick). Calibrate the feedback caps /
accumulation so a generated Earth-like world peaks near −100 to −150 m.

## Updates
- 2026-10-14: Status in-progress -> done. Merged (finish): sea level counts only the ocean water the ice displaces; run moment treated as the cycle average (half caps). bcc894 -171 -> -132 m; Earth-like moment -95 m; Earth -53 m. Cold-era 8e71fd still -258 m: cause is the run's ice rule, moved to PW-190 (decision C).
- 2026-10-14: Status todo -> in-progress. Agent started in worktree finish, bundled with PW-091.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Glacial time zoom. Merged 'Time zooms made from the button run away too' (viewer2).
