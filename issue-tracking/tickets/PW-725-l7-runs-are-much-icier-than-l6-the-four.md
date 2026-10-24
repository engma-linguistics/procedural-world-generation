---
id: PW-725
title: "L7 runs are much icier than L6: the four L7 showcase runs spend 63-79% of 300-1000 Myr in an icehouse, L6 a median 33% (24/32 seed-draws within the owner's 40%)"
type: task
status: done
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: v1-finish-2
blocked_by: []
relates: [PW-708, PW-559, PW-202]
refs: [planet/tectonics/earth.py, planet/climate.py, docs/review/base-climate/v1-finish-2/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
Lane v1-finish-2 measured the 1 Gyr pass rate on the owner's bar at L6 (ice_diag, 16 seeds x 2 draws, judged on
300-1000 Myr): 24/32 (75%), icehouse median 33%. The four random-seed L7 showcase runs made right after on the same
code (`planet make --level 7`, runs 89c2ab, 6ca373, 8b1617, 7f4f06; seeds 733847, 819014, 53669, 958504) spend
70%, 79%, 63% and 67% of 300-1000 Myr in an icehouse (ice >= 20 m of sea level), with ice down to -369..-476 m.
All four fail the bar. The previous L7 batch (a6643c, 3a0480, 0d1889, 89bea8, before PW-559 B) also ended in deep
ice (-500 m at 1000 Myr on 89bea8). Under the L6 distribution (4 of 32 draws above 60%) four in a row is ~2e-4, so
it is a level effect, not the draw.

The CO2 references are planet-relative (frozen at 300 Myr), so the sink's scale shouldn't depend on the level;
suspects are the resolution-dependent parts: higher resolved peaks and plateaus (more ice nucleation, snowline
land), the ice-albedo term on a finer ice mask, the erosion supply's growth with resolved relief (PW-708's
mechanism, larger at L7), and the ice sheets' flow and budget per cell size.

To do: an ice_diag split at L7 on ~4 seeds (L7 1 Gyr ~40 min at 5 threads, with load ~80 min) against the same
seeds at L6: dT parts (drift, CO2 term, albedo), the CO2 source/sink parts (`docs/review/base-climate/v1-finish-2/
relief.py`, `trend.py`), iced land and snowline land per level. Fix the root cause if it's resolution-dependent
physics; the showcase (PW-202) is L7, so v1's look depends on it. The L7 showcase's present worlds are
interglacials within their icehouse (PW-700), so they look fine; their histories are icier than the bar.

## Updates
- 2026-10-24: Created from inbox draft draft-l7-runs-icier-than-l6.md (found by v1-finish-2).
- 2026-10-24: Done (v1-finish-3, be6f208). Cause: the run's margin band (melting as the sheet's outermost 10 km) was one ring of cells, ~120 km at L6, ~60 km at L7; same planet at the same dT grew ~2x iced land, ~3.5x ice at L7. Fix: earth.margin_band, MARGIN_KM 120 (L6 bit-identical, two rings at L7); levels within ~20% over dT -3..+2. L7 1 Gyr: 5/8 seed-draws on the bar, icehouse median 33% (= L6), from 0/4 at 68%. Showcase remake started (seeds 957317, 619496, 583167, 639472; ids to record on PW-202). docs/review/base-climate/v1-finish-3/.
