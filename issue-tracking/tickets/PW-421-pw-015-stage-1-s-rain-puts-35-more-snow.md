---
id: PW-421
title: "PW-015 stage 1's rain puts ~35% more snow on generated sheets: the run's ice rule doubles them and the time zoom's start drift triples"
type: task
status: done
parent: null
milestone: null
subsystem: climate
effort: m
impact: high
found_by: pw418
blocked_by: [PW-366]
relates: [PW-418, PW-366, PW-015, PW-241, PW-295]
refs: [planet/climate.py, planet/tectonics/earth.py, tests/test_timezoom_consistency.py, "run:2c2810@536Myr", "commit 1416523"]
created: 2026-10-16
updated: 2026-10-23
---

## Description
Bisect for PW-418 (time zoom's sea level runs away on main): the jump is commit 1416523 (PW-015 stage 1,
rain kernel in physical time) alone; no time-zoom commit since 1f0fae4 moves it much. Repro: `TZ.simulate`
20 kyr, default params, from a fixed source (scratch script pw418/repro.py; reproduces in 5-30 s):

| source | 1f0fae4 | 415c60b (shelves, just before) | 1416523 | main |
|---|---|---|---|---|
| L7 run 2c2810 @ 536, 20 kyr | -108 m | -92 m | -199 m | -199 m |
| L6 seed 2 600 Myr (= the ticket's 6d67bd, rebuilt as e438c3) @ 580, 20 kyr | -91 m | -115 m | -314 m | -314 m |
| same, 50 kyr | -130 m | | | -487 m |

(2c8092b, PW-294, gave -235 m at 20 kyr for a while; the polar bundle baabbba brought it back to -130.)

Mechanism: the new kernel snows ~35% more on the generated planets' ice (L6 e438c3 @ 580, the start's
precip on its ice: median 118 -> 156 mm/yr, accumulation 8,000 -> 11,100 Gt/yr; at every height band +30-40%).
On Earth the same change adds only 5-9% on the ice sheets (Antarctica 168 -> 183 mm/yr, Greenland 306 -> 328,
obs 336) but 15% on all land (920 -> 1056 mm/yr against 791 observed). Two effects then add up:
- the run's ice rule (`earth.ice_sheets`) makes much bigger sheets at the same climate: on e438c3's terrain at
  its own dT (-2 C), from no ice, 6 updates (scratch pw418/consist.py): 3.0% of the surface / 7 Mkm3 before,
  7.1% / 48 Mkm3 after;
- the time zoom's start surplus is bigger. Same probe, no forcing (no orbit, CO2, ice albedo), 20 kyr:
  -60 m before, -278 m after. The run's own budget for its sheets is gain 6,900 / melt 3,400 / calving 1,700
  Gt/yr; the time zoom on the same sheets: 6,850 / 1,320 / 310. The snow agrees; the melt and calving don't:
  the run counts every ablation-zone cell melting at full rate, but its thin (50 kPa, PW-366) sheets can't
  feed them, so the time zoom's sheets thicken (+890 m median in 20 kyr) and spread (~14 rings).
Not every moment gets worse: L5 seed 2 @ 300 Myr, 4 C colder, the same probe gives -103 m before and -58 m
after (tests/test_timezoom_consistency.py, xfail on PW-366). Ice speeds aren't the cause: under grounded
sheets (>100 m) the medians are 9-26 m/yr before and after (p99 0.5-2 km/yr); they grow with the ice.

Options:
- A. Fix PW-366 (the run's sheet profile, run lane) and re-measure; the time zoom then starts nearer its balance
  whatever the rain. Lean: A first, it's the cause the drift has had all along (PW-241, PW-295).
- B. Also check whether stage 1's extra land rain (+15% on Earth, already above observed) is right on cold
  generated planets' polar coasts; if it's too wet, fix it in the kernel (simulate outputs, goldens).
- C. Leave the rain; accept bigger sheets in cold eras (they are the run's own ice rule's answer).
- [ ] decide A/B/C; after A, `tests/test_timezoom_consistency.py::test_unforced_start_stays_near_balance` should pass
  (then drop its xfail) and the 20 kyr repro from 2c2810 / e438c3 should stay within ~-60 m

## Updates
- 2026-10-23: Status blocked -> done. Closed (PW-597 triage, 2026-10-23): the condition was met. Option A was taken and PW-366 is done (7fbf3b6, 2026-10-19): on the same probe (L6 seed 2 @ 580, unforced, 20 kyr) the drift went from -231 m (old run, old code; -314 m in this ticket's table) to +7 m (+13 m at 50 kyr), L5 seed 1 -43 -> -2 m, and the strict xfail in tests/test_timezoom_consistency.py was removed. The time zoom's start now sits near its balance whatever the rain, and Earth's sheets get only +5-9% snow from stage 1, so option B (bend the rain) is not pursued; the deeper cold eras that PW-366 brought are tracked in PW-434.
- 2026-10-16: Status needs-decision -> blocked. Coordinator's decision (the owner delegates physics calls): option A. Fix PW-366 first; Earth's sheets get only +5-9% snow from the new rain, close to observed, so the rain isn't the thing to bend. Re-measure after PW-366, then close or reopen B.
- 2026-10-16: Created from inbox draft draft-rain-stage1-snowier-sheets-time-zoom-drift.md (found by pw418).
