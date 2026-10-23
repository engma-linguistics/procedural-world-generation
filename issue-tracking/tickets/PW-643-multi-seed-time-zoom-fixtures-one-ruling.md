---
id: PW-643
title: "Multi-seed time-zoom fixtures (one ruling for PW-623, PW-638, PW-640): ready on a branch; main stays green, three deliberate breaks fail clearly; but the forest test stays red on both held branches (12 and 16 of 24), and a 70% bar sits close to main's own pass rate"
type: task
status: done
parent: PW-470
milestone: v1
subsystem: timezoom
effort: s
impact: high
found_by: tests-multiseed
blocked_by: []
relates: [PW-623, PW-638, PW-640, PW-632, PW-592, PW-627]
refs: [tests/seeds.py, tests/conftest.py, tests/test_timezoom.py, tests/test_timezoom_cycle.py, tests/test_timezoom_consistency.py, docs/review/tests/multiseed-fixtures.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Branch `worktree-agent-acfa88d756b0677df` (on main 86d3806) holds the coordinator's proposal from PW-640. It changes
`tests/` only. The details, with every seed's numbers, are in `docs/review/tests/multiseed-fixtures.md`.

**What it does:**
- Each affected test runs its unchanged per-seed assertions on fixed seeds and needs ceil(70%) of the eligible
  seeds to pass:
  - the forest-to-tundra and endings tests on L4 seeds 1-24;
  - the cold-moment tests on L5 seeds 25-50.
- The worlds are built once per session in a process pool and shared by the xdist workers.
- Eligibility:
  - the forest and endings tests: every seed. The endings test's `extra > 10` is an assertion, not a precondition,
    so it is not used to exclude seeds.
  - the cold-moment tests: `_plausible`, unchanged.
- **New and the owner's call:** the speeds and index-zero tests run only on the plausible seeds with sheets. The
  file already says they need sheets. The sheets test asks the window for at least 5 such seeds. At a plain 70%
  bar it would be red on main itself: only 7 of 14 plausible seeds have sheets.

**Measured** (the bar is 17 of 24 for L4):

| tree | forest | endings | cold: sheeted seeds (need 5) | speeds / index 0 |
|---|---|---|---|---|
| main | 20 | 18 | 7 | 7/7, 7/7 |
| main + step 2 (A17's diff) | **16, red** | 21 | 6 | 6/6, 6/6 |
| A20 (shelf air, a1462d3) | **12, red** | 20 | **4, red** | 3/4, 3/4 |

- Suite time: 3:42 -> 4:52 (`pytest -q`, 16 workers). The extra time is the 26 L5 runs.
- The three deliberate breaks fail clearly:
  - no glacial ending: endings 2 of 24;
  - the forest term's sign flipped: forest 4 of 24;
  - no run ice: sheets 0 of 13, drift tests 0 eligible.

**Two things the owner should know:**
1. **Multi-seed does not unblock PW-640's forest test.** A 24-world climate swap shows the zoom climate is not the
   cause: A20's climate on main's worlds gives exactly main's 20 / 18. The cause is that A20's runs give a
   population of worlds where forest loss forces positive (F > 0) on 12 of 24. That would happen by chance 0.7% of
   the time at main's rate. So this is a real population shift for the physics lane, not one world's luck. Step
   2's 16 of 24 is borderline (23% by chance).
2. **70% is close to main's own rate.** Over seeds 1-36, forest passes 75% and endings 69%. A 70% bar on 24 seeds
   would still flip by chance on about half of run-physics changes (endings) or about a quarter (forest). A 50% bar
   (12 of 24) almost never flips by chance (2% / 0%) and still catches the breaks above, which give 2-4 of 24.

**Options:**
- A: adopt as on the branch (70%, N = 24, MIN_SHEETED = 5).
  - main is green;
  - PW-638 (endings) is unblocked;
  - PW-640 and step 2 stay held on the forest test, now as a real multi-world signal;
  - A20 also fails the cold-moment sheets count (4 < 5).
- B: adopt with a different rate or N. Lean within B: 50% on the L4 tests.
  - Then step 2 passes everything.
  - A20 passes the forest test exactly at 12 of 24 and still fails on sheets 4 < 5.
  - MIN_SHEETED is the owner's number too: 4 would pass A20.
- C: keep the single-seed fixtures and hold the physics.
- Lean: **A for the mechanism**, with the B change of the L4 rate to ~50% to make it lottery-proof. In either case,
  treat A20's forest result as a physics question: why do its worlds give F > 0? Do not treat it as fixture
  noise.
- [ ] A / B (rate, N, MIN_SHEETED) / C
- [ ] (if A/B) the index-is-zero invariant at 100% rather than under the rate bar?

## Updates
- 2026-10-23: Status todo -> done. Adopted (merged fdb0d7c): L4 forest/endings at 50%, index-zero on every plausible seed, MIN_SHEETED 5. Breaks fail (2/24, 2/21, 0/13); main green on 3 draws; held branches: A22 and step 2 green on both draws, A20 red on sheets (4 of 8) on one draw.
- 2026-10-23: Rulings applied on branch worktree-agent-ad946bcdcf3b84ccf (d62890d, tests only): the L4 tests at 50% (seeds.PASS_RATE_L4), the L5 drift tests at 70%, MIN_SHEETED 5. Index-zero choice: the index-is-zero assertion at 100% on every plausible seed (the index is the orbit's alone, so one world breaking it is a real break, never a lottery), the sea-level drift at 70% on the sheeted seeds. Main green on 3 draws (climate_offset 0 / +0.001 / -0.001): forest 19/21, 13/18, 14/18 eligible; endings 18, 19, 19 of 24 (bar 12); sheeted 7, 10, 5 (need 5: the -0.001 draw sits on the bar). Held-branch table and the breaks: docs/review/tests/multiseed-fixtures.md (handoff-rulings.md while the lane was paused).
- 2026-10-23: Status needs-decision -> todo. Owner 2026-10-24: adopt A with B's change: the L4 multi-seed tests at ~50% (lottery-proof against main's measured ~70% rates); MIN_SHEETED as proposed. A20's forest result as a physics question: answered by lane A21 (PW-640: lottery, same mean F over 240 worlds).
- 2026-10-23: Lane A21: main's true pass rates are ~72% (forest) and ~69% (endings), so a 70% bar on 24 seeds is itself a lottery (main red in 3 of 4 re-rolled draws). Bars must sit well below the measured rate (~50%), or use more seeds, or rule-based eligibility (PW-644).
- 2026-10-23: Created from inbox draft draft-multiseed-fixtures.md (found by tests-multiseed).
