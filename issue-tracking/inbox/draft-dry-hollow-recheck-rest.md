---
title: The dry-hollow recheck still costs ~0.1 s per lakes() call after the flood reuse (needs an incremental flood or a speculative recheck)
type: task
status: todo
parent: null
milestone: later
subsystem: hydrology
effort: l
impact: low
found_by: lane257
blocked_by: []
relates: [PW-1606, PW-054]
refs: ["planet/hydrology.py::_settle", "planet/hydrology.py::route", "planet/hydrology.py::_same_flood", "planet/kernels.py::priority_flood_to", "planet/kernels.py::lakes_on", docs/review/basins/scout251/prof.py, docs/review/basins/scout251/bench.py, "L7 seed 11 at 200 Myr (run a19366's 000200.0.ckpt)"]
---

## Description
In plain words: PW-1606 (lane 257) took the dry-hollow recheck's extra cost per `lakes()` call from about +0.27 s
to about +0.17 s (19 of the 24 river floods per call now run, five reuse an earlier one bit for bit), but not to
the +0.10 s that the ticket's 0.35 s goal needs. Each L7 run is still about 5% slower than before PW-054 pass 3
(30 Myr: 37.5 s before the rule, 42.0 s on main, 39.9 s now; same machine, back to back, load ~20).

What is left, measured on the profile state (3 `_settle` calls per `lakes()`: 12 + 8 + 4 floods, against 4 + 2 + 2
with the rule off): every dropped kept hollow restarts the whole tries loop (4 floods, 4 `lakes_on`) on a bed that
differs in 1-15 cells. Why it is hard to cut exactly:
- the floods differ in the lakes' outlet cells (a dropped hollow stops being a sink), and the first changed cell is
  low in the queue (the divergence point is at 0-30% of the 52k pops, mostly under 5%), so resuming a flood from
  the old one's prefix saves almost nothing;
- a warm start of the `extra` water from the previous round is not the same iteration (different fixed point
  possible), so outputs would change;
- heap layout is not the cost (a 4-ary heap ties the binary one; 6 ms per flood for 52k pops).
Options: (a) a speculative recheck: start round r+1 in a second thread (kernels with nogil) from the drop set seen
after round r's first try, keep it only if the final drop set agrees; exact, but doubles CPU in the worst case;
(b) accept it, since the result is exact; (c) change the rule so the drop is judged once on the first carve try
(output changes, goldens regenerate; a physics call).
If never done: nothing is wrong, L7 runs stay about 5% (2-3 min per Gyr) slower than before PW-054 pass 3.
- [ ] `lakes()` on the profile state <= 0.35 s with identical outputs
