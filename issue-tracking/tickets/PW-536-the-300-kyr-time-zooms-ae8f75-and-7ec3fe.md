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
- 2026-10-21: Diagnosed (worktree-agent-a1bb68a84d5003e9b); no bookkeeping or wiring bug, so no code change. Documented reason, draft filed under PW-470 (`draft-glacial-cooling-share-excludes-iced-land.md`).
  - Bookkeeping is right: on ae8f75 corr(sea level, ice_sea_equiv) is -1.00 by construction (`sl = -(above_flotation - Vaf0) / ocean_area`, 11.2 Mkm3 of sea-water equivalent = +33 m over a 340 Mkm2 ocean), and the reference is the zoom's own start (sea_level_change_m 0 at t=0), the same for the Earth zoom.
  - The ice volume does not follow the index: corr(ice volume, I) = -0.01 on ae8f75 (19.6..32.0 Mkm3), against +0.62 on Earth's e9d59c (26..77 Mkm3). The cause is the forcing, not the sea level: the glacial cooling is `glacial_cool x share / glacial_f`, and the share (ice-free land poleward of the snowline) is 0.26% of this planet against 3.49% on Earth. So the cooling is 0.49 C (Earth 6.49 C), dT_global at I = 0.94 is only -0.26 C (Earth -5.9 C) and the sea-level target is -7.1 m (Earth -87 m). The cycling latitude is 64.3 S and the index itself is healthy (3 endings, cycles 127 and 94.5 kyr).
  - That swing is far below the start drift: the run moment's ice (5.2% of the surface, 32 Mkm3) is not the zoom's balance, so it melts to 20-25 Mkm3 in the first 12 kyr (+18..+33 m), then wobbles +-4 Mkm3 (+-7 m) on the orbit alone (PW-436).
  - Check that the wiring works once the forcing is there: a diagnostic zoom of the same moment with `--set glacial_dt=5` (scratch store, id f0f487, not a fix) has corr(sea level, I) = -0.48, sea level -28..+28 m, and the glacial pick is only +1 m against -8 m for the interglacial pick: better, still weak, because the start drift (PW-436) and the weak sheet response (PW-435) remain.
  - Earth's e9d59c is unchanged (nothing in the code was touched): cycles 98-109 kyr, maxima -86..-104 m, sea level -115..+5 m.
  - Whether the cooling should count the land that already holds ice, or ignore the share on a planet this warm (+2.1 C, run sea level -291 m), is a calibration of the ice model: parked with PW-470.
