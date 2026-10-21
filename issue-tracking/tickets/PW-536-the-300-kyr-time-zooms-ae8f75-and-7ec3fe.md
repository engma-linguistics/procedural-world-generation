---
id: PW-536
title: The 300 kyr time zooms ae8f75 and 7ec3fe show no sea-level swing with the ice index
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: timezoom
effort: m
impact: med
found_by: worktree-agent-a7b485e309b6e3a74 (PW-493 now-pick check)
blocked_by: []
relates: [PW-493, PW-030, PW-366]
refs: [planet/finish.py, "time zoom ae8f75", "time zoom 7ec3fe", "time zoom e9d59c"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Checking `finish.now_kyr` on the existing time zooms (PW-493): on the 600 kyr zoom e9d59c the
sea level follows the glacial index (interglacial pick 512 kyr, I 0.00, -17 m; glacial pick 594
kyr, I 0.89, -115 m; zoom range -115..+5 m). On the two 300 kyr zooms ae8f75 and 7ec3fe (same
seed 941637, from L6 run bf5ee9 and run 8ddaa4 at 864 Myr; their frame stats are identical) the
sea level does not follow the ice at all: the index goes 0 to 0.95 and back, but sea level stays
between 0 and +33 m, correlation(sea level, I) = 0.01. The glacial pick (266 kyr, I 0.76) is only
0.5 m below the interglacial pick (300 kyr, +19.4 m), so "glacial" is not a low sea level here.
The pick rules are correct on their own terms (the index lands where it should); the zoom has
no sea-level response to its ice.

What to check: why the sea level in a 300 kyr zoom from 864 Myr shows no drawdown (ice volume
vs sea-level bookkeeping, the sea level reference, or the ice being on land that doesn't change
the sea), and whether the 600 kyr zoom e9d59c shows the same response by construction. Compare
the ice volume per frame against sea_level_change_m for both zooms.

- [ ] Explain the zero correlation on ae8f75 (the ice volume and sea-level series per frame).
- [ ] Either a fix (folded into the owning ticket, PW-030/PW-366 area) or a documented reason.
- [ ] After a fix, `planet finish <tz> --now glacial` picks a lower sea level than the interglacial pick.

## Updates
- 2026-10-21: Created from inbox draft draft-timezoom-sealevel-decoupled-300kyr.md (found by worktree-agent-a7b485e309b6e3a74 (PW-493 now-pick check)).
