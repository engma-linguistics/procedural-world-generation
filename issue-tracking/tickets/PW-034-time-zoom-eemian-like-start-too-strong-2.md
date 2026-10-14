---
id: PW-034
title: "Time zoom: Eemian-like start too strong (+24 m in 10 kyr)"
type: task
status: done
parent: null
subsystem: timezoom
effort: s
impact: low
found_by: timezoom
blocked_by: []
relates: []
refs: [planet/timezoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Starting from today's Earth the time zoom loses ice worth +24 m of sea level in the first 10 kyr (real
Eemian +6–9 m), and `insol_k` above 0.3 melts most of Antarctica. Damp the start or the insolation
sensitivity.

## Updates
- 2026-10-14: Status todo -> done. Fixed in 8816c11 (climfix): 'eemian' phases now give e~0.042 (127 ka; was 0.052) and absorb_km 1000 -> 600 (the wide mix pulled the open sea's full absorption onto coastal ice). Earth start: +8.5 m peak at 8 kyr, +7.5 m at 10 kyr (was +25.6); 150 kyr low -46 m (was -24). Antarctica/Greenland split still off (inbox draft).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Glacial time zoom.
