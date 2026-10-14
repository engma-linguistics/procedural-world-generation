---
id: PW-027
title: "Arctic coasts: sea-ice damping of waves and tides"
type: task
status: done
parent: null
subsystem: coast
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-028]
refs: [planet/coast.py, "zoom f81832", "world 0f7abd", tools/coast_check.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Arctic coasts should get much lower wave power (sea ice covers them most of the year) and so lean
river-dominated deltas. Tides on Arctic shelves are also too big (no sea-ice damping). Scale wave power
(and tidal range) by the ice-free season from the world's temperature/sea-ice. Reference: zoom f81832 on
world 0f7abd, a Lena-like river (2.2 Mkm² basin, −12 °C mean, 16,800 m³/s) that comes out
wave-dominated.

## Updates
- 2026-10-14: Status in-progress -> done. coast.sea_ice_share: each half-year's frozen share per sea cell from a sine between the coldest and warmest months crossing FREEZE. Waves: rays stop at mostly-frozen (>= 0.5) sea as before, and the power arriving in a half-year is now scaled by the cell's open-water share (an Arctic coast open ~3 months gets waves only then). Tides: tide_range takes ice_share (annual); sea ice adds shelf friction (ICE_FRIC = 1: R_FRIC and the shelf decay scale with 1 + ice share). world.finish and coast_check pass it. coast_check gained Arctic sites: tides Tiksi 3.33 -> 1.15 m, Kolyma 3.44 -> 1.43, Mackenzie 4.10 -> 3.10 (obs 0.1-0.6, still high: inbox draft draft-arctic-tides-basin-connection), Cook Inlet 7.67 -> 6.96 (in range); other sites unchanged. Deltas: Mackenzie mixed -> river-dominated (its usual type), Lena river-dominated 0.75 -> 0.96. The reference zoom f81832 is NOT an Arctic coast: its mouth (51.6 N on world 0f7abd) is an ice-free sea (cold month +2..3.5 C), so this leaves it wave-dominated; noted on PW-028 (spring flood). Tests: test_coast.test_sea_ice_share; goldens unchanged.
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Created from the owner discussion 2026-10-14. Merged the Arctic part of Known issue 'Tides: Arctic shelves too big' (deltas).
