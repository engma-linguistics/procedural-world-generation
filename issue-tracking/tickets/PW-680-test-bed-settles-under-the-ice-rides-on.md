---
id: PW-680
title: "test_bed_settles_under_the_ice rides on one chaotic world (sim4): PW-636's FLORA_PACE 0.8 turns it red at 47.1 m against a 46.2 m tolerance"
type: task
status: done
parent: PW-649
milestone: v1
subsystem: timezoom
effort: s
impact: med
found_by: merge-1024
blocked_by: []
relates: [PW-636, PW-623, PW-638, PW-640, PW-643]
refs: [tests/test_timezoom.py, tests/seeds.py, docs/review/base-climate/merge-1024/]
created: 2026-10-23
updated: 2026-10-29
---

## Description
In merge lane 1024, step 5 merged PW-636 (FLORA_PACE 0.8, branch head adddbae) on top of main + A22/A23 + A20 +
PW-627. Every multi-seed test was green on three draws. One single-world test went red:
`tests/test_timezoom.py::test_bed_settles_under_the_ice`, where the median |bed - want| under grown ice was 47.1 m
against a tolerance of 46.2 m. The test runs on `cold_src` (sim4: L4 seed 1, 300 Myr, made 8 C colder), so any
run-physics change gives it another world. This is the lottery PW-623/638/640 removed from the other time-zoom
tests. Step 5 was not kept (`docs/review/base-climate/merge-1024/README.md`, `step5_not_kept/`), and PW-636 is held
on this decision.

Options:
- A: move the test onto the multi-seed fixtures (seeds.SEEDS4 sources, each made 8 C colder, its assertions
  unchanged, `PASS_RATE_L4` or `PASS_RATE`, an eligibility rule that ice grows > 500 m somewhere). This is a harness
  change in the owner's "assertions unchanged" class, but it changes the bar from "this world" to a rate.
- B: keep the single world and hold PW-636 until a physics change moves sim4 back under the tolerance.
- C: look into whether the 0.9 m miss is real (the lag term `lag` in the tolerance under-counts when the ice grows
  late in the 40 kyr) before choosing.
- Lean: A, after a quick C check, because the margin is 2% and the world is chaotic.
- [x] A / B / C (C: the lag term fixed)

## Updates
- 2026-10-29: Removed docs/review/base-climate/merge-1024/, docs/review/base-climate/thermostat-1024/ in cleanup; last present at 9861e2df.
- 2026-10-23: Thermostat lane 1024, option C: the lag term was the wrong quantity. It counted the sheet's net volume change over the last iso_tau; the bed lags each cell's own load (replayed relaxation matches bed - want to 0.7 m). On PW-636's sim4 the volume is flat but the cells' load moved a median 32 m, so 47.1 m against 46.2. Fixed in the test: the lag is each grown cell's own load change over the last iso_tau (median); 5% dip, 20 m and the other assertions unchanged. Seeds 1-24 x 3 draws, main and PW-636: new 143/144 pass (the miss is the pressed-down assertion), old 139/144; both isostasy breaks caught on 23-24 of 24. Also found: sim4's world depends on the per-checkout mantle basis cache (draft-mantle-basis-cache-picks-the-world). docs/review/base-climate/thermostat-1024/.
- 2026-10-23: Created from inbox draft draft-bed-settles-single-world.md (found by merge-1024).
