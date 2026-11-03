# Den peoples keep their raiding share between ladder refreshes (PW-1407, round 1)

Lane 149, 2026-11-03. Baseline = main 3cf50fdd; after = this branch (main plus the one change). The same 6 runs of
`tools/peoples_robust.py` as `docs/review/peoples/forager-trade/round1.md` (D&D preset, family base, arm now, seeds 7/10/13, worlds
4360a3 and af2677, one try each, end of the history ~1500 AD). Tables from `compare.py` here (`compare_output.md`).

## In plain words

- **What was wrong.** Goblins, kobolds and troglodytes get part of their food from raiding farmers nearby. The ladder worked out how
  many farmers are near only at its full refreshes (every 500 years). If such a people learned something in between (a herd animal,
  say), its line was redone without that map, so its raiding food dropped to nothing until the next full refresh.
- **The fix.** The ladder keeps the last farmers-near map between the full refreshes, as lane 146 already did for the foragers' trade.
  (`Ladder._sn`, next to `_fn`.)
- **What it does.** Almost nothing at the end of the history: against the same 6 runs on main, goblin and kobold people differ by
  under 0.001% (a few people in millions), their ranges are the same to the last digit shown, people on the raider rung the same, the
  total number of people differs by under 0.000003%, and the largest people and its share are unchanged in every run. The
  suite's checks hold on the branch as on main: 0 failing, 0 crashes, 0 peoples extinct, none over 85%. Troglodytes are dead in all 6 runs on
  main and on the branch (nothing to compare).
- **Why so little.** A den people's tech seldom moves between two full refreshes, and the history ends on a full refresh, so the end
  state shows only the trace of the dips that happened on the way. The fix matters for what a people looks like in between
  (the raid share no longer drops out), not for the final numbers. The golden test needed no update.

## Measured

Goblin and kobold, main -> branch, summed over the 6 runs (full per-run table in `compare_output.md`):

| people | people | range Mkm2 | people on the raider rung |
|---|---|---|---|
| goblin | 1.523e7 -> 1.523e7 (-0.0%) | 35.9 -> 35.9 | 7.602e6 -> 7.602e6 (-0.0%) |
| kobold | 1.098e7 -> 1.098e7 (-0.0%) | 76.9 -> 76.9 | 1.493e6 -> 1.493e6 (-0.0%) |
| troglodyte | dead in every run | | |

Largest single-run change in a den people: goblin on 4360a3 seed 7, 2,991,685 -> 2,991,665 people (-0.0007%); all people 1.0746e9 ->
1.0746e9 (+0.000005%). Top people's share per run (main = branch): 24.4, 26.5, 41.7, 20.5, 27.7, 22.9%.

**Invariants** (`peoples_robust.py report`): main 6 runs, branch 6 runs, each 0 failing, 0 crashes, 0 peoples extinct, 0 over 85%
(`fire_giant` is lost in dnd-s7@af2677 on both). Not isolated: one try per run; at differences this small the history is the same
history, so the numbers are the change itself.

## Test

`tests/test_lineages.py::test_den_people_keeps_its_raid_share_between_refreshes`: with farmers present, a full refresh gives the den
line a raid share; its tech then changes between full refreshes (not due), and the line is redone with the kept map: raid share
unchanged, density equal to `line(..., settled_near=kept map)` and different from before. It fails with the old behaviour (checked by
making the map empty).
