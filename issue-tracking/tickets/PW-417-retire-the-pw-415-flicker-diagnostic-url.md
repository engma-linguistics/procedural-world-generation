---
id: PW-417
title: Retire the PW-415 flicker diagnostic URL switches once the owner's Chrome test is in
type: task
status: todo
parent: null
subsystem: viewer
effort: xs
impact: low
found_by: pw415
blocked_by: [PW-415]
relates: [PW-408]
refs: [viewer/index.html]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-415 added URL switches to viewer/index.html (`DIAG`: logdepth, noaa, pdb, dpr, nodamp, fixclip,
offset, always, blur, rehover, dbg) so the owner could bisect the Chrome-only river flicker. When his
test is in, make whatever fixed it the default (if it isn't one already), and remove the other switches
and the code paths behind them. Keep `?dbg=1` (the readout and the per-second counters cost nothing
when off) unless it's in the way.
- [ ] the winning setting is the default; the other switches are removed; tests/test_viewer.py passes

## Updates
- 2026-10-16: Created from inbox draft draft-pw415-retire-flicker-switches.md (found by pw415).
