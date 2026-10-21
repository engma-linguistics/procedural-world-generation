---
id: PW-498
title: Time zooms made before glacial carving can't be finished; re-run the showcase ones
type: task
status: todo
parent: null
milestone: null
subsystem: timezoom
effort: s
impact: med
found_by: pw037-port
blocked_by: []
relates: [PW-037, PW-091, PW-479]
refs: [planet/finish.py, "run 6d0ed0", "run 098d5d", "run 080df3", "run 86c513", "run 755514", "run 7d5027", "run 98ee98", "run be3362"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
After PW-037, `planet finish <timezoom>` needs the per-frame `glacial_erosion` / `glacial_till` layers;
time zooms made before it stop with "made before glacial carving (PW-037); run it again" (no backward
compatibility, per CLAUDE.md). On the main data root (2026-10-20) that is every time zoom there:
6d0ed0 (PW-471's Earth showcase), 098d5d, 080df3, 86c513, 755514, 7d5027, 98ee98, be3362.
Re-run the ones worth keeping from their run.txt remake lines (~6 min per Myr at L6, 30-40 at L7), finish
their showcase worlds again, and delete the rest (`planet delete`). PW-037's own Earth showcase replaces
6d0ed0. Check the one-command flow (make.py, PW-479) doesn't pick an old zoom.
- [ ] showcase time zooms re-run with carving; finished worlds remade; old zooms deleted

## Updates
- 2026-10-21: Created from inbox draft draft-rerun-time-zooms-for-carving.md (found by pw037-port).
