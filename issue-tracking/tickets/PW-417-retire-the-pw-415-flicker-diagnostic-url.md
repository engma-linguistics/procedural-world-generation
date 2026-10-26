---
id: PW-417
title: Retire the PW-415 flicker diagnostic URL switches once the owner's Chrome test is in
type: task
status: wontdo
parent: PW-649
milestone: later
subsystem: viewer
effort: xs
impact: low
found_by: pw415
blocked_by: []
relates: [PW-408]
refs: [viewer/index.html]
created: 2026-10-16
updated: 2026-10-26
---

## Description
PW-415 added URL switches to viewer/index.html (`DIAG`: logdepth, noaa, pdb, dpr, nodamp, fixclip,
offset, always, blur, rehover, dbg) so the owner could bisect the Chrome-only river flicker. When his
test is in, make whatever fixed it the default (if it isn't one already), and remove the other switches
and the code paths behind them. Keep `?dbg=1` (the readout and the per-second counters cost nothing
when off) unless it's in the way.
- [ ] the winning setting is the default; the other switches are removed; tests/test_viewer.py passes

## Updates
- 2026-10-26: Status todo -> wontdo. Wontdo: tiny and old. (PW-900 backlog reorg).
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-23: PW-597 triage (2026-10-23): left open. The condition is met (PW-415 done; owner confirmed the Chrome flicker resolved), but the `DIAG` URL switches (logdepth, noaa, pdb, dpr, nodamp, fixclip, blur, rehover, ...) are still in viewer/index.html, so the clean-up this ticket asks for is still to do.
- 2026-10-16: Stays todo, low, small (owner confirmed PW-415 resolved; unblocked).
- 2026-10-16: Created from inbox draft draft-pw415-retire-flicker-switches.md (found by pw415).
