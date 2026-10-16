---
id: PW-035
title: "Time zoom: start-anchor cooling persists after the starting ice is gone"
type: task
status: done
parent: null
subsystem: timezoom
effort: m
impact: low
found_by: timezoom
blocked_by: []
relates: []
refs: [planet/timezoom.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
A fixed per-cell cooling keeps the starting ice stable; it persists after that ice has melted, so it's a
calibration crutch. Replace it with something tied to the ice actually present (or fade it out).

## Updates
- 2026-10-16: Status in-progress -> done. Done: start anchor applies only where ice lies; Earth moves < 0.1 m.
- 2026-10-16: Fixed (tzbatch): the anchor is a correction of the ice surface's climate, so climate_step now gets anchor x the cell's ice presence (f_alb, in full from snow_h = 20 m): it leaves with the ice and returns where the ice readvances; ring cells are no longer cooled before ice reaches them. Test test_start_anchor_leaves_with_the_ice (a balance anchor of up to 3 C: cooled cells left bare had 3.2 C of anchor left, now 0). Earth (anchor=obs, Antarctica -2.4 C mean over 1345 cells): the 1 Myr zoom is unchanged to 0.1 m (the anchored cells that lose ice are West Antarctica's marine ones, which turn to sea); runs use anchor=none.
- 2026-10-16: Status todo -> in-progress. Time zoom batch agent started.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Glacial time zoom.
