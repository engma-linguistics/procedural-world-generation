---
title: "PW-422 (film-shielded margins): re-measure after PW-366's in-sub-step balance and front-edge balance"
type: task
status: todo
parent: null
subsystem: timezoom
effort: xs
impact: low
found_by: pw366
blocked_by: []
relates: [PW-422, PW-366, PW-115]
refs: [planet/timezoom.py, planet/timezoom_kernels.py]
---

## Description
PW-366 changed what PW-422 describes: the time zoom's balance now acts within `sia_flow`'s sub-steps on the
ice and the 2 rings around it (`rate`, `_balance`), and bare land next to grounded ice takes a new edge's
balance (bright, `edge_h` ~400 m high, as `earth.ablation_zone` tests a new margin) instead of bare ground's.
So a film the flow pushes beyond a front melts (or grows) as that edge would, within the step. Unforced drift
from a run moment is now -2..+13 m in 20-50 kyr (L5 seed 1 @ 300 -4 C; L6 seed 2 @ 580). Not re-run: PW-422's
own counts (thick cells behind films at 0.5 / 10 kyr) and its 2.5 km L4 cold-world test dome (main kept 10.0
Mkm3 in 10 kyr). Probably merge into PW-422 and close it if the dome holds.
- [ ] re-run PW-422's film count and dome test on the merged code
